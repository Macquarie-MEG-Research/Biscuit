""" A few utilities to handle time and dates """

from datetime import date


def day_num(curr_date):
    """ Returns the day number in the year."""
    year = curr_date.year
    return (curr_date - date(year, 1, 1)).days + 1


def get_chunk_num(curr_date, num):
    """ Returns the chunk number. This will be left padded with 0."""
    return "{:0>2}".format(day_num(curr_date) // 2 * num + 1)


def get_year(curr_date):
    """ Returns the current year."""
    return curr_date.year
