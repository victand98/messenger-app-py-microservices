import json
from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http
from temp_messenger.dependencies.redis import Redis
from temp_messenger.dependencies.jinja2 import Jinja2
from werkzeug.wrappers import Response


class MessageService:
    name = 'message_service'
    redis = Redis('redis')

    @rpc
    def get_message(self, message_id):
        return self.redis.get_message(message_id)

    @rpc
    def set_message(self, message):
        message_id = self.redis.set_message(message)
        return message_id

    @rpc
    def get_all_messages(self):
        messages = self.redis.get_all_messages()
        sorted_messages = sort_messages(messages)
        return sorted_messages


class HttpService:
    name = 'http_service'
    message_service = RpcProxy('message_service')
    templates = Jinja2()

    @http('GET', '/')
    def home(self, request):
        messages = self.message_service.get_all_messages()
        rendered_template = self.templates.render_home(messages)
        html_response = create_html_response(rendered_template)
        return html_response

    @http('POST', '/messages')
    def post_message(self, request):
        try:
            data = get_request_data(request)
        except json.JSONDecodeError:
            return 400, 'Invalid JSON'

        try:
            message = data['message']
        except KeyError:
            return 400, 'Missing message'

        self.message_service.set_message(message)
        return 204, 'Message created'

    @http('GET', '/messages')
    def get_messages(self, request):
        messages = self.message_service.get_all_messages()
        return create_json_response(messages)


def create_html_response(rendered_template):
    headers = {'Content-Type': 'text/html'}
    return Response(rendered_template, status=200, headers=headers)


def get_request_data(request):
    return json.loads(request.get_data(as_text=True))


def sort_messages(messages, reverse=True):
    return sorted(messages, key=lambda m: m['expires_in'], reverse=reverse)


def create_json_response(data):
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    return Response(json_data, status=200, headers=headers)
