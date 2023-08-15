SHELL := /bin/bash
include .env
export

define do_build_docker
	echo "✨ Building docker image..."
	docker build --platform='linux/amd64' \
	--build-arg PY_VERSION=$(PY_VERSION) \
	--build-arg PORT=$(1) \
	--build-arg APP_LOCAL_PATH=$(2) \
	--tag "$(DOCKER_ACCOUNT)/$(3):latest" . \
	--file $(4)
endef

define do_push_docker
	echo "✨ Pushing docker image..."
	docker push "$(DOCKER_ACCOUNT)/$(1):latest"
endef

define do_make_manifests
	echo "✨ Making manifests..."
	for file in src/$(1)/manifests/*.yaml; do \
		envsubst < $$file | kubectl apply -f -; \
	done
endef

auth_build_docker:
	$(call do_build_docker,$(PORT_AUTH),$(AUTH_LOCAL_PATH),$(AUTH_DOCKER_REPO),src/auth/Dockerfile)

auth_push_docker:
	$(call do_push_docker,$(AUTH_DOCKER_REPO))

auth_manifests:
	$(call do_make_manifests,auth)

gateway_build_docker:
	$(call do_build_docker,$(PORT_GATEWAY),$(GATEWAY_LOCAL_PATH),$(GATEWAY_DOCKER_REPO),src/gateway/Dockerfile)

gateway_push_docker:
	$(call do_push_docker,$(GATEWAY_DOCKER_REPO))

gateway_manifests:
	$(call do_make_manifests,gateway)
