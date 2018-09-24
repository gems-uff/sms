from flask import render_template


HANDLED_ERRORS = [403, 404, 500]


def get_handler(status_code):
    template_path = f'errors/{status_code}.html'

    def handle_status_code(_):
        return (render_template(template_path), status_code)

    return handle_status_code


def register_error_handlers(app):
    '''
    Register error handlers for specific status codes.

    To add a new error handler, create the file:
    `errors/<status_code>.html`
    and add <status_code> in `HANDLED_ERRORS` list.
    '''
    for status_code in HANDLED_ERRORS:
        app.register_error_handler(status_code, get_handler(status_code))
