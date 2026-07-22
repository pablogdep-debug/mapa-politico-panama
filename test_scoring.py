"""Pruebas automáticas para la lógica de puntuación."""

import unittest

from scoring import AXES, QUESTION_IDS, calculate_axis, calculate_scores


def answers_with(value):
    """Crea las 24 respuestas con el mismo valor."""
    return {question_id: value for question_id in QUESTION_IDS}


class ScoringTests(unittest.TestCase):
    def test_all_neutral_answers_give_zero(self):
        self.assertEqual(
            calculate_scores(answers_with(3)),
            {axis_id: 0.0 for axis_id in AXES},
        )

    def test_all_answers_at_one_give_zero(self):
        self.assertEqual(
            calculate_scores(answers_with(1)),
            {axis_id: 0.0 for axis_id in AXES},
        )

    def test_all_answers_at_five_give_zero(self):
        self.assertEqual(
            calculate_scores(answers_with(5)),
            {axis_id: 0.0 for axis_id in AXES},
        )

    def test_clearly_positive_profile_in_each_axis(self):
        for target_axis, axis in AXES.items():
            with self.subTest(axis=target_axis):
                answers = answers_with(3)
                for question_id in axis["positive"]:
                    answers[question_id] = 5
                for question_id in axis["opposite"]:
                    answers[question_id] = 1

                expected = {axis_id: 0.0 for axis_id in AXES}
                expected[target_axis] = 100.0
                self.assertEqual(calculate_scores(answers), expected)

    def test_clearly_opposite_profile_in_each_axis(self):
        for target_axis, axis in AXES.items():
            with self.subTest(axis=target_axis):
                answers = answers_with(3)
                for question_id in axis["positive"]:
                    answers[question_id] = 1
                for question_id in axis["opposite"]:
                    answers[question_id] = 5

                expected = {axis_id: 0.0 for axis_id in AXES}
                expected[target_axis] = -100.0
                self.assertEqual(calculate_scores(answers), expected)

    def test_result_matches_a_manual_calculation(self):
        # Positivas: (5 + 4) / 2 = 4.5
        # Contrarias: (2 + 4) / 2 = 3.0
        # ((4.5 - 3.0) / 4) * 100 = 37.5
        answers = answers_with(3)
        answers.update({"q07": 5, "q16": 4, "q02": 2, "q10": 4})
        self.assertEqual(
            calculate_axis(answers, ("q07", "q16"), ("q02", "q10")),
            37.5,
        )

    def test_all_six_axes_match_manual_calculations(self):
        answers = answers_with(3)

        # Diferencias manuales: 4, 2, 1, -1, -2 y -4.
        settings = {
            "x": ((5, 5), (1, 1)),
            "y": ((4, 4), (2, 2)),
            "seguridad": ((4, 3), (2, 3)),
            "familia": ((2, 3), (4, 3)),
            "modernidad": ((2, 2), (4, 4)),
            "partidismo": ((1, 1), (5, 5)),
        }

        for axis_id, (positive_values, opposite_values) in settings.items():
            axis = AXES[axis_id]
            for question_id, value in zip(axis["positive"], positive_values):
                answers[question_id] = value
            for question_id, value in zip(axis["opposite"], opposite_values):
                answers[question_id] = value

        self.assertEqual(
            calculate_scores(answers),
            {
                "x": 100.0,
                "y": 50.0,
                "seguridad": 25.0,
                "familia": -25.0,
                "modernidad": -50.0,
                "partidismo": -100.0,
            },
        )

    def test_incomplete_answers_are_rejected(self):
        answers = answers_with(3)
        del answers["q24"]
        with self.assertRaises(ValueError):
            calculate_scores(answers)

    def test_unknown_question_is_rejected(self):
        answers = answers_with(3)
        answers["q25"] = 3
        with self.assertRaises(ValueError):
            calculate_scores(answers)

    def test_values_outside_the_scale_are_rejected(self):
        for invalid_value in (0, 6, -1, 3.5, "3", True, None):
            with self.subTest(value=invalid_value):
                answers = answers_with(3)
                answers["q01"] = invalid_value
                with self.assertRaises(ValueError):
                    calculate_scores(answers)

    def test_non_dictionary_answers_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_scores([3] * 24)


if __name__ == "__main__":
    unittest.main()
