from nameko.rpc import rpc
from temp_messenger.dependencies.redis import Redis


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
        return self.redis.get_all_messages()
