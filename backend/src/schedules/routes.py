from datetime import datetime

import pytz
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.k8s.services import K8sClient, get_k8s_client
from src.shared.auth.auth_simple import get_current_user
from src.shared.database import ScheduleDB, get_db
from src.shared.settings import settings

from .models import Schedule, ScheduleCreate, ScheduleUpdate

scheduler_router = APIRouter(prefix="/schedules", tags=["schedules"])


def is_in_hibernation_period(scale_down_time: str, scale_up_time: str, current_time: str) -> bool:
    """
    Check if current time is within the hibernation period (between scale_down and scale_up).
    Handles both same-day and overnight periods.

    Examples:
    - scale_down=22:00, scale_up=08:00, current=23:00 → True (overnight period)
    - scale_down=22:00, scale_up=08:00, current=07:00 → True (overnight period)
    - scale_down=22:00, scale_up=08:00, current=10:00 → False
    - scale_down=13:00, scale_up=14:00, current=13:30 → True (same-day period)
    """
    if scale_down_time < scale_up_time:
        # Same-day period (e.g., 13:00 to 14:00)
        return scale_down_time <= current_time < scale_up_time
    else:
        # Overnight period (e.g., 22:00 to 08:00)
        return current_time >= scale_down_time or current_time < scale_up_time


@scheduler_router.get("", response_model=list[Schedule])
async def get_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ScheduleDB:
    """Get all schedules"""
    result = await db.execute(
        select(ScheduleDB).order_by(ScheduleDB.created_at.desc()),
    )
    schedules = result.scalars().all()
    return schedules


@scheduler_router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ScheduleDB:
    """Get a specific schedule"""
    result = await db.execute(
        select(ScheduleDB).where(ScheduleDB.id == schedule_id),
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule


@scheduler_router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    k8s: K8sClient = Depends(get_k8s_client),
) -> ScheduleDB:
    """Create a new schedule"""
    # Check if namespace is allowed (has required label)
    is_allowed = await run_in_threadpool(
        k8s.is_namespace_allowed,
        schedule_data.namespace,
        settings.NAMESPACE_LABEL_KEY,
        settings.NAMESPACE_LABEL_VALUE,
    )

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Namespace '{schedule_data.namespace}' is not allowed. "
            f"Add label {settings.NAMESPACE_LABEL_KEY}={settings.NAMESPACE_LABEL_VALUE} to enable scheduling.",
        )

    # Verify deployment exists and get current replicas
    try:
        current_replicas = await run_in_threadpool(
            k8s.get_deployment_replicas,
            schedule_data.namespace,
            schedule_data.deployment_name,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Deployment not found: {str(e)}")

    # Check if schedule already exists for this deployment
    result = await db.execute(
        select(ScheduleDB).where(
            ScheduleDB.namespace == schedule_data.namespace,
            ScheduleDB.deployment_name == schedule_data.deployment_name,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "A schedule already exists for this deployment",
                "suggestion": "Please edit the existing schedule instead of creating a new one",
                "existing_schedule": {
                    "id": existing.id,
                    "scale_down_time": existing.scale_down_time,
                    "scale_up_time": existing.scale_up_time,
                    "enabled": existing.enabled,
                },
            },
        )

    # Create schedule
    schedule = ScheduleDB(
        namespace=schedule_data.namespace,
        deployment_name=schedule_data.deployment_name,
        scale_down_time=schedule_data.scale_down_time,
        scale_up_time=schedule_data.scale_up_time,
        original_replicas=current_replicas,
        enabled=True,
        is_scaled_down=False,
        last_scaled_at=None,
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    # Check if we're already in the hibernation period
    # If yes, scale down immediately
    tz = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(tz).strftime("%H:%M")

    if is_in_hibernation_period(schedule.scale_down_time, schedule.scale_up_time, current_time):
        # We're in hibernation period, scale down immediately
        try:
            await run_in_threadpool(k8s.scale_down, schedule.namespace, schedule.deployment_name)

            # Update schedule state
            schedule.is_scaled_down = True
            schedule.last_scaled_at = datetime.now(tz)
            schedule.updated_at = datetime.now(tz)

            await db.commit()
            await db.refresh(schedule)
        except Exception:
            # Log the error but don't fail the schedule creation
            # The scheduler will try again at the next minute
            pass

    return schedule


@scheduler_router.patch("/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    k8s: K8sClient = Depends(get_k8s_client),
) -> ScheduleDB:
    """Update a schedule"""
    result = await db.execute(select(ScheduleDB).where(ScheduleDB.id == schedule_id))
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Get current time in configured timezone
    tz = pytz.timezone(settings.TIMEZONE)
    current_time = datetime.now(tz).strftime("%H:%M")

    # Determine the new values after update
    new_scale_down_time = (
        schedule_data.scale_down_time if schedule_data.scale_down_time is not None else schedule.scale_down_time
    )
    new_scale_up_time = (
        schedule_data.scale_up_time if schedule_data.scale_up_time is not None else schedule.scale_up_time
    )
    new_enabled = schedule_data.enabled if schedule_data.enabled is not None else schedule.enabled

    # Case 1: If disabling a schedule that is currently scaled down, scale it back up
    if (
        schedule_data.enabled is not None
        and not schedule_data.enabled  # Disabling
        and schedule.is_scaled_down  # Currently scaled down
        and schedule.original_replicas is not None
    ):
        try:
            await run_in_threadpool(
                k8s.scale_deployment,
                schedule.namespace,
                schedule.deployment_name,
                schedule.original_replicas,
            )
            # Update state
            schedule.is_scaled_down = False
            schedule.last_scaled_at = datetime.now(tz)
        except Exception as e:
            # Log error but continue with update
            import logging

            logging.error(f"Failed to scale up deployment when disabling schedule: {e}")

    # Case 2: If enabling a schedule (or updating times) and currently in hibernation period, scale down immediately
    elif (
        new_enabled  # Schedule will be enabled after update
        and not schedule.is_scaled_down  # Not currently scaled down
        and is_in_hibernation_period(new_scale_down_time, new_scale_up_time, current_time)
    ):
        try:
            # Get current replicas before scaling down
            current_replicas = await run_in_threadpool(
                k8s.get_deployment_replicas, schedule.namespace, schedule.deployment_name
            )

            # Save original replicas if not already saved
            if schedule.original_replicas is None or current_replicas > 0:
                schedule.original_replicas = current_replicas

            # Scale down to 0
            await run_in_threadpool(k8s.scale_down, schedule.namespace, schedule.deployment_name)

            # Update state
            schedule.is_scaled_down = True
            schedule.last_scaled_at = datetime.utcnow()
        except Exception as e:
            # Log error but continue with update
            import logging

            logging.error(f"Failed to scale down deployment when enabling schedule during hibernation period: {e}")

    # Update fields
    if schedule_data.scale_down_time is not None:
        schedule.scale_down_time = schedule_data.scale_down_time
    if schedule_data.scale_up_time is not None:
        schedule.scale_up_time = schedule_data.scale_up_time
    if schedule_data.enabled is not None:
        schedule.enabled = schedule_data.enabled

    await db.commit()
    await db.refresh(schedule)

    return schedule


@scheduler_router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    k8s: K8sClient = Depends(get_k8s_client),
) -> None:
    """Delete a schedule"""
    result = await db.execute(select(ScheduleDB).where(ScheduleDB.id == schedule_id))
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # If deployment is currently scaled down, scale it back up before deleting
    if schedule.is_scaled_down and schedule.original_replicas is not None:
        try:
            await run_in_threadpool(
                k8s.scale_deployment,
                schedule.namespace,
                schedule.deployment_name,
                schedule.original_replicas,
            )
        except Exception as e:
            # Log error but continue with deletion
            import logging

            logging.error(f"Failed to scale up deployment when deleting schedule: {e}")

    await db.delete(schedule)
    await db.commit()

    return None
