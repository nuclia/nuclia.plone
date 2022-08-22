# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import nuclia.plone


class NucliaPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=nuclia.plone)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'nuclia.plone:default')


NUCLIA_PLONE_FIXTURE = NucliaPloneLayer()


NUCLIA_PLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NUCLIA_PLONE_FIXTURE,),
    name='NucliaPloneLayer:IntegrationTesting',
)


NUCLIA_PLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NUCLIA_PLONE_FIXTURE,),
    name='NucliaPloneLayer:FunctionalTesting',
)


NUCLIA_PLONE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        NUCLIA_PLONE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='NucliaPloneLayer:AcceptanceTesting',
)
