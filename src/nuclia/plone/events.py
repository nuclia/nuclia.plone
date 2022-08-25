import logging
import requests
import hashlib
from base64 import b64encode
from plone import api
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger(name="plone.app.contenttypes upgrade")
UID_ANNOTATION = "nuclia.plone.uid"
FIELD_ID_ANNOTATION = "nuclia.plone.fieldid"

def on_create(object, event):
    upload_to_new_resource(object)

def on_modify(object, event):
    # uid = object.UID()
    # title = object.title
    # body = object.text.raw
    annotations = IAnnotations(object)
    resource = annotations.get(UID_ANNOTATION)
    if not resource:
        upload_to_new_resource(object)
    else:
        update_file(object)

def on_delete(object, event):
    annotations = IAnnotations(object)
    resource = annotations.get(UID_ANNOTATION)
    if resource:
        response = requests.delete(
            f"{get_kb_path()}/resource/{resource}",
            headers=get_headers()
        )
        if not response.ok:
            logger.error(f'Error deleting resource')

def upload_to_new_resource(object):
    file = getattr(object, 'file', None)
    if file:
        response = upload_file(f"{get_kb_path()}/upload", file)
        if response:
            annotations = IAnnotations(object)
            resource = response.headers['ndb-resource'].split('/')[-1]
            annotations[UID_ANNOTATION] = resource
            field = response.headers['ndb-field'].split('/')[-1]
            annotations[FIELD_ID_ANNOTATION] = field

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
        return None
    else:
        return response

def update_file(object):
    annotations = IAnnotations(object)
    file = getattr(object, 'file', None)
    if not file:
        return
    resource = annotations.get(UID_ANNOTATION)
    data = {}
    if resource:
        response = requests.get(
            f"{get_kb_path()}/resource/{resource}?show=basic&show=extracted&extracted=file",
            headers=get_headers()
        )
        if not response.ok:
            logger.error(f'Error getting resource')
        data = response.json()['data']
    files = data.get('files', None)
    field_id = annotations.get(FIELD_ID_ANNOTATION, None)
    if files and field_id and field_id in files:
        previous_md5 = files[field_id]['extracted']['file']['md5']
        current_md5 = hashlib.md5(file.data).hexdigest()
        if previous_md5 == current_md5:
            return
        else:
            delete_field(resource, 'file', field_id, annotations)

    response = upload_file(f"{get_kb_path()}/resource/{resource}/file/file1/upload", file)
    if response:
        field = response.headers['ndb-field'].split('/')[-1]
        annotations[FIELD_ID_ANNOTATION] = field

def delete_field(resource, field_type, field_id, annotations):
    response = requests.delete(
        f"{get_kb_path()}/resource/{resource}/{field_type}/{field_id}",
        headers=get_headers()
    )
    if not response.ok:
        logger.error(f'Error deleting field')
    else:
        del annotations[FIELD_ID_ANNOTATION]

def get_kb_path():
    kbid = api.portal.get_registry_record('nuclia.knowledgeBox', default=None)
    return f"https://europe-1.stashify.cloud/api/v1/kb/{kbid}"

def get_headers():
    api_key = api.portal.get_registry_record('nuclia.apiKey', default=None)
    return {"X-STF-Serviceaccount": f"Bearer {api_key}"}