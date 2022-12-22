from datetime import tzinfo, timedelta, datetime, timezone

# Taken from the Python datetime module documentation on how to setup a US time zone
# https://docs.python.org/3.4/library/datetime.html#datetime.tzinfo


def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


# Constant for no time delta and one hour offset
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday in March, which is the first Sunday on or after Mar 8.
PDT_START = datetime(1, 3, 8, 2)
# and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
PDT_END = datetime(1, 11, 1, 1)


class PstTimeZone(tzinfo):
    def __init__(self):
        self.stdoffset = timedelta(hours=-8)
        self.reprname = "Pacific"
        self.stdname = "PST"
        self.dstname = "PDT"

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        # If datetime is not set, or the timezone isn't set, return zero, the datetime is not configured for PST
        if dt is None or dt.tzinfo is None:
            return ZERO

        # Assert that the datetime's timezone is this
        assert dt.tzinfo is self

        # Compute the start and end of PDT for the current year
        start = first_sunday_on_or_after(PDT_START.replace(year = dt.year))
        end   = first_sunday_on_or_after(PDT_END.replace(year = dt.year))

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO


# Inject pst time zone object into datetime namespace
timezone.pst = PstTimeZone()
