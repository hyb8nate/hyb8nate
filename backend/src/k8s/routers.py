"""Kubernetes API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from src.shared.auth.auth_simple import get_current_user
from src.shared.settings import settings
from src.schedules.models import DeploymentInfo
from .services import K8sClient, get_k8s_client

kubernetes_router = APIRouter(tags=["kubernetes"])


@kubernetes_router.get("/namespaces", response_model=list[str])
async def list_namespaces(
    k8s: K8sClient = Depends(get_k8s_client),
    current_user: dict = Depends(get_current_user),
) -> list[str]:
    """List allowed Kubernetes namespaces (with hyb8nate label)"""
    try:
        namespaces = await run_in_threadpool(
            k8s.list_allowed_namespaces,
            settings.NAMESPACE_LABEL_KEY,
            settings.NAMESPACE_LABEL_VALUE,
        )
        return namespaces
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list namespaces: {str(e)}",
        )


@kubernetes_router.get("/namespaces/{namespace}/deployments")
async def list_deployments(
    namespace: str,
    k8s: K8sClient = Depends(get_k8s_client),
    current_user: dict = Depends(get_current_user),
) -> list[DeploymentInfo]:
    """List all deployments in a specific namespace"""
    try:
        deployments = await run_in_threadpool(k8s.list_deployments, namespace)
        return deployments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list deployments: {str(e)}",
        )
