#!/usr/bin/env python3

import os
import sys

build_folder = "images"
images = [
    ("buster-08-2022", "6224"),
    ("buster-lite-08-2022", "6226"),
    ("buster-05-2022", "5435"),
    ("buster-lite-05-2022", "6086"),
    ("stretch", "5433"),
    ("jessie", "5431"),
]


def main() -> int:
    os.makedirs(build_folder, exist_ok=True)
    for tag, file_id in images:
        with open(os.path.join(build_folder, f"Dockerfile.{tag}"), "w") as f:
            image = f"""FROM scratch
ADD https://revolutionpi.com/download/{file_id}/ /
"""
            f.write(image)
    return 0


if __name__ == "__main__":
    sys.exit(main())
