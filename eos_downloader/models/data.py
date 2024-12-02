"""Module to manage data mapping for image types."""

from pydantic import BaseModel
from typing import Dict


class ImageInfo(BaseModel):
    """Image information for a specific image type."""
    extension: str
    prepend: str
    folder_level: int


class DataMapping(BaseModel):
    """Data mapping for image types of CloudVision and EOS on Arista.com."""
    CloudVision: Dict[str, ImageInfo]
    EOS: Dict[str, ImageInfo]

    def filename(self, software: str, image_type: str, version: str) -> str:
        """Generates a filename based on the provided software, image type, and version.

        Args:
            software (str): The name of the software for which the filename is being generated.
            image_type (str): The type of image for which the filename is being generated.
            version (str): The version of the software or image.

        Returns:
            str: The generated filename.

        Raises:
            ValueError: If the software does not have a corresponding mapping.
            ValueError: If no configuration is found for the given image type and no default configuration is available.
        """
        if hasattr(self, software):
            software_mapping = getattr(self, software)
            image_config = software_mapping.get(image_type, None)
            if image_config is None:
                image_config = getattr(software_mapping, "default", None)
                if image_config is None:
                    raise ValueError(
                        f"No default configuration found for image type {image_type}"
                    )
            if image_config is not None:
                return f"{image_config.prepend}-{version}{image_config.extension}"
            raise ValueError(f"No configuration found for image type {image_type}")
        raise ValueError(f"Incorrect value for software {software}")


# Data mapping for image types of CloudVision and EOS on Arista.com.
software_mapping = DataMapping(
    CloudVision={
        "ova": {"extension": ".ova", "prepend": "cvp", "folder_level": 0},
        "rpm": {"extension": "", "prepend": "cvp-rpm-installer", "folder_level": 0},
        "kvm": {"extension": "-kvm.tgz", "prepend": "cvp", "folder_level": 0},
        "upgrade": {"extension": ".tgz", "prepend": "cvp-upgrade", "folder_level": 0},
    },
    EOS={
        "64": {"extension": ".swi", "prepend": "EOS64", "folder_level": 0},
        "INT": {"extension": "-INT.swi", "prepend": "EOS", "folder_level": 1},
        "2GB-INT": {"extension": "-INT.swi", "prepend": "EOS-2GB", "folder_level": 1},
        "cEOS": {"extension": ".tar.xz", "prepend": "cEOS-lab", "folder_level": 0},
        "cEOS64": {"extension": ".tar.xz", "prepend": "cEOS64-lab", "folder_level": 0},
        "vEOS": {"extension": ".vmdk", "prepend": "vEOS", "folder_level": 0},
        "vEOS-lab": {"extension": ".vmdk", "prepend": "vEOS-lab", "folder_level": 0},
        "EOS-2GB": {"extension": ".swi", "prepend": "EOS-2GB", "folder_level": 0},
        "RN": {"extension": "-", "prepend": "RN", "folder_level": 0},
        "SOURCE": {"extension": "-source.tar", "prepend": "EOS", "folder_level": 0},
        "default": {"extension": ".swi", "prepend": "EOS", "folder_level": 0},
    },
)
