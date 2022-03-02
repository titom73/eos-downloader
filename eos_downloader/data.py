#!/usr/bin/python
# coding: utf-8 -*-

# [platform][image][version]
DATA_MAPPING = {
    "EOS": {
        "64": {
            "extension": ".swi",
            "prepend": "EOS64",
            "folder_level": 0
        },
        "INT": {
            "extension": "-INT.swi",
            "prepend": "EOS",
            "folder_level": 1
        },
        "2GB-INT": {
            "extension": "-INT.swi",
            "prepend": "EOS-2GB",
            "folder_level": 1
        },
        "cEOS": {
            "extension": ".tar.xz",
            "prepend": "cEOS-lab",
            "folder_level": 0
        },
        "cEOS64": {
            "extension": ".tar.xz",
            "prepend": "cEOS64-lab",
            "folder_level": 0
        },
        "vEOS": {
            "extension": ".vmdk",
            "prepend": "vEOS",
            "folder_level": 0
        },
        "vEOS-lab": {
            "extension": ".vmdk",
            "prepend": "vEOS-lab",
            "folder_level": 0
        },
        "EOS-2GB": {
            "extension": ".swi",
            "prepend": "EOS-2GB",
            "folder_level": 0
        },
        "RN": {
            "extension": "-",
            "prepend": "RN",
            "folder_level": 0
        },
        "SOURCE": {
            "extension": "-source.tar",
            "prepend": "EOS",
            "folder_level": 0
        },
        "default": {
            "extension": ".swi",
            "prepend": "EOS",
            "folder_level": 0
        }
    }
}
