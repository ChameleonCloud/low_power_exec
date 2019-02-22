DOCKER_REGISTRY := docker.chameleoncloud.org
DOCKER_REPO := user-metric-collector
DOCKER_TAG := stable

DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(DOCKER_REPO):$(DOCKER_TAG)

.PHONY: build
build:
	docker build -t $(DOCKER_IMAGE) .

.PHONY: publish
publish:
	docker push $(DOCKER_IMAGE)
