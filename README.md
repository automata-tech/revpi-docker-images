# Docker images for each Revolution Pi images

This repository contains Dockerfile for each Revolution Pi images ([here](https://revolutionpi.com/tutorials/downloads/#revpiimages)). Pre-built images can be found [here](https://hub.docker.com/r/lbautomata/revpi), each tag represent a different version of the image.

## Usage

All the images are stored in `images` and can be built using `make build`.

You can build individual images manually using:
```bash
docker build -t buster-05-2022 -f images/Dockerfile.buster-05-2022 .
```

Those images are generated using `make images`.

Running `make clear` will put back the repository in a fresh state and running `make` will build everything correctly.

## Adding new images

Edit `images.py` and add the name of the image (will be the Docker tag) and the file ID on the Revolution Pi website.

## Static analysis

You can lint and format the code using `make lint` (or `make lint-fix` to fix formatting issues).
