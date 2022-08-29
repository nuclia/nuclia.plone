from email import header
import logging
import requests
import hashlib
from base64 import b64encode
from plone import api
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger(name="plone.app.contenttypes upgrade")
UID_ANNOTATION = "nuclia.plone.uid"
FIELD_ID_ANNOTATION = "nuclia.plone.fieldid"
MD5_ANNOTATION = "nuclia.plone.md5"

def on_create(object, event):
    if is_public(object):
        upload_to_new_resource(object)

def on_modify(object, event):
    # body = object.text.raw
    if not is_public(object):
        return
    annotations = IAnnotations(object)
    resource = annotations.get(UID_ANNOTATION)
    if not resource:
        upload_to_new_resource(object)
    else:
        update_resource(object)

def on_delete(object, event):
    if is_public(object):
        unindex_object(object)

def on_state_change(object, event):
    if is_public(object):
        upload_to_new_resource(object)
    else:
        unindex_object(object)

def upload_to_new_resource(object):
    file = getattr(object, 'file', None)
    remoteUrl = getattr(object, 'remoteUrl', None)
    annotations = IAnnotations(object)
    if file:
        response = upload_file(f"{get_kb_path()}/upload", file)
        if response:
            resource = response.headers['ndb-resource'].split('/')[-1]
            annotations[UID_ANNOTATION] = resource
            field = response.headers['ndb-field'].split('/')[-1]
            annotations[FIELD_ID_ANNOTATION] = field
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()
    elif remoteUrl:
        response = requests.post(
            f"{get_kb_path()}/resources",
            headers=get_headers(),
            json={
                "links": {"link": { "uri": remoteUrl }},
                "title": object.title,
                "icon": 'application/stf-link',
            },
        )
        if not response.ok:
            logger.error(f'Error creating link resource')
            logger.error(response.text)
        else:
            resource = response.json()['uuid']
            annotations[UID_ANNOTATION] = resource

def upload_file(path, file):
    filename = file.filename
    content_type = file.contentType
    headers = get_headers()
    headers.update({
        "content-type": content_type,
        "x-filename": b64encode(filename.encode('ascii')).decode('ascii'),
    })
    response = requests.post(
        path,
        headers=headers,
        data=file.data,
        verify=False,
    )
    if not response.ok:
        logger.error(f'Error uploading file')
        logger.error(response.text)
        return None
    else:
        return response

def update_resource(object):
    annotations = IAnnotations(object)
    file = getattr(object, 'file', None)
    remoteUrl = getattr(object, 'remoteUrl', None)
    if not file and not remoteUrl:
        return
    resource = annotations.get(UID_ANNOTATION)
    data = {}
    if resource:
        response = requests.get(
            f"{get_kb_path()}/resource/{resource}?show=basic&show=values&show=extracted&extracted=file&extracted=link",
            headers=get_headers()
        )
        if not response.ok:
            logger.error(f'Error getting resource')
            logger.error(response.text)
        data = response.json()['data']
    files = data.get('files', None)
    links = data.get('links', None)
    field_id = annotations.get(FIELD_ID_ANNOTATION, None)
    if files and field_id and field_id in files:
        previous_md5 = annotations.get(MD5_ANNOTATION, None)
        current_md5 = hashlib.md5(file.data).hexdigest()
        if previous_md5 == current_md5:
            return
        else:
            delete_field(resource, 'file', field_id, annotations)
    if links and 'link' in links and links['link']['value']['uri'] != remoteUrl:
        delete_field(resource, 'link', 'link', annotations)

    if file:
        response = upload_file(f"{get_kb_path()}/resource/{resource}/file/file1/upload", file)
        if response:
            field = response.headers['ndb-field'].split('/')[-1]
            annotations[FIELD_ID_ANNOTATION] = field
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()
    if remoteUrl:
        response = requests.patch(
            f"{get_kb_path()}/resource/{resource}",
            headers=get_headers(),
            json={
                "links": {"link": { "uri": remoteUrl }},
                "title": object.title,
            },
        )
        if not response.ok:
            logger.error(f'Error updating link')
            logger.error(response.text)

def unindex_object(object):
    annotations = IAnnotations(object)
    resource = annotations.get(UID_ANNOTATION)
    if resource:
        response = requests.delete(
            f"{get_kb_path()}/resource/{resource}",
            headers=get_headers()
        )
        if not response.ok:
            logger.error(f'Error deleting resource')
            logger.error(response.text)

def delete_field(resource, field_type, field_id, annotations):
    response = requests.delete(
        f"{get_kb_path()}/resource/{resource}/{field_type}/{field_id}",
        headers=get_headers()
    )
    if not response.ok:
        logger.error(f'Error deleting field')
        logger.error(response.text)
    else:
        del annotations[FIELD_ID_ANNOTATION]

def get_kb_path():
    kbid = api.portal.get_registry_record('nuclia.knowledgeBox', default=None)
    region = api.portal.get_registry_record('nuclia.region', default='europe-1')
    return f"https://{region}.nuclia.cloud/api/v1/kb/{kbid}"

def get_headers():
    api_key = api.portal.get_registry_record('nuclia.apiKey', default=None)
    return {"X-STF-Serviceaccount": f"Bearer {api_key}"}

def is_public(object):
    return api.content.get_state(object) == 'published'
