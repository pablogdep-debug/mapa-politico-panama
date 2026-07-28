"""Regresiones de los textos y del balance del eje de estilo político."""

import ast
from pathlib import Path
import unittest

from questions import QUESTIONS
from scoring import AXES, QUESTION_IDS, REVERSE_SCORED_IDS, calculate_scores


EXPECTED_TEXTS = (
    "Las decisiones públicas deberían basarse en la ciencia y la evidencia, aunque la solución más eficiente no le guste a la comunidad afectada.",
    "Prefiero un político que resuelva las urgencias de su gente hoy, aunque le quede menos tiempo para planes y leyes de largo plazo.",
    "Todas las familias —heterosexuales u homosexuales— deberían tener los mismos derechos, aunque eso cambie normas tradicionales sobre el matrimonio.",
    "En las comunidades más violentas, recuperar el orden va primero, aunque por un tiempo se posterguen los programas sociales y de empleo.",
    "Podría votar por candidatos de partidos distintos si me parecen los más capaces.",
    "El gobierno debería intervenir menos en la economía, aunque eso signifique menos subsidios y menos incentivos.",
    "Si estuviera en mis manos decidir los cargos de dirección del gobierno, preferiría nombrar a personas de confianza que compartan el proyecto político antes que a otras con mayor preparación técnica.",
    "Las leyes y la educación deberían reflejar los valores religiosos y las costumbres de Panamá, aunque no todos los compartan.",
    "La delincuencia se reduce más con educación, empleo y deporte para los jóvenes que con mano dura, aunque los resultados tarden más.",
    "Cuando una comunidad lleva años esperando una obra, es razonable comenzarla antes de completar todos los trámites, siempre que no se comprometan la seguridad ni el presupuesto.",
    "Ningún partido tiene mi voto asegurado. Debe ganárselo en cada elección, sin importar lo bien que me haya representado en el pasado.",
    "El gobierno debe poder ponerles reglas estrictas a industrias como la minería, aunque eso limite decisiones de las empresas.",
    "El Estado debería darle un reconocimiento especial a la familia tradicional por encima de otros modelos de familia.",
    "La policía necesita más autoridad para detener y requisar ante sospechas, aunque aumente el riesgo de revisar a personas inocentes.",
    "Panamá debería adoptar las nuevas tecnologías con rapidez, aunque algunos empleos tradicionales desaparezcan.",
    "Me parece normal que un gobierno dé prioridad para algunos puestos a quienes trabajaron en su campaña.",
    "Si un partido representa mis ideas, vale mantenerle la lealtad aunque no me convenzan todos sus candidatos.",
    "El Estado no debería meterse en cómo los adultos viven, forman pareja o crean familia, mientras no dañen a nadie.",
    "Prefiero que no suban los impuestos, aunque tenga que pagar por mi cuenta algunos servicios cuando los necesite.",
    "El progreso del país no debe dejar atrás nuestras tradiciones culturales y religiosas.",
    "La seguridad de los barrios mejora más cuando la policía se gana la confianza de la comunidad que cuando aumenta los patrullajes y retenes.",
    "Aceptaría pagar más impuestos si eso mejora la educación, la salud y los servicios públicos.",
    "El Estado debe fijar límites morales en temas que afectan a los menores, como la educación sexual, aunque algunas familias prefieran decidir solas.",
    "Los partidos fuertes ayudan a que los planes de país no se engaveten con cada gobierno nuevo, aunque dificulten la entrada de nuevas fuerzas.",
)

EXPECTED_AXES = {
    "x": {
        "name": "Mérito frente a favores",
        "positive": ("q07", "q16"),
        "opposite": ("q02", "q10"),
    },
    "y": {
        "name": "Gobierno activo",
        "positive": ("q12", "q22"),
        "opposite": ("q06", "q19"),
    },
    "seguridad": {
        "name": "Mano firme",
        "positive": ("q04", "q14"),
        "opposite": ("q09", "q21"),
    },
    "familia": {
        "name": "Autonomía familiar",
        "positive": ("q03", "q18"),
        "opposite": ("q13", "q23"),
    },
    "modernidad": {
        "name": "Ciencia y modernidad",
        "positive": ("q01", "q15"),
        "opposite": ("q08", "q20"),
    },
    "partidismo": {
        "name": "Voto independiente",
        "positive": ("q05", "q11"),
        "opposite": ("q17", "q24"),
    },
}


def neutral_answers():
    return {question_id: 3 for question_id in QUESTION_IDS}


def x_score(question_id, value):
    answers = neutral_answers()
    answers[question_id] = value
    return calculate_scores(answers)["x"]


def effective_style_poles():
    """Agrupa los ítems por su efecto numérico después de la recodificación."""
    rules_and_merit = []
    results_and_loyalties = []
    style_axis = AXES["x"]

    for side, base_direction in (("positive", 1), ("opposite", -1)):
        for question_id in style_axis[side]:
            direction = -base_direction if question_id in REVERSE_SCORED_IDS else base_direction
            target = rules_and_merit if direction > 0 else results_and_loyalties
            target.append(question_id)

    order = {question_id: index for index, question_id in enumerate(QUESTION_IDS)}
    return {
        "rules_and_merit": tuple(sorted(rules_and_merit, key=order.get)),
        "results_and_loyalties": tuple(sorted(results_and_loyalties, key=order.get)),
    }


def constant_from_app(name):
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f"No se encontró {name} en app.py")


class QuestionnaireV2Tests(unittest.TestCase):
    def test_exact_question_ids_order_count_and_texts(self):
        self.assertEqual(len(QUESTIONS), 24)
        self.assertEqual(
            tuple(question["id"] for question in QUESTIONS),
            QUESTION_IDS,
        )
        self.assertEqual(
            tuple(question["text"] for question in QUESTIONS),
            EXPECTED_TEXTS,
        )

    def test_axis_membership_and_all_other_polarities_are_unchanged(self):
        self.assertEqual(AXES, EXPECTED_AXES)
        self.assertEqual(REVERSE_SCORED_IDS, frozenset({"q07", "q16"}))

    def test_all_style_items_effectively_point_to_results_and_loyalties(self):
        poles = effective_style_poles()
        self.assertEqual(poles["rules_and_merit"], ())
        self.assertEqual(
            poles["results_and_loyalties"],
            ("q02", "q07", "q10", "q16"),
        )
        all_ids = poles["rules_and_merit"] + poles["results_and_loyalties"]
        self.assertEqual(len(all_ids), 4)
        self.assertEqual(len(set(all_ids)), 4)

    def test_each_style_item_has_the_required_contribution_table(self):
        expected = {
            1: 25.0,
            2: 12.5,
            3: 0.0,
            4: -12.5,
            5: -25.0,
        }
        for question_id in ("q02", "q07", "q10", "q16"):
            for value, contribution in expected.items():
                with self.subTest(question_id=question_id, value=value):
                    self.assertEqual(x_score(question_id, value), contribution)

    def test_q07_no_longer_keeps_its_old_positive_polarity(self):
        self.assertEqual(x_score("q07", 1), 25.0)
        self.assertEqual(x_score("q07", 5), -25.0)

    def test_q10_has_no_historical_or_double_inversion(self):
        self.assertEqual(x_score("q10", 1), 25.0)
        self.assertEqual(x_score("q10", 5), -25.0)

    def test_q02_and_q16_keep_their_negative_agreement_direction(self):
        for question_id in ("q02", "q16"):
            with self.subTest(question_id=question_id):
                self.assertEqual(x_score(question_id, 1), 25.0)
                self.assertEqual(x_score(question_id, 5), -25.0)

    def test_all_style_items_have_the_same_absolute_weight(self):
        effects = {
            question_id: abs(x_score(question_id, 4) - x_score(question_id, 3))
            for question_id in ("q02", "q07", "q10", "q16")
        }
        self.assertEqual(set(effects.values()), {12.5})

    def test_combined_style_axis_cases(self):
        cases = (
            ({"q02": 3, "q07": 3, "q10": 3, "q16": 3}, 0.0),
            ({"q02": 5, "q07": 5, "q10": 5, "q16": 5}, -100.0),
            ({"q02": 1, "q07": 1, "q10": 1, "q16": 1}, 100.0),
            ({"q02": 5, "q07": 5, "q10": 1, "q16": 1}, 0.0),
        )
        for style_answers, expected in cases:
            with self.subTest(style_answers=style_answers):
                answers = neutral_answers()
                answers.update(style_answers)
                self.assertEqual(calculate_scores(answers)["x"], expected)

    def test_each_style_item_is_monotonic_from_one_to_five(self):
        expected = [25.0, 12.5, 0.0, -12.5, -25.0]
        for question_id in ("q02", "q07", "q10", "q16"):
            with self.subTest(question_id=question_id):
                observed = [x_score(question_id, value) for value in range(1, 6)]
                self.assertEqual(observed, expected)
                self.assertEqual(observed, sorted(observed, reverse=True))

    def test_q11_keeps_its_independent_vote_direction(self):
        answers = neutral_answers()
        answers["q11"] = 5
        self.assertEqual(calculate_scores(answers)["partidismo"], 25.0)

    def test_q19_keeps_its_government_limited_contribution_table(self):
        expected = {
            1: 25.0,
            2: 12.5,
            3: 0.0,
            4: -12.5,
            5: -25.0,
        }
        for value, contribution in expected.items():
            with self.subTest(value=value):
                answers = neutral_answers()
                answers["q19"] = value
                self.assertEqual(calculate_scores(answers)["y"], contribution)

    def test_q13_keeps_its_traditional_family_direction(self):
        answers = neutral_answers()
        answers["q13"] = 1
        self.assertEqual(calculate_scores(answers)["familia"], 25.0)
        answers["q13"] = 5
        self.assertEqual(calculate_scores(answers)["familia"], -25.0)

    def test_q20_keeps_its_tradition_and_religion_direction(self):
        answers = neutral_answers()
        answers["q20"] = 1
        self.assertEqual(calculate_scores(answers)["modernidad"], 25.0)
        answers["q20"] = 5
        self.assertEqual(calculate_scores(answers)["modernidad"], -25.0)

    def test_q21_keeps_its_community_policing_direction(self):
        expected = {
            1: 25.0,
            2: 12.5,
            3: 0.0,
            4: -12.5,
            5: -25.0,
        }
        for value, contribution in expected.items():
            with self.subTest(value=value):
                answers = neutral_answers()
                answers["q21"] = value
                self.assertEqual(
                    calculate_scores(answers)["seguridad"],
                    contribution,
                )

    def test_new_records_use_version_2_2(self):
        self.assertEqual(constant_from_app("APP_VERSION"), "2.2")


if __name__ == "__main__":
    unittest.main()
