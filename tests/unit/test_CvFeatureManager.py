#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
import os
import platform
from loguru import logger
import logging
import pytest
import eos_downloader
from eos_downloader.eos import EOSDownloader
from eos_downloader.data import DATA_MAPPING
from eos_downloader.cvp import *
from cvprac.cvp_client import CvpClient



# Get Auth token
eos_token = os.getenv('ARISTA_TOKEN', 'unset_token')
eos_token_invalid = 'invalid_token'

cvp_token = os.getenv('ARISTA_AVD_CV_TOKEN', 'unset_token')
cvp_instance = os.getenv('ARISTA_AVD_CV_SERVER', 'unset_server')


cvp_dataset = [
    {
        'server': cvp_instance,
        'token': cvp_token,
        'port': 443,
        'timeout': 1200,
        'validate_cert': False
    }
]

fileItem_dataset = [
    {
        'path': 'tests/EOS-4.27.1.1F.swi',
        'expected_filename': 'EOS-4.27.1.1F.swi',
        'expected_absolute_path': 'tests/EOS-4.27.1.1F.swi',
        'expected_exist': True
    },
    {
        'path': 'tests/EOS-4.27.1.1F.swi.gz',
        'expected_filename': '',
        'expected_absolute_path': '',
        'expected_exist': False
    }
]

@pytest.fixture(params=[cvp_dataset])
def create_test_object(request):
    # logger.info("Execute fixture to create class elements")
    request.cls.cv_data = CvpAuthenticationItem(**request.param[0])
    yield
    # logger.info('Cleanup test environment')



@pytest.mark.parametrize("CVP_INFO", cvp_dataset, ids=['CVaaS'])
class Test_CvpAuthenticationItem():

    def test_data(self, CVP_INFO):
        print(str(CVP_INFO))
        assert True

    def test_load_cvp_data(self, CVP_INFO):
        cvp_auth_data = CvpAuthenticationItem(**CVP_INFO)
        assert cvp_auth_data.server == CVP_INFO['server']


@pytest.mark.parametrize("DATASET", fileItem_dataset, ids=['Existing file', 'Not Existing File'])
class Test_FileItem():

    def test_display_input(self, DATASET):
        print(DATASET)
        assert True

    def test_filer_creation(self, DATASET):
        filer = Filer(path=DATASET['path'])
        assert type(filer) is Filer

    def test_filer_file_exists(self, DATASET):
        logger.info('Testing Filer with file: {}'.format(DATASET['path']))
        filer = Filer(path=DATASET['path'])
        assert filer.file_exist is DATASET['expected_exist']

    def test_filer_filename(self, DATASET):
        logger.info('Testing Filer with file: {}'.format(DATASET['path']))
        filer = Filer(path=DATASET['path'])
        assert filer.filename == DATASET['expected_filename']


@pytest.mark.usefixtures("create_test_object")
@pytest.mark.parametrize("CVP_INFO", cvp_dataset, ids=['CVaaS'])
class Test_CvFeatureManager_base():
    def test_cvp_data(self, CVP_INFO):
        print(self.cv_data)
        assert True

    def test_create_instance(self, CVP_INFO):
        # self.cv_data = CvpAuthenticationItem(**CVP_INFO)
        cvp_manager = CvFeatureManager(authentication=self.cv_data)
        assert type(cvp_manager) is CvFeatureManager

    def test_connect_to_cvp(self, CVP_INFO):
        self.cv_data = CvpAuthenticationItem(**CVP_INFO)
        cvp_manager = CvFeatureManager(authentication=self.cv_data)
        connection_result = cvp_manager._connect(authentication=self.cv_data)
        assert type(connection_result) is CvpClient
        logger.info('Connected to CV instance')

    @pytest.mark.parametrize("DATASET", fileItem_dataset, ids=['Existing file', 'Not Existing File'])
    def test_upload_image(self, CVP_INFO, DATASET):
        self.cv_data = CvpAuthenticationItem(**CVP_INFO)
        cvp_manager = CvFeatureManager(authentication=self.cv_data)
        cvp_manager.upload_image(DATASET['path'])

    @pytest.mark.parametrize("DATASET", fileItem_dataset, ids=['Existing file', 'Not Existing File'])
    def test_image_present(self, CVP_INFO, DATASET):
        self.cv_data = CvpAuthenticationItem(**CVP_INFO)
        cvp_manager = CvFeatureManager(authentication=self.cv_data)
        if DATASET['expected_filename'] != '':
            result = cvp_manager._does_image_exist(image_name=DATASET['expected_filename'])
            assert result is DATASET['expected_exist']
        assert True

    @pytest.mark.parametrize("DATASET", fileItem_dataset, ids=['Existing file', 'Not Existing File'])
    def test_create_bundle(self, CVP_INFO, DATASET):
        self.cv_data = CvpAuthenticationItem(**CVP_INFO)
        cvp_manager = CvFeatureManager(authentication=self.cv_data)
        if DATASET['expected_filename'] != '':
            result = cvp_manager.create_bundle(name='Test', images_name=[DATASET['expected_filename']])
            assert result is DATASET['expected_exist']
        assert True
