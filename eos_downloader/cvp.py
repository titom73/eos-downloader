#!/usr/bin/python
# coding: utf-8 -*-

from posixpath import basename
from loguru import logger
from dataclasses import dataclass
import os
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpLoginError
from typing import List


@dataclass
class CvpAuthenticationItem:
    """
     Data structure to represent Cloudvision Authentication
    """
    server: str
    port: int = 443
    token: str = None
    timeout: int = 1200
    validate_cert: bool = False


class Filer():
    """
    Filer Helper for file management
    """
    def __init__(self, path: str):
        self.file_exist = False
        self.filename = ''
        self.absolute_path = ''
        self.relative_path = path
        if os.path.exists(path):
            self.file_exist = True
            self.filename = os.path.basename(path)
            self.absolute_path = os.path.realpath(path)

    def __repr__(self):
        if self.file_exist:
            return self.absolute_path
        return ''


class CvFeatureManager():
    """
    CvFeatureManager Object to interect with Cloudvision
    """
    def __init__(self, authentication: CvpAuthenticationItem):
        """
        __init__ Class Creator

        Parameters
        ----------
        authentication : CvpAuthenticationItem
            Authentication information to use to connect to Cloudvision
        """
        self._authentication = authentication
        # self._cv_instance = CvpClient()
        self._cv_instance = self._connect(authentication=authentication)
        self._cv_images = self.__get_images()
        # self._cv_bundles = self.__get_bundles()

    def _connect(self, authentication: CvpAuthenticationItem):
        """
        _connect Connection management

        Parameters
        ----------
        authentication : CvpAuthenticationItem
            Authentication information to use to connect to Cloudvision

        Returns
        -------
        CvpClient
            cvprac session to cloudvision
        """
        client = CvpClient()
        if authentication.token is not None:
            try:
                client.connect(
                    nodes=[authentication.server],
                    username='',
                    password='',
                    api_token=authentication.token,
                    is_cvaas=True,
                    port=authentication.port,
                    cert=authentication.validate_cert,
                    request_timeout=authentication.timeout
                )
            except CvpLoginError as error_data:
                logger.error(
                    'Cannot connect to Cloudvision server {}'.format(
                        authentication.server
                    )
                )
                logger.debug('Error message: {}'.format(error_data))
        logger.info('connected to Cloudvision server')
        logger.debug('Connection info: {0}'.format(authentication))
        return client

    def __get_images(self):
        """
        __get_images Collect information about images on Cloudvision

        Returns
        -------
        dict
            Fact returned by Cloudvision
        """
        images = []
        logger.debug('  -> Collecting images')
        images = self._cv_instance.api.get_images()['data']
        if self.__check_api_result(images):
            return images
        return None

    def __get_bundles(self):
        """
        __get_bundles [Not In use] Collect information about bundles on Cloudvision

        Returns
        -------
        dict
            Fact returned by Cloudvision
        """
        bundles = []
        logger.debug('  -> Collecting images bundles')
        bundles = self._cv_instance.api.get_image_bundles()['data']
        # bundles = self._cv_instance.post(url='/cvpservice/image/getImageBundles.do?queryparam=&startIndex=0&endIndex=0')['data']
        if self.__check_api_result(bundles):
            return bundles
        return None

    def __check_api_result(self, arg0):
        """
        __check_api_result Check API calls return content

        Parameters
        ----------
        arg0 : any
            Element to test

        Returns
        -------
        bool
            True if data are correct False in other cases
        """
        logger.debug(arg0)
        return len(arg0) > 0

    def _does_image_exist(self, image_name):
        """
        _does_image_exist Check if an image is referenced in Cloudvision facts

        Parameters
        ----------
        image_name : str
            Name of the image to search for

        Returns
        -------
        bool
            True if present
        """
        return any(image_name == image['name'] for image in self._cv_images)

    def _does_bundle_exist(self, bundle_name):
        """
        _does_bundle_exist Check if an image is referenced in Cloudvision facts

        Parameters
        ----------
        bundle_name : str
            Name of the bundle to search for

        Returns
        -------
        bool
            True if present
        """
        # return any(bundle_name == bundle['name'] for bundle in self._cv_bundles)
        return False

    def upload_image(self, image_path: str):
        """
        upload_image Upload an image to Cloudvision server

        Parameters
        ----------
        image_path : str
            Path to the local file to upload

        Returns
        -------
        bool
            True if succeeds
        """
        image_item = Filer(path=image_path)
        if image_item.file_exist is False:
            logger.error('File not found: {}'.format(image_item.relative_path))
            return False
        logger.info('File path for image: {}'.format(image_item))
        if self._does_image_exist(image_name=image_item.filename):
            logger.error("Image found in Cloudvision , Please delete it before running this script")
            return  False
        try:
            upload_result = self._cv_instance.api.add_image(filepath=image_item.absolute_path)
        except Exception as e:
            logger.error('An error occurred during upload, check CV connection')
            logger.error('Exception message is: {}'.format(e))
            return False
        logger.debug('Upload Result is : {}'.format(upload_result))
        return True

    def build_image_list(self, image_list):
        """
        Builds a list of the image data structures, for a given list of image names.
        Parameters
        ----------
        image_list : list
            List of software image names
        Returns
        -------
        List:
            Returns a list of images, with complete data or None in the event of failure
        """
        internal_image_list = []
        image_data = None
        success = True

        for entry in image_list:
            for image in self._cv_images:
                if image["imageFileName"] == entry:
                    image_data = image

            if image_data is not None:
                internal_image_list.append(image_data)
                image_data = None
            else:
                success = False

        if success:
            return internal_image_list
        else:
            return None

    def create_bundle(self, name: str, images_name: List[str]):
        """
        create_bundle Create a bundle with a list of images.

        Parameters
        ----------
        name : str
            Name of the bundle
        images_name : List[str]
            List of images available on Cloudvision

        Returns
        -------
        bool
            True if succeeds
        """
        logger.debug('Init creation of an image bundle {0} with following images {1}'.format(name, str(images_name)))
        all_images_present : List[bool] = []
        self._cv_images = self.__get_images()
        for image_name in images_name:
            all_images_present.append(self._does_image_exist(image_name=image_name))
        # Bundle Create
        if self._does_bundle_exist(bundle_name=name) is False:
            logger.debug('Creating image bundle {0} with following images {1}'.format(name, str(images_name)))
            images_data = self.build_image_list(image_list=images_name)
            if images_data is not None:
                logger.debug('Images information: {0}'.format(images_data))
                try:
                    data = self._cv_instance.api.save_image_bundle(name=name, images=images_data)
                except Exception as e:
                    logger.critical('{0}'.format(e))
                else:
                    logger.debug(data)
                return True
            else:
                logger.critical('No data found for images')
        return False
