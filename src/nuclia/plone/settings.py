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
        default=u"europe-1"
    )
    widget = schema.Text(
        title=u"Widget snippet",
        default=u"",
        required=False,
    )
    target_folders = schema.List(
        value_type=schema.TextLine(),
        title=u"Target folders",
        description=u"List of folder pathes to index",
        default=[],
        required=False,
    )
    file_field = schema.TextLine(
        title=u"File field",
        description=u"Name of the field containing the file to index",
        default=u"file"
    )
    title_field = schema.TextLine(
        title=u"Title field",
        description=u"Name of the field containing the title to index",
        default=u"title"
    )
    description_field = schema.TextLine(
        title=u"Description field",
        description=u"Name of the field containing the description to index",
        default=u"description",
        required=False,
    )
    tags_field = schema.List(
        value_type=schema.TextLine(),
        title=u"Tags fields",
        description=u"List of fields containing tags to index",
        default=[u"subject"],
        required=False,
    )
    created_field = schema.TextLine(
        title=u"Created date field",
        description=u"Name of the field containing the Created date to index",
        default=u"creation_date",
        required=False,
    )
    modified_field = schema.TextLine(
        title=u"Modified date field",
        description=u"Name of the field containing the modified date to index",
        default=u"modification_date",
        required=False,
    )
    collaborators_field = schema.TextLine(
        title=u"Collaborators date field",
        description=u"Name of the field containing the collaborators date to index",
        default=u"contributors",
        required=False,
    )
    states = schema.List(
        value_type=schema.TextLine(),
        title=u"Worfklow states",
        description=u"Worfklow states triggering the indexation",
        default=[u"published"],
    )

class SettingsEditForm(RegistryEditForm):
    schema = ISettings
    label = u"Nuclia settings"
    schema_prefix = "nuclia"

class NucliaSettingsControlPanel(ControlPanelFormWrapper):
    form = SettingsEditForm