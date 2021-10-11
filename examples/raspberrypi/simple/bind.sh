#!/bin/bash
docker volume create yocto-factory-data
docker run \
  --name yocto-factory \
  --interactive --tty --rm \
  --volume yocto-factory-data:/build/yocto \
  --volume $PWD:/project \
  fotahub/yocto-factory:2021.1.0 \
  $@