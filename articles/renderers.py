from shared.renderers import AppJsonRenderer


class ArticleListJsonRenderer(AppJsonRenderer):

    def get_count_name(self):
        return 'articles_count'

    def get_object_type_name(self):
        return 'articles'


class ArticleJSONRenderer(AppJsonRenderer):
    object_label = 'article'
    pagination_object_label = 'articles'
    pagination_count_label = 'articles_count'
