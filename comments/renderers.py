from shared.renderers import AppJsonRenderer


class CommentJsonRenderer(AppJsonRenderer):
    object_label = 'comment'
    pagination_object_label = 'comments'
    pagination_count_label = 'comments_count'

    def get_object_type_name(self):
        return 'comments'

    def get_count_name(self):
        return 'comments_count'
