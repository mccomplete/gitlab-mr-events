# Run this script from the project root.

DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker build -t gitlab-extractor -f build/Dockerfile .
