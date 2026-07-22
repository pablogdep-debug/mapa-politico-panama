"""Cálculo de los seis ejes del cuestionario político.

Cada resultado queda entre -100 y 100. Este módulo solo calcula números;
los gráficos y las interpretaciones pertenecen a etapas posteriores.
"""


# Estas son las 24 respuestas que debe recibir el cálculo.
QUESTION_IDS = tuple(f"q{number:02d}" for number in range(1, 25))


# Las claves coinciden con las usadas en la guía: x, y y cuatro distintivos.
# En cada eje se guardan primero las preguntas positivas y luego las contrarias.
AXES = {
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


def validate_answers(answers):
    """Comprueba que estén las 24 respuestas y que todas valgan del 1 al 5."""
    if not isinstance(answers, dict):
        raise ValueError("Las respuestas deben estar guardadas en un diccionario.")

    expected = set(QUESTION_IDS)
    received = set(answers)
    missing = sorted(expected - received)
    unexpected = sorted(received - expected)

    if missing or unexpected:
        details = []
        if missing:
            details.append("faltan " + ", ".join(missing))
        if unexpected:
            details.append("sobran " + ", ".join(unexpected))
        raise ValueError("Respuestas incompletas o desconocidas: " + "; ".join(details))

    for question_id, value in answers.items():
        # bool no se acepta aunque Python lo considere parecido a un entero.
        if isinstance(value, bool) or not isinstance(value, int) or value not in range(1, 6):
            raise ValueError(f"{question_id} debe tener un valor entero del 1 al 5.")


def average(answers, question_ids):
    """Devuelve el promedio de las preguntas indicadas."""
    return sum(answers[question_id] for question_id in question_ids) / len(question_ids)


def calculate_axis(answers, positive_ids, opposite_ids):
    """Calcula un eje con la fórmula exacta de la guía."""
    positive_average = average(answers, positive_ids)
    opposite_average = average(answers, opposite_ids)
    difference = positive_average - opposite_average
    return round((difference / 4) * 100, 1)


def calculate_scores(answers):
    """Valida las respuestas y devuelve por separado los seis resultados."""
    validate_answers(answers)

    return {
        axis_id: calculate_axis(
            answers,
            axis["positive"],
            axis["opposite"],
        )
        for axis_id, axis in AXES.items()
    }
