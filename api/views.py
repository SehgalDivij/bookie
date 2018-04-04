import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .handlers import get_main_handler
from django.conf import settings
from telegram import Update

logger = logging.getLogger(__name__)

print(settings.TELEGRAM_TOKEN)
print('printing settings.')
print(vars(settings))
bot = settings.BOT
dispatcher = settings.DISPATCHER


@api_view(http_method_names=['GET', 'POST'])
def bookie_hook(request):
    """
    Base url to replace index call.
    :param request:
    :return:
    """
    bot_update = request.data
    logger.debug(bot_update)
    # decode webhook update object here.
    update = Update.de_json(bot_update, bot)
    dispatcher.process_update(update)
    dispatcher.add_handler(get_main_handler())
    logger.debug(bot_update)
    return Response(
        data={
            "data_received": bot_update
        },
        status=status.HTTP_200_OK
    )
