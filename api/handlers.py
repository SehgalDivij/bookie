import logging

import datetime
from time import sleep

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
from django.conf import settings

from api.model_utils import make_reservation
from api.ndb_models import Table, User
from api.utils import add_to_cache, fetch_from_cache, update_cache
from . import telegramcalendar

logger = logging.getLogger(__name__)


# def start(bot, update):
#     """
#     Callback to handle start command.
#     changes bot state to accept day input.
#     resulting state: INPUT_DAY
#     """
#     reply_keyboard = [
#         ['Today'],
#         ['Tomorrow'],
#         ['Other']
#     ]
#     update.message.reply_text(
#         text='Hi! So you\'ve decided to come visit the Bistro. I\'m thrilled. \n'
#              'Let me help get you a table. \n'
#              'When do you visit?',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard,
#             one_time_keyboard=True
#         )
#     )
#     # change bot state to accept day of visit as input.
#     return settings.INPUT_DAY

def is_booking_active(func):
    """
    Check if a booking is ongoing for a user.
    Checks presence of an object by user's chat id in the cache. If an object is present, use it. Else return whether
    to proceed with booking or not.
    :param func:
    :return:
    """

    def wrapper(bot, update):
        """
        Check return the passed function if linked chat_id is currently in cache.
        Else, return cancel message and take system to raw state.
        :param bot:
        :param update:
        :return:
        """
        chat_id = None
        print(type(update))
        print(update)
        if update.message is not None:
            print('got message')
            chat_id = update.message.chat.id
        elif update.callback_query is not None:
            print('update using callback_query')
            chat_id = update.callback_query.from_user.id
        else:
            print('got nothing')
        print('Found chat id: ' + str(chat_id))
        u_info = fetch_from_cache(chat_id=chat_id)
        if u_info is not None:
            return func(bot, update)
        else:
            return conversation_expired(bot, update)

    return wrapper


def start(bot, update):
    """
    Callback to handle start command.
    changes bot state to accept day input.
    resulting state: INPUT_DAY
    """
    update.message.reply_text(
        text='Hi! So you\'ve decided to come visit the Bistro. I\'m thrilled. \n'
             'Let me help get you a table. \n'
             'When do you visit?',
        reply_markup=telegramcalendar.create_calendar()
    )
    # change bot state to accept day of visit as input.
    return settings.INPUT_DAY


def visit_date_handler(bot, update):
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        reply_keyboard = get_available_time_list(date)
        reservation_exists = User.check_reservation(user_id=update.callback_query.from_user.id, date=date)
        if reservation_exists:
            bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text='A reservation already exists for {0}.\n'
                     'Only one reservation per day per user is allowed.\n'
                     'Please try again with a different date.'.format(date.strftime("%A, %b %d, %Y")),
                reply_markup=telegramcalendar.create_calendar()
            )
            return settings.INPUT_DAY
        add_to_cache(
            chat_id=update.callback_query.from_user.id,
            data={
                "date": date
            }
        )
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text='You\'ve selected ' + date.strftime("%A, %b %d, %Y")
                 + '\nWhat time suits you? (Time is in 24 Hour format)'
                   '\nPlease note that by default, table will be reserved for up to two hours from the time you enter.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True
            )
        )
        return settings.INPUT_TIME
    return settings.INPUT_DAY


def conversation_expired(bot, update):
    """
    End Conversation.
    :param bot:
    :param update:
    :return:
    """
    update.message.reply_text(
        'Your conversation expired as you\'ve been inactive for too long. Please start again.'
    )
    return ConversationHandler.END


def get_available_time_list(date):
    """
    Get list of available timeslots for the day.
    :param chat_id:
    :return:
    """
    return [
        ['18:00', '18:30'],
        ['19:00', '19:30'],
        ['20:00', '20:30'],
        ['21:00', '21:30'],
        ['22:00', '22:30'],
        ['23:00', '23:30']
    ]


def cancel(bot, update):
    """
    End conversation.
    :param bot:
    :param update:
    :return:
    """
    user = update.message.from_user
    logger.info("User {}:{}canceled the conversation.".format(user.first_name, update.message.chat_id))
    update.message.reply_text(
        'Sorry you had to cancel.\n'
        'Look forward to interacting with you again!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


@is_booking_active
def set_visit_time(bot, update):
    """
    Set customer's visiting time.
    :param bot:
    :param update:
    :return:
    """
    reply_keyboard = [
        ['1', '2'],
        ['3', '4'],
        ['5', '6'],
        ['7', '8'],
        ['9', '10'],
        ['11', '12'],
        ['13', '14'],
        ['15', '16'],
        ['17', '18'],
        ['19', '20'],
    ]
    user_info = fetch_from_cache(update.message.chat.id)
    visiting_time = update.message.text
    user_info['time'] = visiting_time
    update_cache(update.message.chat.id, user_info)
    update.message.reply_text(
        'Great. How many guests?\n'
        'We allow bulk bookings for up to 12 people at once.\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True
        )
    )
    print('new state: ' + str(settings.INPUT_NUM_PEOPLE))
    return settings.INPUT_NUM_PEOPLE


def visiting_time_skipped(bot, update):
    """
    If person did not add visiting time when they were supposed to, keep asking them to add a visiting time.
    :param bot:
    :param update:
    :return:
    """
    reservation_date = ''
    reply_keyboard = get_available_time_list(reservation_date)
    update.message.reply_text(
        'Please enter time for reservation. This is mandatory.\n'
        'We allow bulk booking for up to 12 people at once.'
        '\n In case of special requirements and parties, contact us at XXX-XXX-XXXX or send an email @ abc@xyz.com',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True
        )
    )
    return settings.INPUT_TIME


def create_inline_keyboard(tables):
    """
    Create an InlineKeyboard from a list of available tables.
    :param tables:
    :return:
    """
    keyboard = []
    current_key_set = []
    for table in tables:
        cur_button = InlineKeyboardButton('Table ' + str(table.id) + '(Seats ' + str(table.size) + ')',
                                          callback_data=str(table.id))
        current_key_set.append(cur_button)
        if len(current_key_set) == 2:
            keyboard.append(current_key_set)
            current_key_set = []
    if len(current_key_set) != 0:
        # if len(keyboard) != 0:
        # if keyboard length is zero, it means only 1 table is available.
        # current_key_set.append(InlineKeyboardButton('Auto-Select', callback_data='autoselect'))
        keyboard.append(current_key_set)
    # else:
    # if len(keyboard) != 0:
    #     keyboard.append([InlineKeyboardButton('Auto-Select', callback_data='autoselect')])
    return keyboard


def get_duration(date, time):
    start_hour = int(time[0:2])
    start_minute = int(time[3:5])
    start_time = date.replace(hour=start_hour, minute=start_minute, microsecond=0)
    end_time = start_time + datetime.timedelta(hours=2)
    return start_time, end_time


@is_booking_active
def input_num_people(bot, update):
    """
    Set number of people for reservation.
    :return:
    """
    user_info = fetch_from_cache(update.message.chat.id)
    user_info['num_people'] = update.message.text
    date = user_info['date']
    time = user_info['time']
    start_time, end_time = get_duration(date, time)
    if int(user_info['num_people']) < 12:
        update_cache(update.message.chat.id, user_info)
        tables = Table.get_available_tables(start_time, end_time, user_info['num_people'])
        if len(tables) != 0:
            keyboard = create_inline_keyboard(tables)
            update.message.reply_text(
                'Please select a table.\n',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # if no email is present in data store for this user, take system to email input state.
            return settings.INPUT_TABLE_NUMBER
        else:
            keyboard = [
                [InlineKeyboardButton('Try Again', callback_data='restart')],
                [InlineKeyboardButton('Contact Us', callback_data='contact')]
            ]
            update.message.reply_text(
                'Sorry. No tables available at ' + user_info['time'] + ' on ' + date.strftime("%A, %b %d, %Y") + '.\n'
                                                                                                                 'Please try again for a different time or contact us for more information.\n',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # if no email is present in data store for this user, take system to email input state.
            return settings.NO_TABLES_AVAILABLE
    else:
        user_info['tables'] = 'autoselect'
        update_cache(update.message.chat.id, user_info)
        user = User.get_user(update.message.chat.id)
        if user.email in [None, '']:
            update.message.reply_text(
                'Please enter email address for confirmation.\n'
            )
            return settings.INPUT_EMAIL
        else:
            update.message.reply_text(
                'Confirmation email will be sent to the following email address: {}'
                '\n Press OK to Confirm and Change to update email address.'.format(user.email),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton('Confirm', callback_data='confirm')],
                        [InlineKeyboardButton('Change', callback_data='change')]
                    ]
                )
            )
            return settings.EMAIL_OPTIONS


@is_booking_active
def num_people_skipped(bot, update):
    """
    User did not enter number of people for reservation.
    :return:
    """
    update.message.reply_text(
        'Please enter number of people who are going to be coming(up to 12).\n'
        'We take bulk bookings of upto 12 people at once.\n'
        'For more than 12 guests, please call us at XXX-XXX-XXXX or send us an email @ abc@xyz.com.'
    )
    return settings.INPUT_NUM_PEOPLE


def set_user_email(bot, update):
    """
    This should only be asked in case user is a new user.
    In case an old user is returning, this must be skipped.
    :return:
    """
    chat_id = update.message.chat.id
    user_info = fetch_from_cache(chat_id)
    user_info['email'] = update.message.text
    update_cache(chat_id, user_info)
    # This is a fire and forget call.
    # Should be responsive enough.
    User.set_email_address(chat_id, update.message.text)
    update.message.reply_text(
        text='Anything else you want us to know about the reservation?'
             'Press None for No Extras.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton('None', callback_data='No'),
                    InlineKeyboardButton('Yes', callback_data='Yes')
                ]
            ]
        )
    )
    return settings.ANY_REMARKS


@is_booking_active
def email_already_exists(bot, update):
    """
    Choose whether to use existing email address that is stored for the user or add a new email address.
    :param bot:
    :param update:
    :return:
    """
    print(vars(bot))
    update.message.reply_text(
        'Please enter a new email address or enter command /cancel to keep using current email address for '
        'further communication.\n'
    )


@is_booking_active
def enter_valid_email(bot, update):
    """
    User entered invalid email.
    :param bot:
    :param update:
    :return:
    """
    print(vars(bot))
    update.message.reply_text(
        'Please enter a valid email address or enter the command /skipemail to skip adding an email address.\n'
        '(Note that in case you choose to skip adding an email, a confirmation will not be received on email)'
    )
    return settings.INPUT_EMAIL


def send_confirmation_message(bot, chat_id, num_people, time, date, reservation_id, update, tables=None):
    """
    Send reservation confirmation message.
    :param chat_id:
    :param num_people:
    :param time:
    :param date:
    :param reservation_id:
    :param update:
    :return:
    """
    name = update.callback_query.from_user.first_name + " " + update.callback_query.from_user.last_name
    bot.send_message(
        chat_id=chat_id,
        text='Successful!'
             '\nReservation Confirmed for {0} at {1}, {2}.'
             '\nReservation ID: {3}'.format(num_people, time, date.strftime("%A, %b %d, %Y"), reservation_id, name)
    )
    bot.send_message(
        chat_id=chat_id,
        text='If you provided us with an email address, a booking confirmation will soon be sent to you '
             'over email.'
    )


@is_booking_active
def show_confirmation_dialog(bot, update):
    """
    CallbackQueryHandler that decides Whether or not to show confirmation dialog to user
    stating all details entered and ask them to confirm.
    TODO: [LATER] Allow the user to go back to a particular stage and re enter information from there onwards.
    :return:
    """
    # Get reservation information from cache.
    chat_id = update.callback_query.from_user.id
    if update.callback_query.data == 'Yes':
        bot.edit_message_text(
            text='Please wait while we confirm your reservation.',
            chat_id=chat_id,
            message_id=update.callback_query.message.message_id
        )
        # Generate booking id, save reservation info in datastore, update reservation record and send email.
        # If booking fails, show user a message and ask them to start again at a different time.
        user_info = fetch_from_cache(chat_id=chat_id)
        time = user_info['time']
        date = user_info['date']
        num_people = user_info['num_people']
        table = user_info['tables']
        email = None
        if 'email' in user_info:
            email = user_info['email']
        try:
            first_name = update.effective_user.first_name
        except Exception as ex:
            first_name = ''
        try:
            last_name = update.effective_user.last_name
        except Exception as ex:
            last_name = ''
        start_time, end_time = get_duration(date, time)
        if isinstance(table, int):
            # check again that the selected table is available.
            # Assuming some time has elapsed since the user selected the table and the table might've been booked by
            # someone else during that time.
            if Table.is_available(table, start_time, end_time):
                user = User.get_user(chat_id)
                was_successful, reservation_id, tables = make_reservation(
                    email, first_name, last_name, chat_id, num_people, table, start_time, end_time, user
                )
                if was_successful:
                    send_confirmation_message(bot, chat_id, num_people, time, date, reservation_id, update, tables)
                else:
                    bot.send_message(
                        chat_id=chat_id,
                        text="Sorry, Table " + str(table) + ' is no longer available. Please start again.'
                    )
                return ConversationHandler.END
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text="Sorry, Table " + str(table) + ' is no longer available. Please start again.'
                )
                return ConversationHandler.END
        else:
            # Select tables automatically.
            user = User.get_user(chat_id)
            was_successful, reservation_id, tables = make_reservation(
                email, first_name, last_name, chat_id, num_people, table, start_time, end_time, user
            )
            if not was_successful:
                bot.send_message(
                    chat_id=chat_id,
                    text="Could not find sufficient tables for your reservation."
                         "\nPlease contact us for further assistance."
                         "\nType /contact for more details."
                )
            else:
                send_confirmation_message(bot, chat_id, num_people, time, date, reservation_id, update, tables)
            return ConversationHandler.END
    else:
        bot.edit_message_text(
            text='Reservation Cancelled. See you again.',
            chat_id=chat_id,
            message_id=update.callback_query.message.message_id
        )
        return ConversationHandler.END


@is_booking_active
def add_remarks(bot, update):
    """
    Add remarks to a user's booking.
    :param bot:
    :param update:
    :return:
    """
    user_remarks = update.message.text
    user_info = fetch_from_cache(update.message.chat.id)
    user_info['remarks'] = user_remarks
    update_cache(update.message.chat.id, user_info)
    num_people = user_info['num_people']
    time = user_info['time']
    date = user_info['date'].strftime("%A, %b %d, %Y")
    extras = user_remarks
    table = user_info['tables']
    if table == 'autoselect':
        table = 'Auto-Select'
    reply_keyboard = [
        [InlineKeyboardButton('Yes', callback_data='Yes')],
        [InlineKeyboardButton('No', callback_data='No')]
    ]
    update.message.reply_text(
        'Thanks. We\'ll keep that in mind.\n'
        'Booking Summary:\n'
        'Making a reservation for {0} people at {1} on {2}.\n'
        'Table: {4}\n'
        'Extras: {3}'.format(num_people, time, date, extras, table),
        reply_markup=InlineKeyboardMarkup(
            reply_keyboard
        )
    )
    return settings.SHOW_CONFIRMATION_DIALOG


def unregistered_command(bot, update):
    """
    Fallback Method for a command that is not registered.
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(
        chat_id=update.message.chat.id,
        text='Unrecognized Input. Please press /(Forward slash) to see the list of valid commands.'
    )


@is_booking_active
def input_table(bot, update):
    """
    Set table to be used.
    :param bot:
    :param update:
    :return:
    """
    chat_id = update.callback_query.from_user.id
    user_info = fetch_from_cache(chat_id)
    try:
        tables = int(update.callback_query.data)
    except (ValueError, Exception) as ex:
        tables = 'autoselect'
    user_info['tables'] = tables
    update_cache(chat_id, user_info)
    bot.edit_message_text(
        chat_id=chat_id,
        text='You\'ve selected Table: ' + str(tables) + "\n",
        message_id=update.callback_query.message.message_id
    )
    sleep(0.25)
    user = User.get_user(chat_id)
    if user is not None and user.email not in [None, '']:
        email = user.email
        bot.send_message(
            chat_id=chat_id,
            text='Confirmation email will be sent to the following email address: {}'
                 '\nPress Confirm to Proceed or Change to update email address.'.format(email),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton('Confirm', callback_data='confirm')],
                    [InlineKeyboardButton('Change', callback_data='change')]
                ]
            )
        )
        return settings.EMAIL_OPTIONS
    else:
        bot.send_message(
            chat_id=chat_id,
            text='Please enter email address for confirmation.\n',
        )
        return settings.INPUT_EMAIL


def contact(bot, update):
    """
    Return contact information to a user.
    :param bot:
    :param update:
    :return:
    """
    update.message.reply_text(
        'You can contact us via email at: abc@xyz.com.'
        '\n Or \n'
        'You can contact us via telephone at: XXX-XXX-XXX'
    )


@is_booking_active
def email_skipped(bot, update):
    """
    Skipped email. Add remarks.
    :param bot:
    :param update:
    :return:
    """
    update.message.reply_text(
        text='Anything else you want us to know about the reservation?\n'
             'Press None for No extras.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton('None', callback_data='No'),
                    InlineKeyboardButton('Yes', callback_data='Yes')
                ]
            ]
        )
    )
    return settings.ANY_REMARKS


def location(bot, update):
    """
    Return Bistro's Location.
    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Address: \n'
             'Opposite TISS, Sion Trombay Road, Deonar, Chembur, Mumbai.\n'
             'Telephone: XXX-XXX-XXXX'
    )


@is_booking_active
def email_options(bot, update):
    """
    Take in input from email change/confirm inline keyboard button and take system to new state.
    :param args:
    :return:
    """
    chat_id = update.callback_query.from_user.id
    dt = update.callback_query.data
    if dt == 'confirm':
        bot.edit_message_text(
            chat_id=chat_id,
            text="Email confirmed. Anything else you would like us to know about the reservation?"
                 '\nPress None for No Extras.',
            message_id=update.callback_query.message.message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton('None', callback_data='No'),
                        InlineKeyboardButton('Yes', callback_data='Yes')
                    ]
                ]
            )
        )
        return settings.ANY_REMARKS
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            text="You've requested a change in email address.\n"
                 "Please enter new email address.",
            message_id=update.callback_query.message.message_id
        )
        return settings.INPUT_EMAIL


def reservation_list_handler(bot, update):
    """
    Show user a list of current reservations and their details.
    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat.id
    reservation_list = User.get_reservations(chat_id)
    if len(reservation_list) == 0:
        reservation_list_body = 'No reservations made by you yet.\n'
    else:
        reservation_list_body = 'Here\'s a list of reservations you\'ve made in the past:'
    item_number = 1
    for reservation in reservation_list:
        if reservation.start_time.minute == 0:
            minute = '00'
        else:
            minute = '30'
        list_item = '\n\n' \
                    '{0}. Reservation ID: {1}\n' \
                    '   Guests: {2}\n' \
                    '   Date: {3}\n' \
                    '   Time: {4}' \
            .format(item_number,
                    reservation.reservation_id,
                    reservation.guest_count,
                    reservation.start_time.strftime("%A, %b %d, %Y"),
                    '{0}:{1}'.format(reservation.start_time.hour, minute)
                    )
        reservation_list_body += list_item
        item_number += 1
    bot.send_message(
        chat_id=chat_id,
        text=reservation_list_body
    )


def no_conversation_active(bot, update):
    """
    Return that no conversation is currently active.
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(
        chat_id=update.message.chat.id,
        text='No reservation is currently active. You can start booking a table using the /start command.'
    )


def help(bot, update):
    """
    Show help text to a user.
    :param bot:
    :param update:
    :return:
    """
    help_text = 'Here is a list of commands you can navigate around with:' \
                '\n\n1. /start - Book a table' \
                '\n2. /setemail - Set email address' \
                '\n3. /cancel - Cancel an ongoing reservation in progress' \
                '\n4. /contact - View Contact Information' \
                '\n5. /myreservations - View Reservation History' \
                '\n6. /location - View Restaurant Location' \
                '\n7. /skipemail - Skip adding email address' \
                '\n\nTo start a reservation,  press /start'
    bot.send_message(
        chat_id=update.message.chat.id,
        text=help_text
    )


@is_booking_active
def any_remarks_handler(bot, update):
    """
    Whether or not any remarks are to be added by a user.
        1. If yes, go to INPUT_REMARKS state.
        2. If no, go to CONFIRMATION STATE.
    :param bot:
    :param update:
    :return:
    """
    to_add = update.callback_query.data
    if str(to_add) == 'Yes':
        bot.edit_message_text(
            text='Please enter anything else that you\'d like us to keep in mind.',
            chat_id=update.callback_query.from_user.id,
            message_id=update.callback_query.message.message_id
        )
        return settings.INPUT_REMARKS
    else:
        user_info = fetch_from_cache(update.callback_query.from_user.id)
        update_cache(update.callback_query.from_user.id, user_info)
        num_people = user_info['num_people']
        time = user_info['time']
        date = user_info['date'].strftime("%A, %b %d, %Y")
        table = user_info['tables']
        if table == 'autoselect':
            table = 'Auto-Select'
        reply_keyboard = [
            [InlineKeyboardButton('Yes', callback_data='Yes')],
            [InlineKeyboardButton('No', callback_data='No')]
        ]
        bot.edit_message_text(
            chat_id=update.callback_query.from_user.id,
            message_id=update.callback_query.message.message_id,
            text='Skipping extras..'
        )
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text='Booking Summary:\n'
            'Making a reservation for {0} people at {1} on {2}.\n'
            'Table: {4}\n'
            'Extras: {3}'.format(num_people, time, date, 'None', table),
            reply_markup=InlineKeyboardMarkup(
                reply_keyboard
            )
        )
        return settings.SHOW_CONFIRMATION_DIALOG


def change_email(bot, update):
    """
    Update user's email.
    [Not implemented Yet]
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(
        chat_id=update.message.chat.id,
        text='This feature is not yet available.\n'
    )


def get_main_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('contact', contact),
            CommandHandler('myreservations', reservation_list_handler),
            CommandHandler('location', location),
            CommandHandler('cancel', no_conversation_active),
            CommandHandler('setemail', change_email),
            CommandHandler('help', help),
            RegexHandler('^.*', unregistered_command)
        ],

        states={
            settings.INPUT_DAY: [
                # RegexHandler('^(Today|Tomorrow)$', visit_today_tomorrow),
                # RegexHandler('^(Other)$', visit_later)
                CallbackQueryHandler(visit_date_handler)
            ],

            settings.INPUT_TIME: [
                RegexHandler('^([01]\d|2[0-3]):?([0-5]\d)$', set_visit_time),
                RegexHandler('^$', visiting_time_skipped)
            ],

            settings.INPUT_NUM_PEOPLE: [
                RegexHandler('^[1-9]$|^0[1-9]$|^1[0-2]$', input_num_people),
                CommandHandler('cancel', cancel),
                RegexHandler('^', num_people_skipped)
            ],

            settings.INPUT_TABLE_NUMBER: [
                CallbackQueryHandler(input_table),
            ],

            settings.INPUT_EMAIL: [
                # Add regex to handle email address. Follows RFC 5322 Pattern
                # RegexHandler('^(?:[A-Z\d][A-Z\d_-]{5,10}|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})$', set_user_email)
                RegexHandler("^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:["
                             "\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@("
                             "?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25["
                             "0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|["
                             "a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\["
                             "\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$", set_user_email),
                CommandHandler('skipemail', email_skipped)
            ],

            settings.INPUT_REMARKS: [
                MessageHandler(Filters.text, add_remarks)
            ],

            settings.ACCEPT_CONFIRMATION: [
                CallbackQueryHandler(show_confirmation_dialog)
            ],

            settings.SHOW_CONFIRMATION_DIALOG: [
                CallbackQueryHandler(show_confirmation_dialog),
            ],

            settings.NO_TABLES_AVAILABLE: [
                # start again if user selects try again
                CallbackQueryHandler('retry', start),
                # start again if user selects try again
                CallbackQueryHandler('contact', contact)
            ],

            settings.EMAIL_OPTIONS: [
                CallbackQueryHandler(email_options)
            ],

            settings.ANY_REMARKS: [
                CallbackQueryHandler(any_remarks_handler)
            ],

            None: [
                CommandHandler('cancel', cancel),
                CommandHandler('start', start),
                CommandHandler('contact', contact),
                CommandHandler('myreservations', reservation_list_handler),
                CommandHandler('location', location),
                CommandHandler('setemail', change_email),
                CommandHandler('help', help),
                CommandHandler('^.*', conversation_expired),
                MessageHandler(Filters.text, conversation_expired),
                # RegexHandler('^$', conversation_expired),
                CallbackQueryHandler(conversation_expired),
            ]
        },

        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('contact', contact),
            CommandHandler('myreservations', reservation_list_handler),
            CommandHandler('help', help),
            CommandHandler('setemail', change_email),
            CommandHandler('^.*', unregistered_command),
            # CommandHandler('location', location)
        ]
    )
