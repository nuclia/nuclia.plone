from nuclia.plone import MD5_ANNOTATION, get_field_mapping, logger, get_kb_path, get_headers
import requests
import hashlib
from base64 import b64encode
from plone import api
from zope.annotation.interfaces import IAnnotations

def flatten_tags(object, attrs):
    tags = []
    for attr in attrs:
        value = getattr(object, attr, None)
        if value:
            if isinstance(value, (list, tuple)):
                tags.extend([f"{attr}/{v}" for v in value if v])
            else:
                tags.append(f"{attr}/{value}")
    return tags

def get_date(object, field):
    date = getattr(object, field, None)
    if not date:
        return None
    return date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def get_data(object):
    mapping = get_field_mapping()
    return {
        'file': getattr(object, mapping['file'], None),
        'title': getattr(object, mapping['title'], None),
        'summary': getattr(object, mapping['summary'], None),
        'tags': flatten_tags(object, mapping['tags']),
        'created': get_date(object, mapping['created']),
        'modified': get_date(object, mapping['modified']),
        'collaborators': getattr(object, mapping['collaborators'], None),
    }
    

def upload_to_new_resource(object):
    data = get_data(object)
    file = data.get('file', None)
    annotations = IAnnotations(object)
    if file:
        uuid = api.content.get_uuid(obj=object)
        response = requests.post(
            f"{get_kb_path()}/resources",
            headers=get_headers(),
            json={
                "slug": uuid,
                "title": data.get('title', None),
                "summary": data.get('summary', None),
                "origin": {
                    "created": data.get('created', None),
                    "modified": data.get('modified', None),
                    "collaborators": data.get('collaborators', None),
                    "tags": data.get('tags', None),
                    "url": object.absolute_url(),
                    "path": object.absolute_url_path(),
                }
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
    must_update_file = True
    if not file:
        return
    uuid = api.content.get_uuid(obj=object)
    fields = {}
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
    fields = response.json()['data']
    files = fields.get('files', None)
    if files and 'file' in files:
        previous_md5 = annotations.get(MD5_ANNOTATION, None)
        current_md5 = hashlib.md5(file.data).hexdigest()
        if previous_md5 == current_md5:
            must_update_file = False
        else:
            delete_file_field(uuid)

    if must_update_file:
        response = upload_file(uuid, file)
        if response:
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()
    
    data = get_data(object)
    response = requests.patch(
        f"{get_kb_path()}/slug/{uuid}",
        headers=get_headers(),
        json={
            "title": data.get('title', None),
            "summary": data.get('summary', None),
            "origin": {
                "created": data.get('created', None),
                "modified": data.get('modified', None),
                "collaborators": data.get('collaborators', None),
                "tags": data.get('tags', None),
                "url": object.absolute_url(),
                "path": object.absolute_url_path(),
            }
        },
    )

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