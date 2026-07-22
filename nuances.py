"""Presentación de Seguridad y Partidismo como matices visuales."""


NUANCE_CONFIG = {
    "seguridad": {
        "name": "Seguridad",
        "negative": "Prevención y límites policiales",
        "positive": "Mano firme",
    },
    "partidismo": {
        "name": "Relación con los partidos",
        "negative": "Fidelidad partidaria",
        "positive": "Voto independiente",
    },
}


def _validate_value(value):
    """Comprueba que el valor pueda representarse en la escala visual."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("El matiz debe ser un número entre -100 y 100.")
    if value < -100 or value > 100:
        raise ValueError("El matiz debe estar entre -100 y 100.")


def describe_nuance(kind, value):
    """Explica brevemente el signo y la intensidad sin crear otro perfil."""
    _validate_value(value)
    if kind not in NUANCE_CONFIG:
        raise ValueError("Matiz desconocido.")
    config = NUANCE_CONFIG[kind]

    if value == 0:
        return f"Mantienes un equilibrio entre {config['negative'].lower()} y {config['positive'].lower()}."

    magnitude = abs(value)
    if magnitude < 25:
        degree = "ligera"
    elif magnitude < 45:
        degree = "moderada"
    elif magnitude < 70:
        degree = "clara"
    else:
        degree = "fuerte"

    direction = config["positive"] if value > 0 else config["negative"]
    return f"Muestras una preferencia {degree} por {direction.lower()}."


def build_nuance_bar(kind, value):
    """Calcula la posición del marcador y el relleno en una barra -100 a 100."""
    if kind not in NUANCE_CONFIG:
        raise ValueError("Matiz desconocido.")
    _validate_value(value)

    marker = (value + 100) / 2
    return {
        **NUANCE_CONFIG[kind],
        "value": float(value),
        "marker_percent": marker,
        "fill_left_percent": min(50, marker),
        "fill_width_percent": abs(marker - 50),
        "description": describe_nuance(kind, value),
    }
