from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from nuclia.plone.nuclia_api import update_resource
from plone import api

class ReIndex(BrowserView):
    """ Re-index all contents
    """
    index = ViewPageTemplateFile("reindex.pt")
    done = False

    def find_all_files(self):
        indexable_states = api.portal.get_registry_record('nuclia.states', default=['published'])
        portal_catalog = api.portal.get_tool('portal_catalog')
        return portal_catalog(portal_type='File', path={'query': '/'.join(self.context.getPhysicalPath())}, review_state=indexable_states)
    
    def count_all_files(self):
        return len(self.find_all_files())
    
    def reindex_all(self):
        for brain in self.find_all_files():
            obj = brain.getObject()
            update_resource(obj)

    def __call__(self):
        if self.request.method == 'POST':
            self.reindex_all()
            self.done = True
        
        return self.index()