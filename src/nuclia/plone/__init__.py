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
    return f"https://{region}.nuclia.cloud/api/v1/kb/{kbid}"

def get_headers():
    api_key = api.portal.get_registry_record('nuclia.apiKey', default=None)
    return {"X-STF-Serviceaccount": f"Bearer {api_key}"}