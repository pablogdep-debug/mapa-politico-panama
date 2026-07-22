"""Clasificación e interpretación del segundo plano político-social."""

from interpretations import calculate_intensity


SOCIAL_PROFILE_TEXTS = {
    "Conservador moderno": (
        "Combinas valores familiares tradicionales con apertura a la ciencia "
        "y la modernización."
    ),
    "Progresista moderno": (
        "Valoras la autonomía personal, la diversidad, la ciencia y la "
        "modernización."
    ),
    "Guardián de la familia": (
        "Priorizas la familia tradicional, la costumbre, la religión y la "
        "autoridad moral."
    ),
    "Vive y deja vivir": (
        "Defiendes la autonomía personal y la diversidad, aunque mantienes "
        "cercanía con la costumbre y la tradición."
    ),
}


def social_axis_position(x, y):
    """Devuelve la categoría propia de una posición sobre un eje social."""
    if x == 0 and y > 0:
        return "Modernización social equilibrada"
    if x == 0 and y < 0:
        return "Tradición social equilibrada"
    if y == 0 and x > 0:
        return "Autonomía social de centro"
    if y == 0 and x < 0:
        return "Tradición familiar de centro"
    return None


def social_profile_by_quadrant(x, y):
    """Devuelve un perfil solamente dentro de uno de los cuatro cuadrantes."""
    if x == 0 or y == 0:
        return None
    if x < 0 and y > 0:
        return "Conservador moderno"
    if x > 0 and y > 0:
        return "Progresista moderno"
    if x < 0 and y < 0:
        return "Guardián de la familia"
    return "Vive y deja vivir"


def social_quadrant_name(profile, intensity):
    """Aplica a un perfil social los mismos umbrales del primer plano."""
    if intensity < 12:
        return f"Posición social pragmática con ligera tendencia a {profile}"
    if intensity < 25:
        return f"Pragmático con tendencia a {profile}"
    if intensity < 45:
        return f"{profile} moderado"
    if intensity < 70:
        return profile
    return f"{profile} convencido"


def social_axis_name(name, intensity):
    """Aplica las categorías de intensidad propias de una frontera."""
    if intensity < 12:
        return f"{name} con ligera tendencia"
    if intensity < 25:
        return f"{name} pragmática"
    if intensity < 45:
        return f"{name} moderada"
    return name


def classify_social_position(x, y):
    """Clasifica las coordenadas familia y modernidad sin alterar su valor."""
    intensity = calculate_intensity(x, y)

    if x == 0 and y == 0:
        return {
            "profile": None,
            "position_type": "center",
            "name": "Posición social pragmática",
            "intensity": intensity,
        }

    axis_name = social_axis_position(x, y)
    if axis_name is not None:
        return {
            "profile": None,
            "position_type": "axis",
            "name": social_axis_name(axis_name, intensity),
            "intensity": intensity,
        }

    profile = social_profile_by_quadrant(x, y)
    return {
        "profile": profile,
        "position_type": "quadrant",
        "name": social_quadrant_name(profile, intensity),
        "intensity": intensity,
    }


def describe_social(classification):
    """Genera una explicación breve para el segundo plano."""
    position_type = classification["position_type"]

    if position_type == "center":
        return (
            "Tu posición social está exactamente en el centro y combina ideas "
            "de distintas perspectivas."
        )
    if position_type == "axis":
        return (
            "Tu posición está exactamente sobre uno de los ejes sociales, "
            "por lo que no pertenece arbitrariamente a ningún cuadrante."
        )

    profile = classification["profile"]
    intensity = classification["intensity"]
    if intensity < 12:
        introduction = "Estás muy cerca del centro social."
    elif intensity < 25:
        introduction = f"Te inclinas de forma pragmática hacia {profile}."
    elif intensity < 45:
        introduction = f"Tu posición social es {profile}, de forma moderada."
    elif intensity < 70:
        introduction = f"Tienes una posición social clara como {profile}."
    else:
        introduction = f"Tienes una identificación social intensa como {profile}."

    return introduction + " " + SOCIAL_PROFILE_TEXTS[profile]
