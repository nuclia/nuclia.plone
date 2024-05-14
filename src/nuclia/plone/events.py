from .nuclia_api import unindex_object, update_resource, upload_to_new_resource
from plone import api


def on_create(object, event):
    if is_public(object):
        upload_to_new_resource(object)

def on_modify(object, event):
    if not is_public(object):
        return
    update_resource(object)

def on_delete(object, event):
    if is_public(object):
        unindex_object(object)

def on_state_change(object, event):
    if is_public(object):
        upload_to_new_resource(object)
    else:
        unindex_object(object)

def is_public(object):
    return api.content.get_state(obj=object, default='published') == 'published'
