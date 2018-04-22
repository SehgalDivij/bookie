from django.conf import settings
from django.template.loader import get_template

import sendgrid
from sendgrid import Email
from sendgrid.helpers.mail import Content, Mail

from api.ndb_models import *


def is_available(table_id=1, date='201800810', start_time=None, end_time=None):
    """
    Check if table with table_id is available.
    :param table_id:
    :param date:
    :param time:
    :return:
    """
    query = TableReservation.query()
    query = query.filter(TableReservation.table == table_id)
    query = query.filter(TableReservation.start_time <= start_time)
    for reservation in query:
        print(vars(reservation))
    print(query)
    return True


def get_vacant_tables(start_time, end_time):
    """
    Get table ids of available tables during a time slot.
    :param start_time:
    :param end_time:
    :return:
    """
    Table.get_all()
    table_query = TableReservation.query()
    # table_query = table_query.filter(TableReservation.start_time == start_time)
    table_query = table_query.filter(TableReservation.start_time >= start_time)
    table_query = table_query.filter(TableReservation.start_time <= end_time)
    print(table_query.fetch())


def send_email(rendered, subject, recipient, from_address, api_key):
    sg = sendgrid.SendGridAPIClient(apikey=api_key)
    from_email = Email(from_address)
    to_email = Email(recipient)
    subject = subject
    content = Content("text/html", rendered)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code > 226:
        msg = 'Could not send email. Following error occurred. {} Error code: {}'.format(
            response.body,
            response.status_code
        )
        return {
            "message": "error",
            "reason": response.body
        }


def send_confirmation_email(reservation_id, num_people, tables, date, start_time, email):
    """
    Send confirmation email to a user.
    :param tables:
    :param date:
    :param email:
    :param start_time:
    :param num_people:
    :param reservation_id:
    :return:
    """
    post_booking_mail = get_template('post_booking_email.html')
    context = dict()
    context['reservation_id'] = reservation_id
    context['num_people'] = num_people
    context['date'] = date.strftime("%A, %b %d, %Y")
    if start_time.minute == 0:
        minutes = '00'
    else:
        minutes = '30'
    context['time'] = '{0}:{1}'.format(start_time.hour, minutes)
    if isinstance(tables, list):
        tab_list = str(tables[0])
        for t in tables[1:]:
            tab_list = tab_list + ', ' + str(t)
        context['tables'] = tab_list
    else:
        context['tables'] = tables
    rendered = post_booking_mail.render(context=context)
    print('rendered email: ')
    print(rendered.encode('utf-8').strip())
    api_key = settings.SENDGRID_API_KEY
    subject = settings.CONFIRMATION_SUBJECT
    to_address = email
    from_address = settings.FROM_EMAIL
    print('sending encoded to ' + to_address)
    email_send_response = send_email(rendered.encode('utf-8').strip(), subject, to_address, from_address, api_key)
    if email_send_response is not None:
        print(email_send_response)


@ndb.transactional(xg=True)
def make_reservation(email, first_name, last_name, chat_id, num_people, tables, start_time, end_time, user):
    """
    Pick data from cache and update changes in data store(DB).
    :return:
    """
    if not isinstance(tables, int) and tables == 'autoselect':
        # In case of auto select, go for best fit for number of people to the available tables.
        available_tables = Table.get_available_tables(start_time, end_time, num_people)
        if len(available_tables) != 0:
            # If available, assign the first table in list, as table is already sorted in increasing order of table
            # capacity.
            # An algorithm to choose multiple tables can be worked out as a version of Binary Knapsack, but something
            # such of that sort would need more Information such as how much a Restaurant Owner is willing to:
            #   1. Let free seats on the table for a reservation
            #      (e.g, for a booking of 5 people, if the only fitting table is 8, is the restaurant owner willing to
            #      let 3 seats go vacant? As this would mean loss of revenue and blocking of 3 seats for the duration
            #      of the reservation.(opportunity cost)).
            #   2. If 1 is not possible, but the owner would still prefer maximization of seats, he
            #      the other thing that he should be willing to do is transfer a booking to another table
            #      in lieu of another potential reservation that would lead to better maximization of the available
            #      space over all.
            #   3. The third characteristic that would be a cause for concern is the arrangement of tables.
            #      a. Are two tables adjacent to each other?
            #      b. Is it possible to join the two tables together?
            #      c. If not adjacent, is it possible that the two tables can be moved to be placed close to each other
            #         and subsequently allow joining?
            #   etc. Information on concerns as mentioned above will define whether a table can/cannot be assigned to a
            #   reservation and since the scope of requirements would be too broad, it was planned to be taken up but
            #   not actually taken up.
            tables = available_tables[0]
        else:
            # In case no table is available that is either same capacity as the number of people or more, return None.
            return False, False, None
    # else:
    # Table has been either selected by the user or automatically by the above logic and can be booked.
    reservation = Reservation(
        user_id=str(chat_id),
        guest_count=int(num_people),
        start_time=start_time,
        end_time=end_time,
        reservation_id=Reservation.make_reservation_id()
    )
    reservation.put()
    table_reservation = TableReservation(
        reservation_id=str(reservation.reservation_id),
        table=tables,
        start_time=start_time,
        end_time=end_time
    )
    table_reservation.put()
    if user is None:
        user = User(
            id=str(chat_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            reservations_made=1,
            reservations_cancelled=0
        )
        user.put()
    else:
        user.reservations_made += 1
        user.put()
    defer_args = {
        'reservation_id': reservation.reservation_id,
        'num_people': num_people,
        'tables': tables,
        'date': start_time.date(),
        'start_time': start_time,
        'email': user.email,
    }
    send_confirmation_email(**defer_args)
    # deferred.defer(send_confirmation_email, *defer_args, _countdown=2)
    return True, reservation.reservation_id, tables

