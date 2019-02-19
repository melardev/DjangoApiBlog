from shared.renderers import AppJsonRenderer


class UserJsonRenderer(AppJsonRenderer):
    object_label = 'user'
    pagination_object_label = 'users'
