"""Codificación segura y mínima de resultados para enlaces compartibles."""

import base64
import json
from urllib.parse import quote

from interpretations import classify_position
from social import classify_social_position


FORMAT_VERSION = 1
PAYLOAD_FIELDS = frozenset({"v", "p", "sp", "x", "y", "sx", "sy", "seg", "par"})
RESULT_FIELDS = ("x", "y", "familia", "modernidad", "seguridad", "partidismo")


def _valid_score(value):
    """Acepta números reales finitos dentro del rango de los mapas."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and -100 <= value <= 100
    )


def build_shared_result(scores):
    """Extrae exclusivamente los seis resultados agregados necesarios."""
    if set(RESULT_FIELDS) - set(scores):
        raise ValueError("Faltan resultados necesarios")

    result = {field: scores[field] for field in RESULT_FIELDS}
    if not all(_valid_score(value) for value in result.values()):
        raise ValueError("Los resultados deben estar entre -100 y 100")
    return result


def encode_result(scores):
    """Convierte resultados agregados en un payload JSON URL-safe."""
    result = build_shared_result(scores)
    payload = {
        "v": FORMAT_VERSION,
        "p": classify_position(result["x"], result["y"])["name"],
        "sp": classify_social_position(
            result["familia"],
            result["modernidad"],
        )["name"],
        "x": result["x"],
        "y": result["y"],
        "sx": result["familia"],
        "sy": result["modernidad"],
        "seg": result["seguridad"],
        "par": result["partidismo"],
    }
    raw = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_result(encoded):
    """Valida y reconstruye un resultado; devuelve ``None`` si es inválido."""
    try:
        if not isinstance(encoded, str) or not encoded or len(encoded) > 500:
            return None
        padding = "=" * (-len(encoded) % 4)
        raw = base64.b64decode(
            encoded + padding,
            altchars=b"-_",
            validate=True,
        )
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict) or set(payload) != PAYLOAD_FIELDS:
        return None
    if payload["v"] != FORMAT_VERSION:
        return None

    if not isinstance(payload["p"], str) or not isinstance(payload["sp"], str):
        return None

    values = [payload[key] for key in ("x", "y", "sx", "sy", "seg", "par")]
    if not all(_valid_score(value) for value in values):
        return None

    result = {
        "x": payload["x"],
        "y": payload["y"],
        "familia": payload["sx"],
        "modernidad": payload["sy"],
        "seguridad": payload["seg"],
        "partidismo": payload["par"],
    }

    # Las clasificaciones se reconstruyen con las funciones metodológicas reales.
    political = classify_position(result["x"], result["y"])
    social = classify_social_position(result["familia"], result["modernidad"])
    if (
        not political.get("name")
        or not social.get("name")
        or payload["p"] != political["name"]
        or payload["sp"] != social["name"]
    ):
        return None
    return result


def build_share_url(base_url, scores):
    """Crea la URL pública sin respuestas individuales ni datos personales."""
    clean_base = base_url.split("?", 1)[0].rstrip("/")
    return f"{clean_base}/?r={encode_result(scores)}"


def build_social_message(political_name, social_name, share_url):
    """Genera el texto neutral y breve que acompaña el enlace."""
    return (
        "Ya descubrí dónde caí en la Brújula Democrática 🧭\n\n"
        f"Mis resultados fueron: {political_name} y {social_name}.\n\n"
        "¿Tú caerás cerca de mí o en el otro extremo de la brújula? "
        "Completa el cuestionario y descúbrelo:\n\n"
        f"{share_url}\n\n"
        "Equipo de Brújula Democrática"
    )


def whatsapp_share_url(message):
    """Devuelve el enlace oficial de WhatsApp con el mensaje codificado."""
    return f"https://wa.me/?text={quote(message)}"


def facebook_share_url(share_url):
    """Devuelve el diálogo público de Facebook para compartir una URL."""
    return f"https://www.facebook.com/sharer/sharer.php?u={quote(share_url)}"
