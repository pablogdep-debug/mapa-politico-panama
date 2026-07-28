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
    "En los puestos públicos, la preparación debe pesar más que la confianza política, aunque el elegido venga de la oposición.",
    "Las leyes y la educación deberían reflejar los valores religiosos y las costumbres de Panamá, aunque no todos los compartan.",
    "La delincuencia se reduce más con educación, empleo y deporte para los jóvenes que con mano dura, aunque los resultados tarden más.",
    "Prefiero que el gobierno respete los procedimientos y controles, aunque eso haga más lenta la ejecución de obras y soluciones.",
    "Ningún partido debería tener mi voto asegurado: debe ganárselo en cada elección, aunque me haya representado bien antes.",
    "El gobierno debe poder ponerles reglas estrictas a industrias como la minería, aunque eso limite decisiones de las empresas.",
    "El Estado debería darle un reconocimiento especial a la familia tradicional, aunque los demás modelos de familia también tengan protección legal.",
    "La policía necesita más autoridad para detener y requisar ante sospechas, aunque aumente el riesgo de revisar a personas inocentes.",
    "Panamá debería adoptar las nuevas tecnologías con rapidez, aunque algunos empleos tradicionales desaparezcan.",
    "Es entendible que quien trabajó en una campaña espere un puesto en el gobierno que ayudó a elegir.",
    "Si un partido representa mis ideas, vale mantenerle la lealtad aunque no me convenzan todos sus candidatos.",
    "El Estado no debería meterse en cómo los adultos viven, forman pareja o crean familia, mientras no dañen a nadie.",
    "Prefiero pagar menos impuestos, aunque haya menos mantenimiento de calles, menos inversión en escuelas y servicios más limitados.",
    "El progreso del país no debe dejar atrás nuestras tradiciones culturales y religiosas, aunque algunos prefieran una vida pública más neutral.",
    "Darle demasiado poder a las fuerzas de seguridad termina afectando a personas inocentes.",
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
        self.assertEqual(REVERSE_SCORED_IDS, frozenset({"q10", "q16"}))

    def test_style_axis_has_two_unique_questions_per_pole(self):
        poles = effective_style_poles()
        self.assertEqual(poles["rules_and_merit"], ("q07", "q10"))
        self.assertEqual(poles["results_and_loyalties"], ("q02", "q16"))
        all_ids = poles["rules_and_merit"] + poles["results_and_loyalties"]
        self.assertEqual(len(all_ids), 4)
        self.assertEqual(len(set(all_ids)), 4)

    def test_q16_neutral_is_neutral(self):
        self.assertEqual(x_score("q16", 3), 0.0)

    def test_q16_agreement_reduces_merit(self):
        self.assertEqual(x_score("q16", 4), -12.5)
        self.assertEqual(x_score("q16", 5), -25.0)

    def test_q16_disagreement_increases_merit(self):
        self.assertEqual(x_score("q16", 2), 12.5)
        self.assertEqual(x_score("q16", 1), 25.0)

    def test_q16_is_symmetric_and_monotonic(self):
        observed = [x_score("q16", value) for value in range(1, 6)]
        self.assertEqual(observed, [25.0, 12.5, 0.0, -12.5, -25.0])
        self.assertEqual(observed, sorted(observed, reverse=True))

    def test_q07_and_q16_point_in_opposite_directions(self):
        self.assertEqual(x_score("q07", 5), 25.0)
        self.assertEqual(x_score("q16", 5), -25.0)

    def test_q02_and_q16_agreement_share_results_direction(self):
        for question_id in ("q02", "q16"):
            with self.subTest(question_id=question_id):
                self.assertEqual(x_score(question_id, 5), -25.0)

    def test_q16_absolute_weight_matches_other_x_questions(self):
        effects = {
            question_id: abs(x_score(question_id, 4) - x_score(question_id, 3))
            for question_id in ("q07", "q16", "q02", "q10")
        }
        self.assertEqual(set(effects.values()), {12.5})

    def test_q10_neutral_is_neutral(self):
        self.assertEqual(x_score("q10", 3), 0.0)

    def test_q10_agreement_increases_rules_and_merit(self):
        self.assertEqual(x_score("q10", 4), 12.5)
        self.assertEqual(x_score("q10", 5), 25.0)

    def test_q10_disagreement_increases_results_and_loyalties(self):
        self.assertEqual(x_score("q10", 2), -12.5)
        self.assertEqual(x_score("q10", 1), -25.0)

    def test_q10_is_symmetric_and_monotonic(self):
        observed = [x_score("q10", value) for value in range(1, 6)]
        self.assertEqual(observed, [-25.0, -12.5, 0.0, 12.5, 25.0])
        self.assertEqual(observed, sorted(observed))
        self.assertEqual(abs(observed[0]), abs(observed[-1]))

    def test_q07_and_q10_agreement_share_rules_direction(self):
        self.assertEqual(x_score("q07", 5), 25.0)
        self.assertEqual(x_score("q10", 5), 25.0)

    def test_q10_agreement_opposes_q02_and_q16_agreement(self):
        self.assertEqual(x_score("q10", 5), 25.0)
        self.assertEqual(x_score("q02", 5), -25.0)
        self.assertEqual(x_score("q16", 5), -25.0)

    def test_new_records_use_version_2_1(self):
        self.assertEqual(constant_from_app("APP_VERSION"), "2.1")


if __name__ == "__main__":
    unittest.main()
