"""Fuente única de la versión del instrumento político."""


INSTRUMENT_VERSION = "beta-1.0.4"


def instrument_version_display_text() -> str:
    """Convierte la versión interna en el texto discreto de la portada."""
    version_number = INSTRUMENT_VERSION.removeprefix("beta-")
    return f"Brújula Democrática · Versión beta {version_number}"


def instrument_metadata():
    """Devuelve el campo de versión que acompaña cada respuesta nueva."""
    return {"instrument_version": INSTRUMENT_VERSION}
