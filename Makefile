CONTAINER_REGISTRY_URL=eu.gcr.io
PROJECT_ID=ithil-goerli-bots
SERVICE=discord-helper-bot

.PHONY: upgrade-dependencies
upgrade-dependencies:
	poetry update

.PHONY: build-docker-image
build-docker-image:
	poetry export >> requirements.txt && \
	    docker build . \
	    --iidfile .dockeriid \
	    --tag $(CONTAINER_REGISTRY_URL)/$(PROJECT_ID)/$(SERVICE):latest

.PHONY: push-image-to-container-registry
push-image-to-container-registry: build-docker-image
	docker push $(CONTAINER_REGISTRY_URL)/$(PROJECT_ID)/$(SERVICE):latest

.PHONY: start
start: build-docker-image
	docker run -it -p 8080:8080 $$(cat .dockeriid)

.PHONY: monitor
monitor:
	watch -n 5 curl -s https://price-bot-cjgn7z6ucq-lz.a.run.app
