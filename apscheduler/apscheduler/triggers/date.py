from apscheduler.util import convert_to_datetime, datetime_repr


class DateTrigger(object):
    def __init__(self, defaults, run_date, timezone=None):
        """
        Triggers once on the given datetime.

        :param run_date: the date/time to run the job at
        :param timezone: time zone for ``run_date``
        :type timezone: str or an instance of a :cls:`~datetime.tzinfo` subclass
        """
        timezone = timezone or defaults['timezone']
        self.run_date = convert_to_datetime(run_date, timezone, 'run_date')

    def get_next_fire_time(self, start_date):
        if self.run_date >= start_date:
            return self.run_date

    def __str__(self):
        return 'date[%s]' % datetime_repr(self.run_date)

    def __repr__(self):
        return "<%s (run_date='%s')>" % (self.__class__.__name__, datetime_repr(self.run_date))
