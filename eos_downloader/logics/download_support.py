"""Support utilities extracted from :mod:`eos_downloader.logics.download`."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import warnings
from pathlib import Path
from typing import Optional

from loguru import logger

from eos_downloader.models.types import ProgressMode


def resolve_progress_mode(
    progress: ProgressMode, rich_interface: Optional[bool]
) -> ProgressMode:
    """Resolve the effective progress mode, honoring the deprecated alias."""
    if rich_interface is not None:
        warnings.warn(
            "The 'rich_interface' parameter is deprecated; use "
            "progress='auto'|'rich'|'plain'|'none' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return "plain" if rich_interface is False else "auto"
    return progress


def ensure_destination_folder(path: str) -> None:
    """Create a directory path if it does not already exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as error:
        logger.critical(f"Error creating folder: {error}")


def compute_hash_md5sum(file_path: str, hash_expected: str) -> bool:
    """Compare a local file MD5 hash with the expected digest."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as stream:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            hash_md5.update(chunk)
    if hash_md5.hexdigest() == hash_expected:
        return True
    logger.warning(
        "Downloaded file is corrupt: local md5 "
        f"({hash_md5.hexdigest()}) is different to md5 from arista ({hash_expected})"
    )
    return False


def docker_image_exists(image_name: str, image_tag: str) -> bool:
    """Check if a Docker or Podman image with the requested tag exists locally."""
    for cmd in ["docker", "podman"]:
        if not shutil.which(cmd):
            logger.debug(f"{cmd} command not found in PATH")
            continue

        try:
            result = subprocess.run(
                [cmd, "images", "-q", f"{image_name}:{image_tag}"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.stdout.strip():
                logger.info(f"Docker image {image_name}:{image_tag} found in local registry")
                return True

            logger.debug(f"Docker image {image_name}:{image_tag} not found in local registry")
            return False
        except subprocess.TimeoutExpired:
            logger.warning(f"{cmd} command timed out after 5 seconds")
            continue
        except (subprocess.SubprocessError, OSError) as error:
            logger.debug(f"Error checking {cmd} images: {error}")
            continue

    logger.warning("Unable to check Docker images (docker/podman not available)")
    return False


def import_docker_archive(
    docker_path: str,
    local_file_path: str,
    docker_name: str,
    docker_tag: str,
) -> None:
    """Import a local archive into Docker."""
    cmd_args = [
        docker_path,
        "import",
        str(local_file_path),
        f"{docker_name}:{docker_tag}",
    ]
    logger.debug(f"Executing: {' '.join(cmd_args)}")
    subprocess.run(cmd_args, check=True, capture_output=True, text=True)


def convert_vmdk_to_qcow2(qemu_img_path: str, vmdk_path: str, qcow2_path: str) -> None:
    """Convert a VMDK image into QCOW2 format."""
    subprocess.run(
        [
            qemu_img_path,
            "convert",
            "-f",
            "vmdk",
            "-O",
            "qcow2",
            vmdk_path,
            qcow2_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def fix_eve_permissions(unl_wrapper_path: Path) -> bool:
    """Run the EVE-NG permission fix wrapper when available."""
    if not unl_wrapper_path.exists():
        logger.warning(f"unl_wrapper not found at {unl_wrapper_path}")
        return False
    subprocess.run(
        [str(unl_wrapper_path), "-a", "fixpermissions"],
        check=True,
        capture_output=True,
        text=True,
    )
    return True
