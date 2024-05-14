from nuclia.plone import MD5_ANNOTATION, logger, get_kb_path, get_headers
import requests
import hashlib
from base64 import b64encode
from plone import api
from zope.annotation.interfaces import IAnnotations

def upload_to_new_resource(object):
    file = getattr(object, 'file', None)
    annotations = IAnnotations(object)
    if file:
        uuid = api.content.get_uuid(obj=object)
        response = requests.post(
            f"{get_kb_path()}/resources",
            headers=get_headers(),
            json={
                "slug": uuid,
                "title": object.title,
            },
        )
        if not response.ok:
            if response.status_code == 409:
                update_resource(object)
                return
            else:
                logger.error(f'Error creating resource')
                logger.error(response.text)
                return
        response = upload_file(uuid, file)
        if response:
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()

def upload_file(uuid, file):
    filename = getattr(file, "filename", None)
    if not filename:
        return
    content_type = file.contentType
    headers = get_headers()
    headers.update({
        "content-type": content_type,
        "x-filename": b64encode(filename.encode()).decode(),
    })
    response = requests.post(
        f"{get_kb_path()}/slug/{uuid}/file/file/upload",
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
    if not file:
        return
    uuid = api.content.get_uuid(obj=object)
    data = {}
    response = requests.get(
        f"{get_kb_path()}/slug/{uuid}?show=basic&show=values&show=extracted&extracted=file",
        headers=get_headers()
    )
    if not response.ok:
        if response.status_code == 404:
            upload_to_new_resource(object)
            return
        else:
            logger.error(f'Error getting resource')
            logger.error(response.text)
            return
    data = response.json()['data']
    files = data.get('files', None)
    if files and 'file' in files:
        previous_md5 = annotations.get(MD5_ANNOTATION, None)
        current_md5 = hashlib.md5(file.data).hexdigest()
        if previous_md5 == current_md5:
            return
        else:
            delete_file_field(uuid)

    if file:
        response = upload_file(uuid, file)
        if response:
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()

def unindex_object(object):
    uuid = api.content.get_uuid(obj=object)
    response = requests.delete(
        f"{get_kb_path()}/slug/{uuid}",
        headers=get_headers()
    )
    if not response.ok:
        logger.error(f'Error deleting resource')
        logger.error(response.text)

def delete_file_field(resource):
    response = requests.delete(
        f"{get_kb_path()}/slug/{resource}/file/file",
        headers=get_headers()
    )
    if not response.ok:
        logger.error(f'Error deleting field')
        logger.error(response.text)