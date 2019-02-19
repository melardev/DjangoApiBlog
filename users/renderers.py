import json

from shared.renderers import AppJsonRenderer


class JsonLoginRenderer(AppJsonRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # In stack ow they call super after putting the token in data
        # It should work before as well,
        username = data.get('username', None)
        to_render = {}
        if username is None:
            to_render['success'] = False
            errors = data.get('non_field_errors', None)
            if errors is not None:
                to_render['full_messages'] = errors
        else:
            to_render['success'] = True
            to_render['user'] = {'id': data.get('id'), 'username': data.get('username'), 'email': data.get('email'),
                                 'token': data.get('token'), 'roles': data.get('roles', None)}
        return json.dumps(to_render)
