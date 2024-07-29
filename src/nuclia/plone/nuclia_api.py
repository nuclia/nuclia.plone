from nuclia.plone import MD5_ANNOTATION, get_field_mapping, logger, get_kb_path, get_headers
import requests
import hashlib
from base64 import b64encode
from plone import api
from zope.annotation.interfaces import IAnnotations

def get_attribute_value(object, attr, default=None):
    if attr.startswith('parent/'):
        return get_attribute_value(object.getParentNode(), attr[7:], default)
    return getattr(object, attr, default)

def flatten_tags(object, attrs):
    tags = []
    for attr in attrs:
        value = get_attribute_value(object, attr, None)
        if value:
            if isinstance(value, (list, tuple)):
                tags.extend([u"{attr}/{v}".format(attr=attr, v=v) for v in value if v])
            else:
                tags.append(u"{attr}/{value}".format(attr=attr, value=value))
    return tags

def get_date(object, field):
    date = get_attribute_value(object, field, None)
    if not date:
        return None
    return date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def get_data(object):
    mapping = get_field_mapping()
    return {
        'file': get_attribute_value(object, mapping['file'], None),
        'title': get_attribute_value(object, mapping['title'], None),
        'summary': get_attribute_value(object, mapping['summary'], None),
        'tags': flatten_tags(object, mapping['tags']),
        'created': get_date(object, mapping['created']),
        'modified': get_date(object, mapping['modified']),
        'collaborators': get_attribute_value(object, mapping['collaborators'], None),
    }
    

def upload_to_new_resource(object):
    data = get_data(object)
    file = data.get('file', None)
    annotations = IAnnotations(object)
    if file:
        uuid = api.content.get_uuid(obj=object)
        response = requests.post(
            "{path}/resources".format(path=get_kb_path()),
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
                logger.error('Error creating resource')
                logger.error(response.text)
                return
        response = upload_file(uuid, file)
        if response:
            annotations[MD5_ANNOTATION] = hashlib.md5(file.data).hexdigest()

def upload_file(uuid, file):
    filename = getattr(file, "filename", None).encode('utf-8').decode('ascii','ignore')
    if not filename:
        return
    content_type = file.contentType
    headers = get_headers()
    headers.update({
        "content-type": content_type,
        "x-filename": filename,
    })
    response = requests.post(
        "{path}/slug/{uuid}/file/file/upload".format(path=get_kb_path(), uuid=uuid),
        headers=headers,
        data=file.data,
        verify=False,
    )
    if not response.ok:
        logger.error('Error uploading file')
        logger.error(response.text)
        return None
    else:
        return response

def update_resource(object):
    annotations = IAnnotations(object)
    data = get_data(object)
    file = data.get('file', None)
    must_update_file = True
    if not file:
        return
    uuid = api.content.get_uuid(obj=object)
    fields = {}
    response = requests.get(
        "{path}/slug/{uuid}?show=basic&show=values&show=extracted&extracted=file".format(path=get_kb_path(), uuid=uuid),
        headers=get_headers()
    )
    if not response.ok:
        if response.status_code == 404:
            upload_to_new_resource(object)
            return
        else:
            logger.error('Error getting resource')
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
        "{path}/slug/{uuid}".format(path=get_kb_path(), uuid=uuid),
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
        "{path}/slug/{uuid}".format(path=get_kb_path(), uuid=uuid),
        headers=get_headers()
    )
    if not response.ok:
        logger.error('Error deleting resource')
        logger.error(response.text)

def delete_file_field(resource):
    response = requests.delete(
        "{path}/slug/{resource}/file/file".format(path=get_kb_path(), resource=resource),
        headers=get_headers()
    )
    if not response.ok:
        logger.error('Error deleting field')
        logger.error(response.text)