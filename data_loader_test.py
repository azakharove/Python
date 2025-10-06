import unittest
import io
from data_loader import load_from_reader
import csv
from models import MarketDataPoint
from datetime import datetime

class TestDataLoader(unittest.TestCase):
    def test_perfect(self):
       perfect_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-22T19:54:01.786263,IBM,144.79
2025-09-23T19:54:01.801212,MSFT,150.06
2025-09-21T19:54:01.816644,AAPL,154.48"""
       f = io.StringIO(perfect_string)
       reader = csv.DictReader(f)
       data = load_from_reader(reader)
       self.assertEqual(len(data), 4)
       self.assertEqual(data[0].symbol, "AAPL")
       self.assertAlmostEqual(data[0].price, 149.35)
       self.assertEqual(data[0].timestamp, datetime(year=2025, month=9, day=21, hour=19, minute=54, second=1, microsecond=774173))

       self.assertEqual(data[1].symbol, "IBM")
       self.assertAlmostEqual(data[1].price, 144.79)
       self.assertEqual(data[1].timestamp, datetime(year=2025, month=9, day=22, hour=19, minute=54, second=1, microsecond=786263))

       self.assertEqual(data[2].symbol, "MSFT")
       self.assertAlmostEqual(data[2].price, 150.06)
       self.assertEqual(data[2].timestamp, datetime(year=2025, month=9, day=23, hour=19, minute=54, second=1, microsecond=801212))

       self.assertEqual(data[3].symbol, "AAPL")
       self.assertAlmostEqual(data[3].price, 154.48)
       self.assertEqual(data[3].timestamp, datetime(year=2025, month=9, day=21, hour=19, minute=54, second=1, microsecond=816644))

    def test_bad_timestamp(self):
        bad_timestamp_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-22T19:hi:54,IBM,144.79
2025-09-23T19:54:01.801212,MSFT,150.06
2025-09-21T19:54:01.816644,AAPL,154.48"""
        f = io.StringIO(bad_timestamp_string)
        reader = csv.DictReader(f)
        with self.assertRaises(ValueError) as context:
            load_from_reader(reader)

    def test_bad_price(self):
        bad_timestamp_string = """timestamp,symbol,price
2025-09-21T19:54:01.774173,AAPL,149.35
2025-09-23T19:54:01.801212,MSFT,hi
2025-09-21T19:54:01.816644,AAPL,154.48"""
        f = io.StringIO(bad_timestamp_string)
        reader = csv.DictReader(f)
        with self.assertRaises(ValueError) as context:
            load_from_reader(reader)

if __name__ == "__main__":
    unittest.main()