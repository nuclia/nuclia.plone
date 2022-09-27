
from plone import api
from Products.Five.browser import BrowserView
from nuclia.plone import UID_ANNOTATION, logger, get_kb_path, get_headers
import requests
from zope.annotation.interfaces import IAnnotations
from plone.app.textfield import RichTextValue


class ExtractText(BrowserView):
    """ Extract text from Nuclia resource
    """
    
    def __call__(self):
        data = get_resource(self.context, 'text')
        if data:
            texts = []
            for field_type in data.values():
                for field in field_type.values():
                    if 'extracted' in field and 'text' in field['extracted']:
                        texts.append(field['extracted']['text'].get('text', '').replace('\n', '<br/>'))
            container = self.context
            if not container.isPrincipiaFolderish:
                container = container.getParentNode()
            transcript = api.content.create(
                type='Document',
                title=f"{self.context.title} – Transcript",
                container=container,
                text=RichTextValue('<br/>'.join(texts), 'text/html', 'text/x-html-safe'),
            )
            self.request.response.redirect(transcript.absolute_url())
            
        return None


class ExtractKeywords(BrowserView):
    """ Extract keywords from Nuclia resource
    """
    
    def __call__(self):
        data = get_resource(self.context, 'metadata')
        if data:
            keywords = []
            for field_type in data.values():
                for field in field_type.values():
                    if 'extracted' in field and 'metadata' in field['extracted']:
                        keywords += [f"{item[1]} | {item[0]}" for item in field['extracted']['metadata']['metadata']['ner'].items()]
            if len(keywords) > 0:
                self.context.subject = keywords
                self.request.response.redirect(self.context.absolute_url())
            
        return None


def get_resource(context, mode):
    annotations = IAnnotations(context)
    resource = annotations.get(UID_ANNOTATION)
    if resource:
        response = requests.get(
            f"{get_kb_path()}/resource/{resource}?show=extracted&show=errors&extracted={mode}",
            headers=get_headers()
        )
        if not response.ok:
            logger.error(f'Error getting resource')
            logger.error(response.text)
        return response.json().get('data', None)
    return None