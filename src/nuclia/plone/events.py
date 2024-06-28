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
    target_folders = api.portal.get_registry_record('nuclia.target_folders', default=[])
    object_path = object.absolute_url_path()
    return api.content.get_state(obj=object, default='published') in indexable_states and (len(target_folders) == 0 or any([object_path.startswith(path) for path in target_folders]))
