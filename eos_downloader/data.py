#!/usr/bin/python
# coding: utf-8 -*-

"""
EOS Downloader Information to use in
eos_downloader.object_downloader.ObjectDownloader._build_filename.

Data are built from content of Arista XML file
"""


# [platform][image][version]
DATA_MAPPING = {
    "CloudVision": {
        "ova": {"extension": ".ova", "prepend": "cvp", "folder_level": 0},
        "rpm": {"extension": "", "prepend": "cvp-rpm-installer", "folder_level": 0},
        "kvm": {"extension": "-kvm.tgz", "prepend": "cvp", "folder_level": 0},
        "upgrade": {"extension": ".tgz", "prepend": "cvp-upgrade", "folder_level": 0},
    },
    "EOS": {
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
}
