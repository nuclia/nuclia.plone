from .nuclia_api import unindex_object, update_resource, upload_to_new_resource
from plone import api

def on_create(object, event):
    if is_indexable(object):
        upload_to_new_resource(object)

def on_modify(object, event):
    if not is_indexable(object):
        return
    update_resource(object)

def on_delete(object, event):
    if is_indexable(object):
        unindex_object(object)

def on_state_change(object, event):
    if is_indexable(object):
        upload_to_new_resource(object)
    else:
        unindex_object(object)

def is_indexable(object):
    indexable_states = api.portal.get_registry_record('nuclia.states', default=['published'])
    return api.content.get_state(obj=object, default='published') in indexable_states
