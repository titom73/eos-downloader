"""Module to manage data mapping for image types."""

from typing import Dict, List

from pydantic import BaseModel

from eos_downloader.models.types import AristaMapping, ReleaseType


RTYPE_FEATURE: ReleaseType = "F"
RTYPE_MAINTENANCE: ReleaseType = "M"
RTYPES: List[ReleaseType] = [RTYPE_FEATURE, RTYPE_MAINTENANCE]


class ImageInfo(BaseModel):
    """Image information for a specific image type."""

    extension: str
    prepend: str


class DataMapping(BaseModel):
    """Data mapping for image types of CloudVision and EOS on Arista.com."""

    CloudVision: Dict[str, ImageInfo]
    EOS: Dict[str, ImageInfo]

    def filename(self, software: AristaMapping, image_type: str, version: str) -> str:
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
            soft_mapping = getattr(self, software)
            image_config = soft_mapping.get(image_type, None)
            if image_config is None:
                image_config = getattr(soft_mapping, "default", None)
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
        "ova": {"extension": ".ova", "prepend": "cvp"},
        "rpm": {"extension": "", "prepend": "cvp-rpm-installer"},
        "kvm": {"extension": "-kvm.tgz", "prepend": "cvp"},
        "upgrade": {"extension": ".tgz", "prepend": "cvp-upgrade"},
    },
    EOS={
        "64": {"extension": ".swi", "prepend": "EOS64"},
        "INT": {"extension": "-INT.swi", "prepend": "EOS"},
        "2GB-INT": {"extension": "-INT.swi", "prepend": "EOS-2GB"},
        "cEOS": {"extension": ".tar.xz", "prepend": "cEOS-lab"},
        "cEOS64": {"extension": ".tar.xz", "prepend": "cEOS64-lab"},
        "vEOS": {"extension": ".vmdk", "prepend": "vEOS"},
        "vEOS-lab": {"extension": ".vmdk", "prepend": "vEOS-lab"},
        "EOS-2GB": {"extension": ".swi", "prepend": "EOS-2GB"},
        "RN": {"extension": "-", "prepend": "RN"},
        "SOURCE": {"extension": "-source.tar", "prepend": "EOS"},
        "default": {"extension": ".swi", "prepend": "EOS"},
    },
)
