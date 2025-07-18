# GitHub Actions Workflows

This directory contains the GitHub Actions workflows for the Monarch App project.

## Docker Image Building and Deployment

The Docker image building and deployment has been restructured for clarity and to avoid confusion with release tagging:

### Active Workflows

1. **`build-and-deploy-main.yaml`** - Main Branch Development
   - **Triggers**: Push to main branch, manual dispatch
   - **Purpose**: Keeps the dev environment updated with latest main branch code
   - **Tags**: `main-<sha>`, `latest-dev`, `<sha>`
   - **Deployment**: Automatically deploys to dev environment

2. **`build-release-images.yaml`** - Production Releases
   - **Triggers**: Release published
   - **Purpose**: Creates production-ready images for actual releases
   - **Tags**: `latest`, `<release-version>`, `<sha>`
   - **Deployment**: No automatic deployment (production images)

3. **`build-images-for-branch.yaml`** - Branch Testing
   - **Triggers**: Manual dispatch, configurable branch pushes
   - **Purpose**: Build images for specific branches when needed for testing
   - **Tags**: `<branch-name>-<sha>`, `<sha>`
   - **Deployment**: No deployment (testing images only)

### Deprecated Workflows

- **`build-and-deploy-images.yaml.deprecated`** - Old combined workflow
  - This workflow was causing confusion by tagging images with old release versions on every main branch push
  - Functionality has been split into the three workflows above for better clarity

## Other Workflows

- **`test-backend.yaml`** - Backend testing
- **`test-frontend.yaml`** - Frontend testing
- **`publish-backend.yaml`** - PyPI publishing on releases
- **`codecov_main.yaml`** - Code coverage reporting
- **`deploy-documentation.yaml`** - Documentation deployment
- **`update-resource-data.yaml`** - Resource data updates

## Usage

### For Development
- Push to main branch → automatic dev deployment via `build-and-deploy-main.yaml`

### For Releases
- Create and publish a GitHub release → production images built via `build-release-images.yaml`

### For Branch Testing
- Use "Run workflow" button on `build-images-for-branch.yaml` to build images for any branch
- Or add specific branch names to the workflow file for automatic builds