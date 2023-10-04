# This Dockerfile is used to build a supplementary image, based on
# the Monarch API image, that runs the OAK RPC server.
# Note that it takes a build argument, FROM_IMAGE, which should be the
# API image and tag that's associated with the current build.
# It assumes that the build context is the root of the repository.
# The image is built using the following command structure:
#  (from the root of the repository, i.e. .../monarch-app)
#  docker build \
#    --build-arg="FROM_IMAGE=<API image:tag>" \
#    -f services/oak_lib/Dockerfile .

ARG FROM_IMAGE
FROM ${FROM_IMAGE}

COPY ./services/oak_rpc_server/start_rpc_service.sh /var/oak_server/start_rpc_service.sh
COPY ./services/oak_rpc_server/rpc_healthcheck.py /var/oak_server/rpc_healthcheck.py

HEALTHCHECK \
    --interval=30s --timeout=15s --retries=3 \
    --start-period=120s \
    CMD poetry run python /var/oak_server/rpc_healthcheck.py || exit 1

CMD /var/oak_server/start_rpc_service.sh
