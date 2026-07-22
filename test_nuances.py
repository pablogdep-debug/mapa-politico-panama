"""Pruebas de las barras centradas de Seguridad y Partidismo."""

import unittest

from nuances import build_nuance_bar


class NuanceTests(unittest.TestCase):
    def test_bars_use_the_complete_minus_one_hundred_to_one_hundred_range(self):
        for kind in ("seguridad", "partidismo"):
            with self.subTest(kind=kind):
                self.assertEqual(build_nuance_bar(kind, -100)["marker_percent"], 0)
                self.assertEqual(build_nuance_bar(kind, 0)["marker_percent"], 50)
                self.assertEqual(build_nuance_bar(kind, 100)["marker_percent"], 100)

    def test_positive_and_negative_fills_start_at_the_correct_place(self):
        negative = build_nuance_bar("seguridad", -40)
        positive = build_nuance_bar("partidismo", 40)

        self.assertEqual(negative["fill_left_percent"], 30)
        self.assertEqual(negative["fill_width_percent"], 20)
        self.assertEqual(positive["fill_left_percent"], 50)
        self.assertEqual(positive["fill_width_percent"], 20)

    def test_out_of_range_values_are_rejected(self):
        for value in (-101, 101):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    build_nuance_bar("seguridad", value)


if __name__ == "__main__":
    unittest.main()
