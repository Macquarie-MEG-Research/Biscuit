""" A few utilities to handle time and dates """

from datetime import date


def day_num():
    """ Returns the day number in the year."""
    year = date.today().year
    return (date.today() - date(year, 1, 1)).days + 1


def get_fortnight():
    """ Returns the fortnight number. This will be left padded with 0."""
    return "{:0>2}".format(day_num() // 14 + 1)


def get_year():
    """ Returns the current year."""
    return date.today().year
