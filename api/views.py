import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .handlers import get_main_handler
from django.conf import settings
from telegram import Update
from .model_utils import *

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


@api_view(http_method_names=['POST'])
def add_table(request):
    """
    Add a table.
    :param request:
    :return:
    """
    data = request.data
    table = Table()
    table.can_join = data['can_join']
    table.size = data['capacity']
    table.type = data['type']
    table.put()
    return Response('table added')


@api_view(http_method_names=['POST'])
def add_dummy_reservation(request):
    """
    Add dummy reservation.
    :param request:
    :return:
    """
    data = request.data
    reservation = TableReservation(
        start_time=datetime.datetime.now().replace(day=data['start_day'], hour=data['start_hour'],
                                                   minute=data['start_minute']),
        end_time=datetime.datetime.now().replace(day=data['end_day'], hour=data['end_hour'],
                                                 minute=data['end_minute']),
        table=1
    )
    reservation.put()
    return Response(data='done')


@api_view(http_method_names=['POST'])
def check_table_avaialbility(request):
    """
    Check if table is available.
    :param request:
    :return:
    """
    data = request.data
    start_time = datetime.datetime.now().replace(day=data['start_day'], hour=data['start_hour'],
                                                 minute=data['start_minute'])
    end_time = datetime.datetime.now().replace(day=data['end_day'], hour=data['end_hour'], minute=data['end_minute'])
    if get_vacant_tables(start_time, end_time):
        return Response('yes')
    else:
        return Response('no')
