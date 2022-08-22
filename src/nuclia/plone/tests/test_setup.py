# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from nuclia.plone.testing import NUCLIA_PLONE_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that nuclia.plone is properly installed."""

    layer = NUCLIA_PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if nuclia.plone is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'nuclia.plone'))

    def test_browserlayer(self):
        """Test that INucliaPloneLayer is registered."""
        from nuclia.plone.interfaces import (
            INucliaPloneLayer)
        from plone.browserlayer import utils
        self.assertIn(
            INucliaPloneLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = NUCLIA_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('nuclia.plone')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if nuclia.plone is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'nuclia.plone'))

    def test_browserlayer_removed(self):
        """Test that INucliaPloneLayer is removed."""
        from nuclia.plone.interfaces import \
            INucliaPloneLayer
        from plone.browserlayer import utils
        self.assertNotIn(INucliaPloneLayer, utils.registered_layers())
