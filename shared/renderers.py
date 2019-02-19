import re

import rest_framework
from rest_framework import renderers
import json

from shared.models import PageMetaModel, PageMetaModel2
from shared.serializers import PageMetaSerializer, PageMetaModelSerializer

# https://gist.github.com/vbabiy/5842073

_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camelcase_to_underscore(word):
    s1 = _first_cap_re.sub(r'\1_\2', word)
    return _all_cap_re.sub(r'\1_\2', s1).lower()


def recursive_key_map(function, obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            if isinstance(key, str):
                key = function(key)
            new_dict[key] = recursive_key_map(function, value)
        return new_dict
    if hasattr(obj, '__iter__'):
        return [recursive_key_map(function, value) for value in obj]
    else:
        return obj


class AppJsonRenderer(renderers.JSONRenderer):
    charset = 'utf-8'
    pagination_object_label = 'objects'
    pagination_object_count = 'count'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # What we get here is the Response.data, for paginated results we will have a results field
        from rest_framework.exceptions import ErrorDetail
        if data.get('results', None) is not None:
            # data = recursive_key_map(camelcase_to_underscore, data.get('results'))
            meta_data = PageMetaSerializer(data=data, context=renderer_context)

            # model = PageMetaModel(next_page_url='cool')
            # meta_data = PageMetaModelSerializer(data=model, context=renderer_context)
            meta_data.is_valid()

            return json.dumps({
                'success': True,
                'data': {
                    # 'page_meta': meta_data.data,
                    'page_meta': renderer_context['page_meta'].get_data(),
                    self.pagination_object_label: data['results'],
                    # self.pagination_count_label: data['count']
                }
            })

            # If the view throws an error (such as the user can't be authenticated
            # or something similar), `data` will contain an `errors` key. We want
            # the default JSONRenderer to handle rendering errors, so we need to
            # check for this case.
        elif data.get('errors', None) is not None:
            return super(AppJsonRenderer, self).render(data)
        elif type(data.get('detail')) == ErrorDetail:
            return json.dumps({'success': False, 'full_messages': [data.get('detail')]})
        else:
            return json.dumps({'success': True, 'data': data})
