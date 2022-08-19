#!/usr/bin/env python3

import os
import subprocess
import sys

build_folder = "images"


def main() -> int:
    for filename in os.listdir(build_folder):
        filepath = os.path.join(build_folder, filename)
        if not os.path.isfile(filepath):
            continue
        _, tag = os.path.splitext(filepath)
        tag = tag[1:]
        print(f"building {tag}")
        subprocess.run(["docker", "build", "-t", f"lbautomata/revpi:{tag}", "-f", filepath, "."], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
