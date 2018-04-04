import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
from django.conf import settings

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
    print(selected)
    print(date)
    if selected:
        # bot.send_message(chat_id=update.callback_query.from_user.id,
        #                  text="You selected %s" % (date.strftime("%d/%m/%Y")),
        #                  reply_markup=ReplyKeyboardRemove())
        print('sending message to the bot.')
        reply_keyboard = get_available_time_list(date)
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text='You\'ve selected ' + date.strftime("%A, %b %d, %Y")
                 + '\n What time suits you? (Time is in 24 Hour format)',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True
            )
        )
        return settings.INPUT_TIME
    return settings.INPUT_DAY


# def visit_today_tomorrow(bot, update):
#     """
#     Handler for user visiting either today or tomorrow.
#     Allow booking only for only up to next two days to maintain
#     fairness with customers coming without booking as well.
#     changes bot state to accept time input.
#     resulting state: INPUT_TIME
#     """
#     # TODO: generate list of available time of visit for the restaurant based on table availability.
#     # show in pairs of two, as in:
#     # 12:00 | 12:30
#     # 13:00 | 13:30
#     # 14:00 | 14:30
#     # 15:00 | 15:30
#     # 16:00 | 16:30
#     # TODO: Check if bot is to allow 24 hour format timestamps or 12 hour format timestamps.
#     # TODO: Based on message text - today or tomorrow, extract and pass a date to the restaurant schedule fetch
#     # function.
#     reservation_date = update.message.text
#     reply_keyboard = get_available_time_list(reservation_date)
#     # get today/tomorrow's date and show in message.
#     # date in - weekday, time etc.
#     update.message.reply_text(
#         'You\'ve selected '
#         'What time suits you?'
#         '(Time is given in 24 Hour format)',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard,
#             one_time_keyboard=True
#         )
#     )
#     return settings.INPUT_TIME


# def visit_later(bot, update):
#     """
#     Ask user to enter a day between today or tomorrow.
#     resulting state: same as before. no change in state.
#     """
#     reply_keyboard = [
#         ['Today'],
#         ['Tomorrow'],
#         ['Other']
#     ]
#     update.message.reply_text(
#         # TODO: Add dates here as well, for today and tomorrow.
#         'Sorry. In order to be fair to all our customers, we take bookings only upto two days in advance.'
#         'Please select either Today or Tomorrow or come back later if you plan to visit on a later date.\n'
#         'You can also call us up to enquire further. Press:\n'
#         '1. /contact to get contact information.\n'
#         '2. /cancel to discard your details.\n'
#         '3. /start to start a fresh booking.\n',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard,
#             one_time_keyboard=True
#         )
#     )
#     return settings.INPUT_DAY


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
    update.message.reply_text(
        # TODO: Add dates here as well, for today and tomorrow.
        'Great. How many people would you like to book it for?\n'
        'We allow bulk bookings for up to 20 people at once.\n',
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
    # TODO: get time of reservation from cache and enter here.
    reservation_date = ''
    reply_keyboard = get_available_time_list(reservation_date)
    update.message.reply_text(
        # TODO: Add dates here as well, for today and tomorrow.
        'Please enter time for reservation. This is mandatory.\n'
        'We allow bulk booking for up to 20 people at once.\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True
        )
    )
    return settings.INPUT_TIME


def input_num_people(bot, update):
    """
    Set number of people for reservation.
    :return:
    """
    # TODO: Save number of people in cache.
    update.message.reply_text(
        # TODO: Add dates here as well, for today and tomorrow.
        'Please enter email address for confirmation.\n'
    )
    # if no email is present in data store for this user, take system to email input state.
    return settings.INPUT_EMAIL


def num_people_skipped(bot, update):
    """
    User did not enter number of people for reservation.
    :return:
    """
    update.message.reply_text(
        # TODO: Add dates here as well, for today and tomorrow.
        'Please enter number of people who are going to be coming(up to 20).\n'
        'We take bulk bookings of upto 20 people at once.'
    )
    return settings.INPUT_NUM_PEOPLE


def set_user_email(bot, update):
    """
    This should only be asked in case user is a new user.
    In case an old user is returning, this must be skipped.
    :return:
    """
    # TODO: Save user email in cache as well as datastore backend.
    update.message.reply_text(
        # TODO: Add dates here as well, for today and tomorrow.
        'Anything else you want us to know about the reservation?'
    )
    return settings.INPUT_REMARKS


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


# def show_confirmation_dialog(bot, update):
#     """
#     Show confirmation dialog to user stating all details entered and ask them to confirm.
#     TODO: [LATER] Allow the user to go back to a particular stage and re enter information from there onwards.
#     :return:
#     """
#     update.message.reply_text(
#         # TODO: Add dates here as well, for today and tomorrow.
#         'Making a reservation for 2 people at 7:00 PM on Tuesday, April 4.'
#         # Add commands to this later.
#     )
#     return settings.ACCEPT_CONFIRMATION


def show_confirmation_dialog(bot, update):
    """
    CallbackQueryHandler that decides Whether or not to show confirmation dialog to user
    stating all details entered and ask them to confirm.
    TODO: [LATER] Allow the user to go back to a particular stage and re enter information from there onwards.
    :return:
    """
    # Get reservation information from cache.
    chat_id = update.callback_query.from_user.id
    print(vars(update.callback_query))
    # get above fields from cache.
    update.callback_query.reply_text('Please wait while we confirm your reservation.')
    # Generate booking id, save reservation info in datastore, update available time slots table and send email.
    # If booking fails, show user a message and ask them to start again at a different time.
    bot.send_message('Reservation Confirmed for 8:00 PM, April 2. Reservation ID: BISTRO_02112234')
    bot.send_message(
        chat_id=update.message.chat_id,
        text='If you provided us with an email address, a booking confirmation will soon be sent to you '
             'over email.'
    )
    return settings.ACCEPT_CONFIRMATION


def add_remarks(bot, update):
    """
    Add remarks to a user's booking.
    :param bot:
    :param update:
    :return:
    """
    user_remarks = update.message.text
    reply_keyboard = [
        [InlineKeyboardButton('Yes', callback_data='Yes')],
        [InlineKeyboardButton('No', callback_data='No')]
    ]
    # fetch the following details from cache memory.
    num_people = '2'
    time = '7:00 PM'
    date = 'April 4'
    extras = ''
    update.message.reply_text(
        'Thanks. We\'ll keep that in mind.\n'
        'Booking Summary:\n\n'
        'Making a reservation for {0} people at {1} on {2}.\n'
        'Extras: {3}'.format(num_people, time, date, extras),
        reply_markup=InlineKeyboardMarkup(
            reply_keyboard
        )
    )
    return settings.SHOW_CONFIRMATION_DIALOG


def confirm_reservation(bot, update):
    """
    Confirm User Reservation.
    :param bot:
    :param update:
    :return:
    """
    update.message.reply_text('Reservation Confirmed for 8:00 PM, April 2. Reservation ID: BISTRO_02112234')
    bot.send_message(chat_id=update.message.chat_id,
                     text='If you opted to receive an email, a booking confirmation will soon be sent to you over '
                          'email')
    return ConversationHandler.END


def unregistered_command(bot, update):
    """
    Fallback Method for a command that is not registered.
    :param bot:
    :param update:
    :return:
    """
    pass


def get_main_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],

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
                RegexHandler('^[1-9]$|^0[1-9]$|^1[0-9]$|^20$', input_num_people),
                RegexHandler('^', num_people_skipped)
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
                CommandHandler('skipemail', add_remarks),
                RegexHandler('^', enter_valid_email)
            ],

            settings.INPUT_REMARKS: [
                MessageHandler(Filters.text, add_remarks)
            ],

            settings.ACCEPT_CONFIRMATION: [
                CallbackQueryHandler(show_confirmation_dialog)
            ],
            settings.SHOW_CONFIRMATION_DIALOG: [
                CallbackQueryHandler(show_confirmation_dialog),
                # RegexHandler('^(Yes)$', show_confirmation_dialog),
                # RegexHandler('^(No)$', confirm_reservation)
            ],

            None: [
                CommandHandler('cancel', cancel),
                # CommandHandler('contact', lambda bot, update: bot.)
            ]
        },

        fallbacks=[
            CommandHandler('cancel', cancel),
            # CommandHandler('^$', unregistered_command)
            # CommandHandler('location', location)
        ]
    )
