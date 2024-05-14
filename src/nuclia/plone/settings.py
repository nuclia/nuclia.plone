from zope import schema
from zope.interface import Interface

from plone.z3cform import layout
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

class ISettings(Interface):
    knowledgeBox = schema.TextLine(
        title=u"Knowledge Box",
        description=u"Unique identifier for the knowledge box",
    )
    apiKey = schema.TextLine(
        title=u"API key",
        description=u"Nuclia API key with contributor access",
    )
    region = schema.TextLine(
        title=u"Region",
        description=u"Processing zone",
        default="europe-1"
    )
    widget = schema.Text(
        title=u"Widget snippet",
        default=""
    )

class SettingsEditForm(RegistryEditForm):
    schema = ISettings
    label = u"Nuclia settings"
    schema_prefix = "nuclia"

class NucliaSettingsControlPanel(ControlPanelFormWrapper):
    form = SettingsEditForm