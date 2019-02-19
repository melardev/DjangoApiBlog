from rest_framework.views import exception_handler


def app_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {'success': False, 'errors': response.data}
        full_messages = []
        for value in list(exc.detail.items()):
            if type(value) == str:
                full_messages.append(value)
            elif type(value) == tuple:
                full_messages.append('%s -> %s' % (value[0], str(value[1][0])))
        response.data['full_messages'] = full_messages
    return response
