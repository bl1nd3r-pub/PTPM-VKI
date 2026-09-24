import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.delivery_service import calculate_delivery_cost

INVALID = (-1, "0000-00-00")


class TestDeliveryCostValidation(unittest.TestCase):
    def test_delivery_rejects_weight_below_minimum(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), INVALID)

    def test_delivery_rejects_weight_above_maximum(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"), INVALID)

    def test_delivery_accepts_weight_bounds_inclusive(self):
        result = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertEqual(result[0], 700)
        result = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertEqual(result[0], 1050)

    def test_delivery_rejects_distance_below_minimum(self):
        self.assertEqual(calculate_delivery_cost(1.0, 0, "обычный"), INVALID)

    def test_delivery_rejects_distance_above_maximum(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный"), INVALID)

    def test_delivery_accepts_distance_bounds_inclusive(self):
        self.assertEqual(calculate_delivery_cost(1.0, 1, "обычный")[0], 205)
        self.assertEqual(calculate_delivery_cost(1.0, 5000, "обычный")[0], 25200)

    def test_delivery_rejects_unknown_package_type(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "стекло"), INVALID)


class TestDeliveryCostCalculation(unittest.TestCase):
    def test_delivery_base_tariff_for_light_small_parcel(self):
        self.assertEqual(calculate_delivery_cost(3.0, 100, "обычный"), (700, "2026-09-04"))

    def test_delivery_applies_140_percent_surcharge_for_medium_weight(self):
        self.assertEqual(calculate_delivery_cost(10.0, 100, "обычный"), (840, "2026-09-04"))

    def test_delivery_applies_150_percent_surcharge_for_heavy_weight(self):
        self.assertEqual(calculate_delivery_cost(20.0, 100, "обычный"), (1050, "2026-09-04"))

    def test_delivery_no_surcharge_for_weight_exactly_five_kg(self):
        self.assertEqual(calculate_delivery_cost(5.0, 100, "обычный"), (700, "2026-09-04"))

    def test_delivery_fragile_package_adds_surcharge(self):
        self.assertEqual(calculate_delivery_cost(3.0, 100, "хрупкий"), (1000, "2026-09-04"))

    def test_delivery_dangerous_package_adds_surcharge(self):
        self.assertEqual(calculate_delivery_cost(3.0, 100, "опасный"), (1700, "2026-09-04"))


class TestDeliveryTiming(unittest.TestCase):
    def test_delivery_minimum_delivery_time_is_one_day(self):
        self.assertEqual(calculate_delivery_cost(3.0, 1, "обычный")[1], "2026-09-04")

    def test_delivery_time_grows_with_distance(self):
        self.assertEqual(calculate_delivery_cost(3.0, 1500, "обычный")[1], "2026-09-06")

    def test_express_delivery_returns_sooner_than_regular(self):
        regular_date = calculate_delivery_cost(3.0, 4620, "обычный")[1]
        express_date = calculate_delivery_cost(3.0, 4620, "обычный", is_express=True)[1]
        self.assertLess(express_date, regular_date)

    def test_express_delivery_should_cost_more_than_regular(self):
        regular_cost = calculate_delivery_cost(3.0, 100, "обычный")[0]
        express_cost = calculate_delivery_cost(3.0, 100, "обычный", is_express=True)[0]
        self.assertGreater(express_cost, regular_cost)


if __name__ == "__main__":
    unittest.main()