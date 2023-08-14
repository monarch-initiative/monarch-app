#!/usr/bin/env bash

# this testing script emulates the image build process for monarch-ui defined in
# /.github/workflows/deploy-frontend.yaml, and also runs the image
# on port 8085 if the build succeeds

# build the frontend
REPO_DIR=$( cd $( git rev-parse --show-toplevel ) && pwd )
(
    cd ${REPO_DIR}/frontend
    yarn install && yarn build
)

# build our custom nginx image, which copies the frontend from ./frontend/dist
# into the image.
# note that this uses the repo root as the context so that it
# can access both the ./services and ./frontend folders.
docker build -t monarch-ui:latest \
    -f ${REPO_DIR}/services/nginx/Dockerfile \
    ${REPO_DIR}
BUILD_RESULT=$?

if [[ ${BUILD_RESULT} -eq 0 ]]; then
    docker run -p 8085:80 --rm -it monarch-ui "$@"
fi
