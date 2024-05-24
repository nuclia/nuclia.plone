# -*- coding: utf-8 -*-
"""Init and utils."""
import logging
from zope.i18nmessageid import MessageFactory
from plone import api


_ = MessageFactory('nuclia.plone')

logger = logging.getLogger(name="nuclia")
MD5_ANNOTATION = "nuclia.plone.md5"

def get_kb_path():
    kbid = api.portal.get_registry_record('nuclia.knowledgeBox', default=None)
    region = api.portal.get_registry_record('nuclia.region', default='europe-1')
    return "https://{region}.nuclia.cloud/api/v1/kb/{kbid}".format(region=region, kbid=kbid)

def get_headers():
    api_key = api.portal.get_registry_record('nuclia.apiKey', default=None)
    return {"X-STF-Serviceaccount": "Bearer {api_key}".format(api_key=api_key)}

def get_field_mapping():
    return {
        'file': api.portal.get_registry_record('nuclia.file_field', default='file'),
        'title': api.portal.get_registry_record('nuclia.title_field', default='title'),
        'summary': api.portal.get_registry_record('nuclia.description_field', default='description'),
        'tags': api.portal.get_registry_record('nuclia.tags_field', default=['subject']),
        'created': api.portal.get_registry_record('nuclia.created_field', default='creation_date'),
        'modified': api.portal.get_registry_record('nuclia.modified_field', default='modification_date'),
        'collaborators': api.portal.get_registry_record('nuclia.collaborators_field', default='contributors'),
    }