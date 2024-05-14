from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SearchWidget(BrowserView):
    """ Render the search widget
    """
    index = ViewPageTemplateFile("search.pt")
    _kbid = None
    _region = None
    _widget = None

    @property
    def kbid(self):
        if not self._kbid:
            self._kbid = api.portal.get_registry_record('nuclia.knowledgeBox', default=None)
        return self._kbid

    @property
    def region(self):
        if not self._region:
            self._region = api.portal.get_registry_record('nuclia.region', default='europe-1')
        return self._region

    @property
    def widget(self):
        if not self._widget:
            self._widget = api.portal.get_registry_record('nuclia.widget', default='')
        return self._widget

    def __call__(self):
        return self.index()