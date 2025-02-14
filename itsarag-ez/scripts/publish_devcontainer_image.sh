#!/usr/bin/env bash
set -euo pipefail
[[ ${DEBUG-} =~ ^1|yes|true$ ]] && set -o xtrace

source=devcontainers/its-a-rag
target=dbroeglin/its-a-rag:dev

printf '\033[32m➜ Just double checking. Did you update \n'
printf '  devcontainers/its-a-rag/.devcontainer/feature/requirements.txt ?\033[0m\n\n' 

if [[ "$(docker info -f '{{ .DriverStatus }}')" != "[[driver-type io.containerd.snapshotter.v1]]" ]];
then
	printf '\033[31m➜ To store multi platform images, you need the containerd image\n'
	printf '  store enabled for in your Docker engine\n'
	printf '  See https://docs.docker.com/engine/storage/containerd/\033[0m\n\n'
	exit -1
fi

cd ${source} 
devcontainer build \
	--workspace-folder . \
	--push true \
	--image-name ${target} \
	--platform linux/amd64,linux/arm64
