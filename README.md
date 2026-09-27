# business-days

Count working days between two `date` objects with a holiday calendar. Standard library only.

```python
from datetime import date
from business_days import BusinessDays, HolidayCalendar

cal = HolidayCalendar([date(2024, 1, 1)])          # New Year's Day
bd = BusinessDays(cal)

bd.is_working_day(date(2024, 1, 1))                # False (holiday Monday)
bd.is_working_day(date(2024, 1, 2))                # True
bd.next_working_day(date(2024, 1, 5))              # date(2024, 1, 8)
bd.count_between(date(2024, 1, 1), date(2024, 1, 8))          # 4
bd.count_between(date(2024, 1, 1), date(2024, 1, 8), inclusive=True)  # 5
```

## Why this exists

The Python standard library has no business-day arithmetic, and `numpy.busday_count` is unavailable in environments without third-party packages. This library covers the one operation that comes up in invoicing and SLA tracking — counting working days across an interval with a caller-supplied holiday set — with no dependencies and a tiny surface.

The trade-off: holidays are passed as explicit `date` objects. There is no built-in locale or country pack, because regional holiday rules drift year to year and embedding them would invite staleness. Bring your own list.

## Semantics (read this before relying on counts)

- Weekends are Saturday and Sunday.
- `count_between(start, end)` is **half-open on the right**: `[start, end)`. `start` is counted if it is a working day; `end` is not. This matches `range` arithmetic and lets you chain intervals without double-counting.
- `count_between(start, end, inclusive=True)` is `[start, end]`: both endpoints eligible.
- If `end < start`, the result is the negation of the forward count. Counts are signed and antisymmetric; this is the only directional behaviour the library supports.
- A half-open interval where `start == end` is empty and returns `0`, even if that day is a working day. Use `inclusive=True` for single-day checks.

The awkward edge: when `start == end` and the day is a working day, the default half-open call returns `0`, not `1`. If you want to count both endpoints of a same-day interval, pass `inclusive=True`.

## Exports

- `HolidayCalendar(holidays=None)` — immutable holiday set; `.is_holiday(date)`, `.holidays`.
- `BusinessDays(calendar=None)` — `.is_working_day(date)`, `.next_working_day(date)`, `.previous_working_day(date)`, `.count_between(start, end, inclusive=False)`.
