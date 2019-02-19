import json

from rest_framework import renderers


class UserRelationsRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        from rest_framework.exceptions import ErrorDetail
        if data.get('results', None) is not None:
            return json.dumps({
                'success': True,
                'data': {
                    # 'page_meta': meta_data.data,
                    'page_meta': renderer_context['page_meta'].get_data(),
                    'following': data['results'][0]['following'],
                    'followers': data['results'][0]['followers'],
                    # self.pagination_count_label: data['count']
                }
            })

            # If the view throws an error (such as the user can't be authenticated
            # or something similar), `data` will contain an `errors` key. We want
            # the default JSONRenderer to handle rendering errors, so we need to
            # check for this case.
        elif data.get('errors', None) is not None:
            return super(UserRelationsRenderer, self).render(data)
        elif type(data.get('detail')) == ErrorDetail:
            return json.dumps({'success': False, 'full_messages': [data.get('detail')]})
        else:
            return json.dumps({'success': True, 'data': data})
