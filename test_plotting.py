"""Pruebas del mapa político."""

import unittest
from unittest.mock import patch

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle, Rectangle

from interpretations import classify_position
from plotting import (
    QUADRANT_STYLES,
    SOCIAL_QUADRANT_STYLES,
    create_map,
    create_social_map,
)


class PlottingTests(unittest.TestCase):
    def test_map_places_point_at_received_coordinates(self):
        figure = create_map(37.5, -62.5)
        axis = figure.axes[0]

        point = axis.collections[0].get_offsets()[0]
        self.assertEqual(tuple(point), (37.5, -62.5))
        self.assertEqual(axis.get_xlim(), (-100.0, 100.0))
        self.assertEqual(axis.get_ylim(), (-100.0, 100.0))
        self.assertEqual(axis.get_aspect(), 1.0)

        labels = {text.get_text() for text in axis.texts}
        self.assertIn("EL RESUELVE", labels)
        self.assertIn("EL GERENTE PÚBLICO", labels)
        self.assertIn("EL CONECTADO", labels)
        self.assertIn("DÉJAME TRABAJAR", labels)
        self.assertIn("Tú\n37.5, -62.5", labels)

        plt.close(figure)

    def test_map_works_without_profile_images(self):
        with patch("plotting._load_profile_image", return_value=None):
            figure = create_map(0, 0)
            self.assertEqual(len(figure.axes), 1)
            plt.close(figure)

    def test_four_political_images_are_loaded_inside_safe_quadrant_zones(self):
        figure = create_map(0, 0)
        axis = figure.axes[0]

        self.assertEqual(len(axis.images), 4)
        for image_artist, style in zip(axis.images, QUADRANT_STYLES):
            self.assertEqual(tuple(image_artist.get_extent()), style["image_extent"])
            left, right, bottom, top = image_artist.get_extent()
            self.assertTrue(right <= -14 or left >= 14)
            self.assertTrue(top <= -18 or bottom >= 18)
            self.assertLess(image_artist.get_zorder(), axis.collections[0].get_zorder())

        plt.close(figure)

    def test_political_images_stay_below_axes_guides_and_user_label(self):
        figure = create_map(100, 100)
        axis = figure.axes[0]
        user_label = next(
            text for text in axis.texts if text.get_text().startswith("Tú\n")
        )

        self.assertTrue(all(image.get_zorder() == 2 for image in axis.images))
        self.assertEqual(axis.collections[0].get_zorder(), 10)
        self.assertEqual(user_label.get_zorder(), 11)
        self.assertTrue(all(line.get_zorder() >= 7 for line in axis.lines))
        plt.close(figure)

    def test_backgrounds_are_in_the_correct_quadrants(self):
        figure = create_map(0, 0)
        axis = figure.axes[0]
        backgrounds = [
            patch_object
            for patch_object in axis.patches
            if isinstance(patch_object, Rectangle)
            and patch_object.get_width() == 100
            and patch_object.get_height() == 100
        ]

        self.assertEqual(len(backgrounds), 4)
        for background, style in zip(backgrounds, QUADRANT_STYLES):
            left, bottom, width, height = style["rectangle"]
            self.assertEqual(background.get_xy(), (left, bottom))
            self.assertEqual(background.get_width(), width)
            self.assertEqual(background.get_height(), height)
            self.assertEqual(background.get_facecolor(), to_rgba(style["color"], 0.55))

        plt.close(figure)

    def test_exact_center_remains_visible(self):
        figure = create_map(0, 0)
        axis = figure.axes[0]
        center_circles = [
            patch_object
            for patch_object in axis.patches
            if isinstance(patch_object, Circle)
            and patch_object.center == (0, 0)
        ]
        labels = {text.get_text() for text in axis.texts}

        self.assertEqual(len(center_circles), 1)
        self.assertIn("centro", labels)
        plt.close(figure)

    def test_visual_changes_do_not_change_classifications(self):
        expected = {
            (0, 0): "Centro pragmático",
            (0, 40): "Gobierno activo equilibrado moderado",
            (0, -40): "Gobierno limitado equilibrado moderado",
            (40, 0): "Meritocrático de centro moderado",
            (-40, 0): "Pragmático de contactos moderado",
            (100, 100): "El Gerente Público convencido",
            (-100, 100): "El Resuelve convencido",
            (-100, -100): "El Conectado convencido",
            (100, -100): "Déjame Trabajar convencido",
        }

        for coordinates, expected_name in expected.items():
            with self.subTest(coordinates=coordinates):
                self.assertEqual(
                    classify_position(*coordinates)["name"],
                    expected_name,
                )

    def test_social_map_places_point_at_received_coordinates(self):
        figure = create_social_map(-37.5, 62.5)
        axis = figure.axes[0]
        point = axis.collections[0].get_offsets()[0]

        self.assertEqual(tuple(point), (-37.5, 62.5))
        self.assertEqual(axis.get_xlim(), (-100.0, 100.0))
        self.assertEqual(axis.get_ylim(), (-100.0, 100.0))
        self.assertEqual(axis.get_aspect(), 1.0)
        plt.close(figure)

    def test_social_backgrounds_are_in_the_correct_quadrants(self):
        figure = create_social_map(0, 0)
        axis = figure.axes[0]
        backgrounds = [
            patch_object
            for patch_object in axis.patches
            if isinstance(patch_object, Rectangle)
            and patch_object.get_width() == 100
            and patch_object.get_height() == 100
        ]

        self.assertEqual(len(backgrounds), 4)
        for background, style in zip(backgrounds, SOCIAL_QUADRANT_STYLES):
            left, bottom, width, height = style["rectangle"]
            self.assertEqual(background.get_xy(), (left, bottom))
            self.assertEqual(background.get_width(), width)
            self.assertEqual(background.get_height(), height)
            self.assertEqual(background.get_facecolor(), to_rgba(style["color"], 0.55))

        plt.close(figure)

    def test_both_maps_work_without_images(self):
        with patch("plotting._load_profile_image", return_value=None):
            political_figure = create_map(25, -25)
            social_figure = create_social_map(-25, 25)
            self.assertEqual(len(political_figure.axes), 1)
            self.assertEqual(len(social_figure.axes), 1)
            plt.close(political_figure)
            plt.close(social_figure)

    def test_point_labels_stay_inside_the_figure_at_all_extremes(self):
        extremes = ((100, 100), (-100, 100), (-100, -100), (100, -100))

        for map_builder in (create_map, create_social_map):
            for coordinates in extremes:
                with self.subTest(map=map_builder.__name__, coordinates=coordinates):
                    figure = map_builder(*coordinates)
                    figure.canvas.draw()
                    annotation = next(
                        text
                        for text in figure.axes[0].texts
                        if text.get_text().startswith("Tú\n")
                    )
                    label_box = annotation.get_window_extent(figure.canvas.get_renderer())
                    figure_box = figure.bbox
                    self.assertGreaterEqual(label_box.x0, figure_box.x0)
                    self.assertGreaterEqual(label_box.y0, figure_box.y0)
                    self.assertLessEqual(label_box.x1, figure_box.x1)
                    self.assertLessEqual(label_box.y1, figure_box.y1)
                    plt.close(figure)


if __name__ == "__main__":
    unittest.main()
