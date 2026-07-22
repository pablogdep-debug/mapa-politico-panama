"""Pruebas de clasificación e interpretación."""

import unittest

from interpretations import (
    PROFILE_TEXTS,
    calculate_intensity,
    classify_position,
    describe,
    profile_by_quadrant,
)


class InterpretationTests(unittest.TestCase):
    def test_exact_center(self):
        result = classify_position(0, 0)
        self.assertIsNone(result["profile"])
        self.assertEqual(result["position_type"], "center")
        self.assertEqual(result["intensity"], 0.0)
        self.assertEqual(result["name"], "Centro pragmático")

    def test_center_and_axis_positions_have_their_own_classifications(self):
        cases = {
            (0, 0): "Centro pragmático",
            (0, 40): "Gobierno activo equilibrado moderado",
            (0, -40): "Gobierno limitado equilibrado moderado",
            (40, 0): "Meritocrático de centro moderado",
            (-40, 0): "Pragmático de contactos moderado",
        }

        for coordinates, expected_name in cases.items():
            with self.subTest(coordinates=coordinates):
                result = classify_position(*coordinates)
                self.assertEqual(result["name"], expected_name)
                self.assertIsNone(result["profile"])
                self.assertIn(result["position_type"], {"center", "axis"})

    def test_axis_positions_use_their_specific_intensity_labels(self):
        cases = {
            (0, 10): "Gobierno activo equilibrado con ligera tendencia",
            (0, 20): "Gobierno activo equilibrado pragmático",
            (0, 40): "Gobierno activo equilibrado moderado",
            (0, 70): "Gobierno activo equilibrado",
        }

        for coordinates, expected_name in cases.items():
            with self.subTest(coordinates=coordinates):
                self.assertEqual(
                    classify_position(*coordinates)["name"],
                    expected_name,
                )

    def test_four_quadrants(self):
        cases = {
            (-10, 10): "El Resuelve",
            (10, 10): "El Gerente Público",
            (-10, -10): "El Conectado",
            (10, -10): "Déjame Trabajar",
        }
        for coordinates, expected in cases.items():
            with self.subTest(coordinates=coordinates):
                self.assertEqual(profile_by_quadrant(*coordinates), expected)

    def test_intensity_thresholds(self):
        cases = {
            11.9: "Centro pragmático con ligera tendencia a El Gerente Público",
            12.0: "Pragmático con tendencia a El Gerente Público",
            12.1: "Pragmático con tendencia a El Gerente Público",
            24.9: "Pragmático con tendencia a El Gerente Público",
            25.0: "El Gerente Público moderado",
            25.1: "El Gerente Público moderado",
            44.9: "El Gerente Público moderado",
            45.0: "El Gerente Público",
            45.1: "El Gerente Público",
            69.9: "El Gerente Público",
            70.0: "El Gerente Público convencido",
            70.1: "El Gerente Público convencido",
        }
        # Cuando x e y son iguales, el porcentaje radial es ese mismo número.
        for intensity, expected_name in cases.items():
            with self.subTest(intensity=intensity):
                result = classify_position(intensity, intensity)
                self.assertEqual(result["intensity"], intensity)
                self.assertEqual(result["name"], expected_name)

    def test_positive_extreme(self):
        result = classify_position(100, 100)
        self.assertEqual(result["profile"], "El Gerente Público")
        self.assertEqual(result["intensity"], 100.0)

    def test_negative_extreme(self):
        result = classify_position(-100, -100)
        self.assertEqual(result["profile"], "El Conectado")
        self.assertEqual(result["intensity"], 100.0)

    def test_maximum_intensity_is_one_hundred_percent(self):
        self.assertEqual(calculate_intensity(100, 100), 100.0)
        self.assertEqual(calculate_intensity(-100, -100), 100.0)

    def test_description_matches_profile_and_intensity(self):
        cases = [
            ((-5, 5), "Estás muy cerca del centro", "El Resuelve"),
            ((20, 20), "Estás cerca del centro", "El Gerente Público"),
            ((-30, -30), "Tu orientación es", "El Conectado"),
            ((80, -80), "Tienes una identificación bastante intensa", "Déjame Trabajar"),
        ]
        for coordinates, expected_start, profile in cases:
            with self.subTest(coordinates=coordinates):
                classification = classify_position(*coordinates)
                paragraph = describe(classification)
                self.assertTrue(paragraph.startswith(expected_start))
                self.assertTrue(paragraph.endswith(PROFILE_TEXTS[profile]))


if __name__ == "__main__":
    unittest.main()
