# syntax=docker/dockerfile:1

# Runtime image for `sirgent gateway`.
#
# This image does NOT build the binary. It expects a prebuilt native
# linux-x64 `sirgent` executable in the build context — the public SirGent AI
# release binary, which includes the `gateway` subcommand. setup.sh places it
# at ./sirgent (downloading it from the public release endpoint and verifying
# it against the release manifest if missing). Override SIRGENT_BINARY to
# point at a different path.
#
# Build (with the binary at ./sirgent; otherwise add --build-arg SIRGENT_BINARY=<path>):
#   docker build --platform=linux/amd64 --provenance=false -t sirgent-gateway .
#
# Run:
#   docker run --rm -p 8080:8080 \
#     -v "$PWD/gateway.yaml:/etc/sirgent/gateway.yaml:ro" \
#     -e OIDC_CLIENT_SECRET -e GATEWAY_JWT_SECRET -e GATEWAY_POSTGRES_URL \
#     sirgent-gateway

ARG SIRGENT_BINARY=./sirgent

# distroless/cc provides glibc + libstdc++ (required by the Bun-compiled
# native binary). The :nonroot tag runs as uid/gid 65532.
FROM gcr.io/distroless/cc-debian12:nonroot

ARG SIRGENT_BINARY
COPY --chmod=0755 ${SIRGENT_BINARY} /usr/local/bin/sirgent

ENV SIRGENT_CONFIG_DIR=/tmp/.sirgent

EXPOSE 8080
USER nonroot

ENTRYPOINT ["/usr/local/bin/sirgent", "gateway", "--config", "/etc/sirgent/gateway.yaml"]
