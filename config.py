"""Configuración pública y estática de Brújula Democrática."""


PATREON_URL = "https://www.patreon.com/BrujulaDemocratica"
INSTRUMENT_VERSION = "beta-1.0.4"


def instrument_version_display_text():
    """Convierte la versión interna en el texto discreto de la portada."""
    visible_version = INSTRUMENT_VERSION.replace("-", " ", 1)
    return f"Brújula Democrática · Versión {visible_version}"


def instrument_metadata():
    """Devuelve el campo de versión que acompaña cada respuesta nueva."""
    return {"instrument_version": INSTRUMENT_VERSION}
