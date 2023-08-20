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

define do_delete_manifests
	echo "✨ Deleting manifests..."
	for file in src/$(1)/manifests/*.yaml; do \
		envsubst < $$file | kubectl delete -f -; \
	done
endef

export_env:
	export $(grep -v ^# .env | xargs)

auth_build_docker:
	$(call do_build_docker,$(PORT_AUTH),$(AUTH_LOCAL_PATH),$(AUTH_DOCKER_REPO),src/auth/Dockerfile)

auth_push_docker:
	$(call do_push_docker,$(AUTH_DOCKER_REPO))

auth_manifests:
	$(call do_make_manifests,auth)

auth_delete_manifests:
	$(call do_delete_manifests,auth)

gateway_build_docker:
	$(call do_build_docker,$(PORT_GATEWAY),$(GATEWAY_LOCAL_PATH),$(GATEWAY_DOCKER_REPO),src/gateway/Dockerfile)

gateway_push_docker:
	$(call do_push_docker,$(GATEWAY_DOCKER_REPO))

gateway_manifests:
	$(call do_make_manifests,gateway)

gateway_delete_manifests:
	$(call do_delete_manifests,gateway)

rabbitmq_manifests:
	$(call do_make_manifests,rabbitmq)

rabbitmq_delete_manifests:
	$(call do_delete_manifests,rabbitmq)

converter_build_docker:
	$(call do_build_docker,,$(CONVERTER_LOCAL_PATH),$(CONVERTER_DOCKER_REPO),src/converter/Dockerfile)

converter_push_docker:
	$(call do_push_docker,$(CONVERTER_DOCKER_REPO))

converter_manifests:
	$(call do_make_manifests,converter)

converter_delete_manifests:
	$(call do_delete_manifests,converter)
