# Docker images for each Revolution Pi images

This repository contains Dockerfile for each Revolution Pi images ([here](https://revolutionpi.com/tutorials/downloads/#revpiimages)). Pre-built images can be found [here](https://hub.docker.com/r/lbautomata/revpi), each tag represent a different version of the image.

## Usage

In order to run the images using systemd, you will need the following setup:
```bash
docker run --tmpfs /run --tmpfs /run/lock --tmpfs /tmp -v /sys/fs/cgroup:/sys/fs/cgroup -p 22:22 lbautomata/revpi:YOUR_TAG
```

You should be able to SSH in the same way you do with any Raspberry Pi.

## Building images

All the images can be built using `make build` and pushed with `make push`.

Running `make clear` will put back the repository in a fresh state.

## Adding new images

Edit `images.py` and add the name of the image (will be the Docker tag) and the file ID on the Revolution Pi website.

## Static analysis

You can lint and format the code using `make lint` (or `make lint-fix` to fix formatting issues).
