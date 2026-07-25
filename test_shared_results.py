"""Pruebas del formato compartible sin datos personales."""

import base64
import json
import unittest

from shared_results import (
    build_share_url,
    build_social_message,
    decode_result,
    encode_result,
)


VALID_RESULT = {
    "x": 25.0,
    "y": -50.0,
    "familia": 12.5,
    "modernidad": 75.0,
    "seguridad": -37.5,
    "partidismo": 50.0,
}


def encode_raw(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


class SharedResultTests(unittest.TestCase):
    def test_round_trip_preserves_aggregate_scores(self):
        self.assertEqual(decode_result(encode_result(VALID_RESULT)), VALID_RESULT)

    def test_url_contains_only_one_encoded_result_parameter(self):
        url = build_share_url("https://example.com/?old=1", VALID_RESULT)
        self.assertTrue(url.startswith("https://example.com/?r="))
        self.assertNotIn("old=", url)
        self.assertNotIn("email", url.lower())
        self.assertNotIn("q01", url.lower())

    def test_rejects_unknown_fields(self):
        payload = {
            "v": 1, "p": "Centro pragmático",
            "sp": "Posición social pragmática",
            "x": 0, "y": 0, "sx": 0, "sy": 0, "seg": 0, "par": 0,
        }
        payload["email"] = "persona@example.com"
        self.assertIsNone(decode_result(encode_raw(payload)))

    def test_rejects_incomplete_payload(self):
        self.assertIsNone(decode_result(encode_raw({"v": 1, "x": 0})))

    def test_rejects_invalid_coordinates(self):
        payload = {
            "v": 1, "p": "Centro pragmático",
            "sp": "Posición social pragmática",
            "x": 101, "y": 0, "sx": 0, "sy": 0, "seg": 0, "par": 0,
        }
        self.assertIsNone(decode_result(encode_raw(payload)))

    def test_rejects_non_numeric_coordinates(self):
        payload = {
            "v": 1, "p": "Centro pragmático",
            "sp": "Posición social pragmática",
            "x": "0", "y": 0, "sx": 0, "sy": 0, "seg": 0, "par": 0,
        }
        self.assertIsNone(decode_result(encode_raw(payload)))

    def test_rejects_nonexistent_profile_data(self):
        payload = {
            "v": 1,
            "p": "Perfil inventado",
            "sp": "Posición social pragmática",
            "x": 0,
            "y": 0,
            "sx": 0,
            "sy": 0,
            "seg": 0,
            "par": 0,
        }
        self.assertIsNone(decode_result(encode_raw(payload)))

    def test_social_message_uses_both_profiles_and_signature(self):
        message = build_social_message(
            "El Resuelve",
            "Conservador moderno",
            "https://example.com/?r=abc",
        )
        self.assertIn("El Resuelve", message)
        self.assertIn("Conservador moderno", message)
        self.assertIn("https://example.com/?r=abc", message)
        self.assertTrue(message.endswith("Equipo de Brújula Democrática"))


if __name__ == "__main__":
    unittest.main()
