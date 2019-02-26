DOCKER_REGISTRY := docker.chameleoncloud.org
DOCKER_REPO := gnocchi-metric-collector
DOCKER_TAG := $(shell git rev-parse --short HEAD)

DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(DOCKER_REPO):$(DOCKER_TAG)

.PHONY: build
build:
	docker build -t $(DOCKER_IMAGE) .

.PHONY: publish
publish:
	docker push $(DOCKER_IMAGE)
	docker tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY)/$(DOCKER_REPO):stable
