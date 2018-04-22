from django.utils.crypto import get_random_string
from google.appengine.ext import ndb


class Table(ndb.Model):
    size = ndb.IntegerProperty(default=0)
    # signifies if this can be part of a multi table booking
    can_join = ndb.BooleanProperty(default=False)
    id = ndb.IntegerProperty()

    EXPECTED_MEAL_TIME_HOURS = 2

    @classmethod
    def get_all(cls, min_capacity=None):
        """
        Get list of all tables in the system.
        :return:
        """
        tables = cls.query()
        if min_capacity is not None and isinstance(min_capacity, int):
            tables = tables.filter(cls.size >= min_capacity)
        tables = tables.order(cls.size)
        result_set = tables.fetch()
        return result_set

    @classmethod
    def exists(cls, table_id):
        """
        Check if a table exists.
        :param table_id:
        :return:
        """
        query = cls.query()
        query = query.filter(Table.id == table_id)
        result_set = query.fetch()
        if len(result_set) == 0:
            return False
        else:
            return True

    @classmethod
    def is_available(cls, table_id, start_time, end_time):
        """
        Returns whether a table is available or not.
        :param table_id:
        :param start_time:
        :param end_time:
        :return:
        """
        query = TableReservation.query()
        query = query.filter(TableReservation.table == table_id)
        query = query.filter(TableReservation.start_time >= start_time)
        query = query.filter(TableReservation.start_time <= end_time)
        result_set = query.fetch()
        for reservation in result_set:
            print(reservation)
            reservation = dict(reservation)
            print(reservation)
            # if end_time.time() >= reservation['start_time'].time >= start_time.time() \
            if end_time >= reservation['end_time'] >= start_time:
                """
                Check if any reservation for that day falls during the same time as the duration needed for reservation
                """
                print('end time', reservation['end_time'])
                print('desired start time', start_time)
                print('start time', reservation['start_time'])
                print('desired end time', end_time)
                return False
        return True

    @classmethod
    def get(cls, table_id):
        """
        Check if a table exists.
        :param table_id:
        :return:
        """
        query = cls.query()
        query = query.filter(cls.id == table_id)
        result_set = query.fetch()
        if len(result_set) == 0:
            return False
        else:
            return True

    @classmethod
    def get_available_tables(cls, start_time, end_time, num_people):
        """
        Get tables available during a time frame.
        :param start_time:
        :param end_time:
        :return:
        """
        table_set = cls.get_all(min_capacity=int(num_people))
        available_tables = []
        query = TableReservation.query()
        query = query.filter(TableReservation.start_time >= start_time)
        query = query.filter(TableReservation.start_time <= end_time)
        result_set = query.fetch()

        def _get_reservations(reservations, table_id):
            res_list = []
            for res in reservations:
                if res.table == table_id:
                    res_list.append(res)
            return res_list

        for table in table_set:
            print('reservations for table: ' + str(table.id))
            reservations = _get_reservations(result_set, table.id)
            print(reservations, len(reservations))
            is_available = True
            for reservation in reservations:
                print(reservation)
                print('table_id: ', reservation.table)
                print('end time', reservation.end_time)
                print('desired start time', start_time)
                print('start time', reservation.start_time)
                print('desired end time', end_time)
                if end_time >= reservation.end_time >= start_time and is_available:
                    """
                    Check if any reservation for that day falls during the same time as the duration needed for 
                    reservation.
                    """
                    is_available = False
                    # Break at the first clash of timings.
                    break
            if is_available:
                available_tables.append(table)
        return available_tables


class Reservation(ndb.Model):
    """
    Store a booking for a date, time and a user, along with number of guests.
    """
    start_time = ndb.DateTimeProperty(required=True)
    end_time = ndb.DateTimeProperty(required=True)
    reservation_id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    guest_count = ndb.IntegerProperty()

    @classmethod
    def make_reservation_id(cls):
        res_id = get_random_string(length=8)
        try:
            device = Reservation.objects.get(reservation_id=res_id)
            if device:
                return cls.make_reservation_id()
        except Exception as ex:
            return res_id

    @classmethod
    def get_by_user(cls, user_id):
        """
        Get list of reservations by chat id.
        :param user_id:
        :return:
        """
        reservation_query = cls.query()
        reservation_query = reservation_query.filter(cls.user_id == user_id)
        reservations = reservation_query.fetch()
        print(reservations)
        return reservations

    @classmethod
    def get_by_reservation(cls, res_id):
        """
        Get reservation info by reservation id.
        :param res_id:
        :return:
        """
        reservation_query = cls.query()
        reservation_query = reservation_query.filter(cls.reservation_id == res_id)
        info = reservation_query.fetch()
        print(info)
        return info


class TableReservation(ndb.Model):
    """
    Store a reservation for a table for a date, time and a related reservation_id.
    """
    reservation_id = ndb.StringProperty()
    table = ndb.IntegerProperty()
    start_time = ndb.DateTimeProperty(required=True)
    end_time = ndb.DateTimeProperty(required=True)


class User(ndb.Model):
    """
    Contains User Information.
    """
    # corresponds to chat_id.
    id = ndb.StringProperty('id')
    first_name = ndb.StringProperty('first_name')
    last_name = ndb.StringProperty('last_name')
    email = ndb.StringProperty('email')
    reservations_made = ndb.IntegerProperty('bookings')
    reservations_cancelled = ndb.IntegerProperty('cancelled')

    @classmethod
    def get_user(cls, user_id):
        """
        Get user with a specific chat_id
        :return:
        """
        us_qr = cls.query()
        us_qr = us_qr.filter(cls.id == str(user_id))
        user_set = us_qr.fetch()
        if len(user_set) != 0:
            return user_set[0]
        else:
            return None

    @classmethod
    def get_reservations(cls, user_id):
        """
        Get list of reservations made by a user in the past.
        :param user_id:
        :return:
        """
        r_query = Reservation.query()
        r_query = r_query.filter(Reservation.user_id == str(user_id))
        return r_query.fetch()

    @classmethod
    def check_reservation(cls, user_id, date):
        """
        Check whether a reservation for a user exists on a particular date.
        :param user_id:
        :param date:
        :return: True if exists, False if does not exist.
        """
        r_query = Reservation.query()
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=23, minute=59, second=59, microsecond=0)
        r_query = r_query.filter(Reservation.start_time >= start_time)
        r_query = r_query.filter(Reservation.start_time <= end_time)
        r_query = r_query.filter(Reservation.user_id == str(user_id))
        if len(r_query.fetch()) != 0:
            return True
        else:
            return False

    @classmethod
    def set_email_address(cls, chat_id, email):
        """
        Update User's email address.
        :param chat_id:
        :param email:
        :return:
        """
        user = cls.get_user(chat_id)
        if user is not None:
            user.email = email
            user.put()
        return None
