# Docker Registry Setup

This document explains how to configure GitHub secrets for automated Docker image publishing.

## GitHub Container Registry (ghcr.io)

GitHub Container Registry is automatically configured using `GITHUB_TOKEN`. No additional setup required!

## Docker Hub Setup

To push images to Docker Hub, you need to configure two secrets:

### 1. Create a Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/)
2. Click on your profile → **Account Settings**
3. Go to **Security** → **Access Tokens**
4. Click **New Access Token**
5. Give it a name (e.g., "GitHub Actions hyb8nate")
6. Set permissions: **Read & Write**
7. Click **Generate** and copy the token

### 2. Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

   **Secret 1: `DOCKERHUB_USERNAME`**
   - Name: `DOCKERHUB_USERNAME`
   - Value: Your Docker Hub username (e.g., `romain` or your username)

   **Secret 2: `DOCKERHUB_TOKEN`**
   - Name: `DOCKERHUB_TOKEN`
   - Value: The access token you generated in step 1

### 3. Update Docker Hub Image Name (Optional)

If your Docker Hub username is different, edit `.github/workflows/docker-publish.yml`:

```yaml
env:
  DOCKERHUB_IMAGE: your-dockerhub-username/hyb8nate
```

## How It Works

### Triggers

The workflow runs on:
- **Push to `main` branch**: Builds and pushes with multiple tags
- **Git tags** (e.g., `v1.0.0`): Builds and pushes with version tags
- **Pull requests**: Only builds (doesn't push)

### Image Tags

The workflow automatically creates multiple tags:

**Sur push vers `main`** :
- `latest` - Dernière version stable
- `stable` - Même que latest, pour compatibilité
- `2025.01.02` - Tag automatique avec la date du build
- `sha-abc1234` - Tag avec le commit SHA pour traçabilité

**Sur création de tag git** (ex: `v1.0.0`) :
- `1.0.0` - Version complète
- `latest` + `stable` - Mis à jour aussi
- `2025.01.02` - Tag avec date
- `sha-abc1234` - Tag avec SHA

### Multi-Architecture Support

Images are built for:
- `linux/amd64` (Intel/AMD)
- `linux/arm64` (ARM, Apple Silicon)

## Usage Examples

### Pull from GitHub Container Registry
```bash
# Dernière version
docker pull ghcr.io/hyb8nate/hyb8nate:latest

# Version stable (identique à latest)
docker pull ghcr.io/hyb8nate/hyb8nate:stable

# Version spécifique par date
docker pull ghcr.io/hyb8nate/hyb8nate:2025.01.02

# Version sémantique
docker pull ghcr.io/hyb8nate/hyb8nate:1.0.0
```

### Pull from Docker Hub
```bash
# Dernière version
docker pull your-dockerhub-username/hyb8nate:latest

# Version stable
docker pull your-dockerhub-username/hyb8nate:stable

# Version par date
docker pull your-dockerhub-username/hyb8nate:2025.01.02
```

## Creating a Release

To create a versioned release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger the workflow and create images tagged as:
- `1.0.0` - Version complète
- `latest` - Dernière version stable
- `stable` - Version stable
- `2025.01.02` - Date du build
- `sha-abc1234` - SHA du commit

## Troubleshooting

### "unauthorized: authentication required"
- Check that your Docker Hub secrets are correctly configured
- Verify the access token has **Read & Write** permissions

### "denied: permission_denied"
- For Docker Hub: Check username and token are correct
- For GHCR: Check that repository has **Actions** permissions enabled

### Build fails
- Check the Actions logs in the **Actions** tab
- Verify your Dockerfile builds locally: `docker build -t test .`
