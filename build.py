#!/usr/bin/env python3

import argparse
import os
import random
import subprocess
import sys
from urllib.request import urlretrieve
from zipfile import ZipFile

from tqdm import tqdm

build_folder = "images"
images = [
    ("buster-08-2022", "6224"),
    ("buster-lite-08-2022", "6226"),
    ("buster-05-2022", "5435"),
    ("buster-lite-05-2022", "6086"),
    ("stretch", "5433"),
    ("jessie", "5431"),
]


def download_file(file_id: str, dest: str) -> None:
    with tqdm(unit="B", unit_scale=True) as pbar:

        def show_progress(block_num: int, block_size: int, total_size: int) -> None:
            pbar.reset(total=total_size)
            downloaded = block_num * block_size
            if downloaded < total_size:
                pbar.update(downloaded - pbar.n)

        try:
            urlretrieve(f"https://revolutionpi.com/download/{file_id}/", filename=dest, reporthook=show_progress)
        except KeyboardInterrupt:
            os.remove(dest)
            raise


def extract_img(src: str, dest: str) -> None:
    with ZipFile(src) as archive:
        img = None
        for filename in archive.namelist():
            if filename.endswith(".img"):
                if img is not None:
                    raise RuntimeError(f"duplicated img ({img} and {filename}) in {src}")
                img = filename
        if img is None:
            raise RuntimeError(f"did not find an img in {src}")
        with archive.open(img) as fsrc:
            with open(dest, "wb") as fdest:
                with tqdm(total=archive.getinfo(img).file_size, unit="B", unit_scale=True) as fbar:
                    try:
                        while True:
                            buffer = fsrc.read(8192)
                            if buffer == b"":
                                break
                            fdest.write(buffer)
                            fbar.update(len(buffer))
                    except KeyboardInterrupt:
                        os.remove(dest)
                        raise


def extract_partition(src: str, dest: str) -> None:
    dest_folder, dest_file = os.path.split(dest)
    loop = random.randrange(10, 50)  # Ensure that even if it fails a few times, it's unlikely we will have conflicts
    command = " && ".join(
        [
            # Install required commands
            f"echo setup",
            "apk add pv",
            # Remove created loop devices as they tend to stick with --privileged
            f"""cleanup()
{{
  echo cleanup
  losetup -d /dev/loop{loop}
  rm /dev/loop{loop} /dev/loop{loop}p2
}}""",
            # Setup a subgroup for cleanup
            "( true",
            # Create a new loop device (it it doesn't exist) so we don't conflict with existing ones
            f"echo create main loop{loop} device",
            f"([ ! -f /dev/loop{loop} ] && mknod /dev/loop{loop} b 7 {loop})",
            # Clear existing any association and associate our image (scanning for partition)
            "echo associate image to loop device",
            f"losetup -a /dev/loop{loop}",
            f"losetup -P /dev/loop{loop} /img",
            # Create the partition sub-loop device manually as Docker doesn't pick it up automatically
            "echo creating partition loop device",
            f"([ ! -f /dev/loop{loop}p2 ] && mknod /dev/loop{loop}p2 b 259 1)",
            # Finally mount the device on the file system
            "echo mounting partition",
            f"mount /dev/loop{loop}p2 /mnt",
            # Create a tar.gz of the whole thing
            "echo creating archive",
            f"tar cf - -C /mnt . | pv -f -s `du -s /mnt | cut -f1`k | gzip > /out/{dest_file}",
            # Ensure cleanup always run
            "cleanup ) || (cleanup && false)",
        ]
    )
    p = subprocess.Popen(
        [
            "docker",
            "run",
            "--privileged",
            "--rm",
            "-v",
            f"{os.path.abspath(src)}:/img",
            "-v",
            f"{os.path.abspath(dest_folder)}:/out:rw",
            "--entrypoint",
            "/bin/sh",
            "alpine:latest",
            "-c",
            command,
        ],
    )
    try:
        if p.wait() != 0:
            raise RuntimeError("docker extraction failed")
    except KeyboardInterrupt:
        p.terminate()
        os.remove(dest)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()

    os.makedirs(build_folder, exist_ok=True)

    pbar = tqdm(images)
    for tag, file_id in pbar:
        pbar.set_description(f"processing {tag}")

        zip_dest = os.path.join(build_folder, f"{file_id}.zip")
        if not os.path.exists(zip_dest):
            pbar.set_description(f"downloading {tag} base image")
            download_file(file_id, zip_dest)

        img_dest = os.path.join(build_folder, f"{file_id}.img")
        if not os.path.exists(img_dest):
            pbar.set_description(f"extracting {tag} img")
            extract_img(zip_dest, img_dest)

        tarball_dest = os.path.join(build_folder, f"{file_id}.tar.gz")
        if not os.path.exists(tarball_dest):
            pbar.set_description(f"mount and tarball {tag} partition")
            extract_partition(img_dest, tarball_dest)

        pbar.set_description(f"building {tag}")
        subprocess.run(
            ["docker", "build", "-t", f"lbautomata/revpi:{tag}", "-f", "Dockerfile.revpi", f"--build-arg=FILE_ID={file_id}", "."],
            check=True,
        )
        if args.push:
            pbar.set_description(f"pushing {tag}")
            subprocess.run(["docker", "push", f"lbautomata/revpi:{tag}"], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
