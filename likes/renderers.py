import json

from rest_framework import renderers


class LikeRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # start with x's keys and values
        data.update({'success': True})
        return json.dumps(data)
