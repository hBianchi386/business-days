from __future__ import annotations

from datetime import date, timedelta


class HolidayCalendar:
    """A set of holiday dates for use in business-day calculations.

    Internally a frozenset of ``date`` objects: membership is O(1),
    the calendar is immutable, and callers cannot mutate the set the
    library holds a reference to.
    """

    def __init__(self, holidays=None):
        """``holidays`` may be any iterable of ``date`` objects.

        We coerce to a frozenset eagerly so that accidental later mutation
        of the caller's list/set has no effect on this calendar, and so
        membership checks are O(1) rather than O(n).
        """
        if holidays is None:
            holidays = ()
        for h in holidays:
            if not isinstance(h, date):
                raise TypeError("holidays must be date objects; got %r" % (h,))
        self._holidays = frozenset(holidays)

    def is_holiday(self, d):
        """Return True if ``d`` is an observed holiday."""
        if not isinstance(d, date):
            raise TypeError("expected a date; got %r" % (d,))
        return d in self._holidays

    @property
    def holidays(self):
        """Return the holiday set as a frozenset (immutable)."""
        return self._holidays


class BusinessDays:
    """Count working days between dates, honouring a holiday calendar.

    Weekends are Saturday and Sunday (ISO weekday 6 and 7). Holidays are
    whatever the caller's ``HolidayCalendar`` says, independent of weekday.
    """

    def __init__(self, calendar=None):
        """``calendar`` is an optional :class:`HolidayCalendar`.

        When omitted, an empty calendar is used, so the library degrades
        to plain weekend-skipping.
        """
        self._calendar = calendar if calendar is not None else HolidayCalendar()

    def is_working_day(self, d):
        """Return True iff ``d`` is a weekday and not a holiday."""
        if not isinstance(d, date):
            raise TypeError("expected a date; got %r" % (d,))
        if d.weekday() >= 5:
            return False
        return not self._calendar.is_holiday(d)

    def next_working_day(self, d):
        """Return the first working day strictly after ``d``."""
        if not isinstance(d, date):
            raise TypeError("expected a date; got %r" % (d,))
        cur = d + timedelta(days=1)
        while not self.is_working_day(cur):
            cur += timedelta(days=1)
        return cur

    def previous_working_day(self, d):
        """Return the first working day strictly before ``d``."""
        if not isinstance(d, date):
            raise TypeError("expected a date; got %r" % (d,))
        cur = d - timedelta(days=1)
        while not self.is_working_day(cur):
            cur -= timedelta(days=1)
        return cur

    def count_between(self, start, end, inclusive=False):
        """Count working days in the closed or half-open interval.

        Semantics (a deliberate, single choice):
          * If ``end < start``, the result is the negation of
            ``count_between(end, start)``. This gives signed, anti-
            symmetric counts for past/future deltas without a separate
            direction argument.
          * ``inclusive=False`` (default): the interval is half-open on the
            right, ``[start, end)`` — ``start`` is counted if it is a working
            day, ``end`` is not counted. This mirrors range arithmetic and
            avoids double-counting when chaining intervals.
          * ``inclusive=True``: the interval is ``[start, end]``, both
            endpoints eligible.

        Args:
          start: ``date`` at one end of the interval.
          end: ``date`` at the other end of the interval.
          inclusive: when True, count ``end`` if it is a working day.

        Returns:
          ``int`` number of working days in the interval; signed.
        """
        if not isinstance(start, date) or not isinstance(end, date):
            raise TypeError("start and end must be date objects")
        if end < start:
            return -self.count_between(end, start, inclusive=inclusive)
        if start == end:
            if inclusive:
                return 1 if self.is_working_day(start) else 0
            # Half-open single-point interval [d, d) is empty.
            return 0
        count = 0
        cur = start
        last = end if inclusive else end - timedelta(days=1)
        while cur <= last:
            if self.is_working_day(cur):
                count += 1
            cur += timedelta(days=1)
        return count
