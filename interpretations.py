"""Clasificación e interpretación breve del resultado principal."""

import math


PROFILE_TEXTS = {
    "El Resuelve": (
        "Valoras un gobierno que ayude y resuelva problemas concretos para su gente."
    ),
    "El Gerente Público": (
        "Quieres un gobierno activo, pero manejado con capacidad, reglas claras "
        "y transparencia."
    ),
    "El Conectado": (
        "Prefieres menos trámites, aunque ves los contactos políticos como una "
        "forma útil de resolver."
    ),
    "Déjame Trabajar": (
        "Prefieres reglas iguales, menos burocracia y menos dependencia de "
        "contactos políticos."
    ),
}


def axis_position(x, y):
    """Devuelve el nombre propio de una posición exactamente sobre un eje."""
    if x == 0 and y > 0:
        return "Gobierno activo equilibrado"
    if x == 0 and y < 0:
        return "Gobierno limitado equilibrado"
    if y == 0 and x > 0:
        return "Meritocrático de centro"
    if y == 0 and x < 0:
        return "Pragmático de contactos"
    return None


def profile_by_quadrant(x, y):
    """Devuelve un perfil solo cuando el punto está dentro de un cuadrante."""
    if x == 0 or y == 0:
        return None
    if x > 0 and y > 0:
        return "El Gerente Público"
    if x < 0 and y > 0:
        return "El Resuelve"
    if x < 0 and y < 0:
        return "El Conectado"
    return "Déjame Trabajar"


def calculate_intensity(x, y):
    """Calcula la distancia al centro como porcentaje del máximo posible."""
    maximum_distance = math.sqrt(100**2 + 100**2)
    intensity = math.sqrt(x**2 + y**2) / maximum_distance * 100
    return round(intensity, 1)


def position_name(profile, intensity):
    """Combina el perfil con el nivel de intensidad indicado en la guía."""
    if intensity < 12:
        return f"Centro pragmático con ligera tendencia a {profile}"
    if intensity < 25:
        return f"Pragmático con tendencia a {profile}"
    if intensity < 45:
        return f"{profile} moderado"
    if intensity < 70:
        return profile
    return f"{profile} convencido"


def axis_position_name(name, intensity):
    """Aplica a los ejes sus categorías de intensidad específicas."""
    if intensity < 12:
        return f"{name} con ligera tendencia"
    if intensity < 25:
        return f"{name} pragmático"
    if intensity < 45:
        return f"{name} moderado"
    return name


def classify_position(x, y):
    """Devuelve perfil, nombre completo e intensidad para un punto."""
    intensity = calculate_intensity(x, y)

    if x == 0 and y == 0:
        return {
            "profile": None,
            "position_type": "center",
            "name": "Centro pragmático",
            "intensity": intensity,
        }

    axis_name = axis_position(x, y)
    if axis_name is not None:
        return {
            "profile": None,
            "position_type": "axis",
            "name": axis_position_name(axis_name, intensity),
            "intensity": intensity,
        }

    profile = profile_by_quadrant(x, y)
    return {
        "profile": profile,
        "position_type": "quadrant",
        "name": position_name(profile, intensity),
        "intensity": intensity,
    }


def describe(classification):
    """Produce el párrafo breve que combina intensidad y perfil."""
    position_type = classification["position_type"]

    if position_type == "center":
        return "Estás exactamente en el centro y combinas ideas de varios perfiles."

    if position_type == "axis":
        return (
            "Tu posición está exactamente sobre uno de los ejes del mapa, "
            "por lo que no pertenece arbitrariamente a ningún cuadrante."
        )

    profile = classification["profile"]
    intensity = classification["intensity"]

    if intensity < 12:
        introduction = (
            "Estás muy cerca del centro y combinas ideas de varios perfiles."
        )
    elif intensity < 25:
        introduction = f"Estás cerca del centro, pero te inclinas hacia {profile}."
    elif intensity < 45:
        introduction = f"Tu orientación es {profile}, aunque de forma moderada."
    elif intensity < 70:
        introduction = f"Tienes una orientación clara hacia {profile}."
    else:
        introduction = (
            f"Tienes una identificación bastante intensa con {profile}."
        )

    return introduction + " " + PROFILE_TEXTS[profile]
