"""Pruebas de la clasificación del segundo plano social."""

import unittest

from social import classify_social_position, social_profile_by_quadrant


class SocialClassificationTests(unittest.TestCase):
    def test_social_center(self):
        result = classify_social_position(0, 0)
        self.assertEqual(result["name"], "Posición social pragmática")
        self.assertEqual(result["intensity"], 0.0)
        self.assertIsNone(result["profile"])
        self.assertEqual(result["position_type"], "center")

    def test_four_social_quadrants(self):
        cases = {
            (-40, 40): "Conservador moderno",
            (40, 40): "Progresista moderno",
            (-40, -40): "Guardián de la familia",
            (40, -40): "Vive y deja vivir",
        }
        for coordinates, expected_profile in cases.items():
            with self.subTest(coordinates=coordinates):
                self.assertEqual(
                    social_profile_by_quadrant(*coordinates),
                    expected_profile,
                )

    def test_four_social_axis_positions(self):
        cases = {
            (0, 40): "Modernización social equilibrada moderada",
            (0, -40): "Tradición social equilibrada moderada",
            (40, 0): "Autonomía social de centro moderada",
            (-40, 0): "Tradición familiar de centro moderada",
        }
        for coordinates, expected_name in cases.items():
            with self.subTest(coordinates=coordinates):
                result = classify_social_position(*coordinates)
                self.assertEqual(result["name"], expected_name)
                self.assertIsNone(result["profile"])
                self.assertEqual(result["position_type"], "axis")

    def test_social_extremes(self):
        cases = {
            (100, 100): "Progresista moderno convencido",
            (-100, 100): "Conservador moderno convencido",
            (-100, -100): "Guardián de la familia convencido",
            (100, -100): "Vive y deja vivir convencido",
        }
        for coordinates, expected_name in cases.items():
            with self.subTest(coordinates=coordinates):
                result = classify_social_position(*coordinates)
                self.assertEqual(result["name"], expected_name)
                self.assertEqual(result["intensity"], 100.0)

    def test_social_maximum_intensity_is_one_hundred_percent(self):
        self.assertEqual(
            classify_social_position(100, 100)["intensity"],
            100.0,
        )


if __name__ == "__main__":
    unittest.main()
