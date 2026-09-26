import unittest
from datetime import date

from business_days import BusinessDays, HolidayCalendar


class TestHolidayCalendar(unittest.TestCase):
    def test_empty_by_default(self):
        cal = HolidayCalendar()
        self.assertFalse(cal.is_holiday(date(2024, 1, 1)))

    def test_membership(self):
        cal = HolidayCalendar([date(2024, 1, 1)])
        self.assertTrue(cal.is_holiday(date(2024, 1, 1)))
        self.assertFalse(cal.is_holiday(date(2024, 1, 2)))

    def test_immutable(self):
        src = [date(2024, 1, 1)]
        cal = HolidayCalendar(src)
        src.append(date(2024, 1, 2))
        # Caller mutation must not leak into the calendar.
        self.assertFalse(cal.is_holiday(date(2024, 1, 2)))
        self.assertEqual(cal.holidays, frozenset([date(2024, 1, 1)]))

    def test_rejects_non_date(self):
        with self.assertRaises(TypeError):
            HolidayCalendar(["2024-01-01"])
        with self.assertRaises(TypeError):
            HolidayCalendar().is_holiday("2024-01-01")


class TestIsWorkingDay(unittest.TestCase):
    def test_weekdays_without_holidays(self):
        bd = BusinessDays()
        # Monday.
        self.assertTrue(bd.is_working_day(date(2024, 1, 1)))
        # Sunday.
        self.assertFalse(bd.is_working_day(date(2024, 1, 7)))

    def test_weekday_holiday_is_not_working(self):
        cal = HolidayCalendar([date(2024, 1, 1)])
        bd = BusinessDays(cal)
        self.assertFalse(bd.is_working_day(date(2024, 1, 1)))

    def test_rejects_non_date(self):
        bd = BusinessDays()
        with self.assertRaises(TypeError):
            bd.is_working_day("2024-01-01")


class TestNextPreviousWorkingDay(unittest.TestCase):
    def test_next_skips_weekend(self):
        bd = BusinessDays()
        # Friday 2024-01-05 -> Monday 2024-01-08.
        self.assertEqual(
            bd.next_working_day(date(2024, 1, 5)),
            date(2024, 1, 8),
        )

    def test_next_skips_holiday(self):
        cal = HolidayCalendar([date(2024, 1, 8)])
        bd = BusinessDays(cal)
        # Friday -> holiday Monday -> Tuesday.
        self.assertEqual(
            bd.next_working_day(date(2024, 1, 5)),
            date(2024, 1, 9),
        )

    def test_previous_skips_weekend(self):
        bd = BusinessDays()
        # Monday 2024-01-08 -> Friday 2024-01-05.
        self.assertEqual(
            bd.previous_working_day(date(2024, 1, 8)),
            date(2024, 1, 5),
        )

    def test_previous_skips_holiday(self):
        cal = HolidayCalendar([date(2024, 1, 5)])
        bd = BusinessDays(cal)
        # Monday -> holiday Friday -> Thursday.
        self.assertEqual(
            bd.previous_working_day(date(2024, 1, 8)),
            date(2024, 1, 4),
        )


class TestCountBetween(unittest.TestCase):
    def test_half_open_weekend_span(self):
        bd = BusinessDays()
        # Mon 2024-01-01 (inclusive) .. Mon 2024-01-08 (exclusive).
        # Working days: Mon, Tue, Wed, Thu, Fri of the first week = 5.
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 8)),
            5,
        )

    def test_inclusive_weekend_span(self):
        bd = BusinessDays()
        # [Mon 2024-01-01, Mon 2024-01-08] -> 5 + 1 (the second Monday).
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 8), inclusive=True),
            6,
        )

    def test_excludes_holidays(self):
        cal = HolidayCalendar([date(2024, 1, 1)])
        bd = BusinessDays(cal)
        # New Year's Day is a Monday; it should be skipped.
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 8)),
            4,
        )

    def test_single_day_inclusive(self):
        bd = BusinessDays()
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 1), inclusive=True),
            1,
        )
        # Sunday, inclusive, still not a working day.
        self.assertEqual(
            bd.count_between(date(2024, 1, 7), date(2024, 1, 7), inclusive=True),
            0,
        )

    def test_single_day_half_open_is_empty(self):
        bd = BusinessDays()
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 1)),
            0,
        )

    def test_reversed_is_negated(self):
        bd = BusinessDays()
        forward = bd.count_between(date(2024, 1, 1), date(2024, 1, 8))
        backward = bd.count_between(date(2024, 1, 8), date(2024, 1, 1))
        self.assertEqual(forward, 5)
        self.assertEqual(backward, -5)

    def test_reversed_inclusive_antisymmetric(self):
        bd = BusinessDays()
        a = date(2024, 1, 1)
        b = date(2024, 1, 8)
        self.assertEqual(
            bd.count_between(a, b, inclusive=True),
            6,
        )
        # Antisymmetry must hold for inclusive mode too: the right endpoint
        # is included once, not zero or two times.
        self.assertEqual(
            bd.count_between(b, a, inclusive=True),
            -6,
        )

    def test_start_on_holiday_inclusive(self):
        cal = HolidayCalendar([date(2024, 1, 1)])
        bd = BusinessDays(cal)
        # New Year's Day is a Monday; inclusive but still excluded as holiday.
        self.assertEqual(
            bd.count_between(date(2024, 1, 1), date(2024, 1, 1), inclusive=True),
            0,
        )

    def test_rejects_non_date(self):
        bd = BusinessDays()
        with self.assertRaises(TypeError):
            bd.count_between("2024-01-01", date(2024, 1, 8))


if __name__ == "__main__":
    unittest.main()
