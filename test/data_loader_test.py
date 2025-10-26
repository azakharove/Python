import io
import csv
from datetime import datetime

import pytest

from trading_lib.data_loader import load_from_reader, load_from_reader_yf, _parse_date_only

def test_perfect():
    perfect_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-22T19:54:01.786263,IBM,144.79
2025-09-23T19:54:01.801212,MSFT,150.06
2025-09-21T19:54:01.816644,AAPL,154.48"""
    f = io.StringIO(perfect_string)
    reader = csv.DictReader(f)
    data = load_from_reader(reader)
    assert len(data) == 4
    assert data[0].symbol == "AAPL"
    assert data[0].price == 149.35
    assert data[0].timestamp == datetime(
        year=2025, month=9, day=21, hour=19, minute=54, second=1, microsecond=774173
    )

    assert data[1].symbol == "IBM"
    assert data[1].price == 144.79
    assert data[1].timestamp == datetime(
        year=2025, month=9, day=22, hour=19, minute=54, second=1, microsecond=786263
    )

    assert data[2].symbol == "MSFT"
    assert data[2].price == 150.06
    assert data[2].timestamp == datetime(
        year=2025, month=9, day=23, hour=19, minute=54, second=1, microsecond=801212
    )

    assert data[3].symbol == "AAPL"
    assert data[3].price == 154.48
    assert data[3].timestamp == datetime(
        year=2025, month=9, day=21, hour=19, minute=54, second=1, microsecond=816644
    )


def test_bad_timestamp():
    bad_timestamp_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-22T19:hi:54,IBM,144.79
2025-09-23T19:54:01.801212,MSFT,150.06
2025-09-21T19:54:01.816644,AAPL,154.48"""
    f = io.StringIO(bad_timestamp_string)
    reader = csv.DictReader(f)
    with pytest.raises(ValueError):
        load_from_reader(reader)


def test_bad_price():
    bad_timestamp_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-23T19:54:01.801212,MSFT,hi
2025-09-21T19:54:01.816644,AAPL,154.48"""
    f = io.StringIO(bad_timestamp_string)
    reader = csv.DictReader(f)
    with pytest.raises(ValueError):
        load_from_reader(reader)

def test_two_columns():
    perfect_string =  """Date,Close
2005-01-03,26.73
2005-01-04,26.84
2005-01-05,26.78
2005-01-06,26.75"""
    f = io.StringIO(perfect_string)
    reader = csv.DictReader(f)
    data = load_from_reader_yf(reader, "AAPL")
    assert len(data) == 4
    assert data[0].symbol == "AAPL"
    assert data[0].price == 26.73
    assert data[0].timestamp == datetime(
        year=2005, month=1, day=3
    )

    assert data[1].symbol == "AAPL"
    assert data[1].price == 26.84
    assert data[1].timestamp == datetime(
        year=2005, month=1, day=4
    )

    assert data[2].symbol == "AAPL"
    assert data[2].price == 26.78
    assert data[2].timestamp == datetime(
        year=2005, month=1, day=5
    )

    assert data[3].symbol == "AAPL"
    assert data[3].price == 26.75
    assert data[3].timestamp == datetime(
        year=2005, month=1, day=6
    )

def test_parse_date_only():
    ts = "2025-09-21"
    dt = _parse_date_only(ts)
    assert dt == datetime(year=2025, month=9, day=21)