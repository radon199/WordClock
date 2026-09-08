from datetime import tzinfo, timedelta, datetime, timezone

# New Pacific not DST time zone. Always -7 hours from UTC.

class PtTimeZone(tzinfo):
    def __init__(self):
        self.reprname = "Pacific"
        self.name = "PT"

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        return self.name

    def utcoffset(self, dt):
        return timedelta(hours=-7)

    def dst(self, dt):
        return timedelta(0)


# Inject pt time zone object into datetime namespace
timezone.pt = PtTimeZone()
