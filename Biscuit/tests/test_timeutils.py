from Biscuit.utils.timeutils import day_num, get_chunk_num, get_year
from datetime import date


def test_day_num():
    d = date(year=2018, month=1, day=1)
    assert day_num(d) == 1


def test_get_chunk_num():
    d = date(year=2018, month=1, day=1)
    assert get_chunk_num(d, 2) == '01'


def test_get_year():
    d = date(year=2018, month=1, day=1)
    assert get_year(d) == 2018
