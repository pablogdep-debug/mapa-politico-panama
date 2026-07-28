"""Pruebas de los datos demográficos, independientes del scoring."""

import base64
import json
import unittest

from demographics import (
    AGE_FIELD_ID,
    AGE_RANGES,
    ALL_RESIDENCE_OPTIONS,
    DISTRICT_FIELD_ID,
    DISTRICTS_BY_REGION,
    EXTERIOR_OPTION,
    OFFICIAL_DISTRICT_OPTIONS,
    build_demographic_record,
    filter_residence_options,
    is_valid_age_range,
    is_valid_residence_option,
)
from questions import QUESTIONS
from scoring import AXES, calculate_scores
from shared_results import encode_result


EXPECTED_COUNTS = {
    "Bocas del Toro": 4,
    "Coclé": 6,
    "Colón": 6,
    "Chiriquí": 14,
    "Darién": 3,
    "Herrera": 7,
    "Los Santos": 7,
    "Panamá": 6,
    "Panamá Oeste": 5,
    "Veraguas": 12,
    "Comarca Emberá-Wounaan": 2,
    "Comarca Ngäbe-Buglé": 9,
    "Comarca Naso Tjër Di": 1,
}


class DemographicDataTests(unittest.TestCase):
    def test_questionnaire_still_has_24_political_questions(self):
        self.assertEqual(len(QUESTIONS), 24)
        self.assertEqual(
            [question["id"] for question in QUESTIONS],
            [f"q{number:02d}" for number in range(1, 25)],
        )

    def test_demographic_fields_are_not_political_question_ids(self):
        political_ids = {question["id"] for question in QUESTIONS}
        self.assertEqual(AGE_FIELD_ID, "dem_age_range")
        self.assertEqual(DISTRICT_FIELD_ID, "dem_district")
        self.assertNotIn(AGE_FIELD_ID, political_ids)
        self.assertNotIn(DISTRICT_FIELD_ID, political_ids)

    def test_demographic_fields_are_not_in_scoring_axes(self):
        scored_ids = {
            question_id
            for definition in AXES.values()
            for side in ("positive", "opposite")
            for question_id in definition[side]
        }
        self.assertNotIn(AGE_FIELD_ID, scored_ids)
        self.assertNotIn(DISTRICT_FIELD_ID, scored_ids)

    def test_age_ranges_are_exact(self):
        self.assertEqual(len(AGE_RANGES), 6)
        self.assertEqual(AGE_RANGES[0], "18 a 24 años")
        self.assertEqual(AGE_RANGES[-1], "65 años o más")

    def test_required_demographic_values_reject_empty_or_invented_data(self):
        self.assertFalse(is_valid_age_range(None))
        self.assertFalse(is_valid_age_range("17 años"))
        self.assertTrue(is_valid_age_range("25 a 34 años"))
        self.assertFalse(is_valid_residence_option(None))
        self.assertFalse(is_valid_residence_option("Distrito inventado"))
        self.assertTrue(is_valid_residence_option(EXTERIOR_OPTION))

    def test_district_counts_by_region_are_exact(self):
        counts = {
            region: len(districts)
            for region, districts in DISTRICTS_BY_REGION.items()
        }
        self.assertEqual(counts, EXPECTED_COUNTS)
        self.assertEqual(sum(counts.values()), 82)
        self.assertEqual(len(OFFICIAL_DISTRICT_OPTIONS), 82)

    def test_exterior_is_additional_and_not_official(self):
        self.assertFalse(EXTERIOR_OPTION.official)
        self.assertEqual(EXTERIOR_OPTION.region, "Exterior")
        self.assertEqual(EXTERIOR_OPTION.district, "Fuera de Panamá")
        self.assertNotIn(EXTERIOR_OPTION, OFFICIAL_DISTRICT_OPTIONS)
        self.assertEqual(ALL_RESIDENCE_OPTIONS[-1], EXTERIOR_OPTION)

    def test_no_duplicate_region_and_district_pairs(self):
        pairs = {
            (option.region, option.district)
            for option in OFFICIAL_DISTRICT_OPTIONS
        }
        self.assertEqual(len(pairs), 82)

    def test_repeated_santa_fe_districts_remain_distinct(self):
        labels = {
            option.label
            for option in OFFICIAL_DISTRICT_OPTIONS
            if option.district == "Santa Fe"
        }
        self.assertEqual(
            labels,
            {"Darién — Santa Fe", "Veraguas — Santa Fe"},
        )

    def test_search_ignores_case_and_accents(self):
        cases = {
            "chitre": "Herrera — Chitré",
            "PENONOME": "Coclé — Penonomé",
            "arraijan": "Panamá Oeste — Arraiján",
            "nurum": "Comarca Ngäbe-Buglé — Ñürüm",
        }
        for query, expected_label in cases.items():
            labels = {option.label for option in filter_residence_options(query)}
            self.assertIn(expected_label, labels)

    def test_demographics_do_not_change_known_scores(self):
        answers = {
            question["id"]: ((number * 3) % 5) + 1
            for number, question in enumerate(QUESTIONS, 1)
        }
        expected = {
            "x": -37.5,
            "y": -37.5,
            "seguridad": -12.5,
            "familia": 0.0,
            "modernidad": -12.5,
            "partidismo": 0.0,
        }
        self.assertEqual(calculate_scores(answers), expected)

    def test_demographics_are_excluded_from_shared_payload(self):
        scores = {
            "x": 37.5,
            "y": -37.5,
            "familia": 0.0,
            "modernidad": -12.5,
            "seguridad": -12.5,
            "partidismo": 0.0,
            "age_range": "25 a 34 años",
            "residence_region": "Panamá Oeste",
            "residence_district": "Arraiján",
        }
        encoded = encode_result(scores)
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        payload = json.loads(raw)
        self.assertNotIn("age_range", payload)
        self.assertNotIn("residence_region", payload)
        self.assertNotIn("residence_district", payload)
        self.assertNotIn("Arraiján", json.dumps(payload, ensure_ascii=False))

    def test_anonymous_demographic_record_has_only_three_expected_fields(self):
        record = build_demographic_record(
            "25 a 34 años",
            "Panamá Oeste",
            "Arraiján",
        )
        self.assertEqual(
            record,
            {
                "age_range": "25 a 34 años",
                "residence_region": "Panamá Oeste",
                "residence_district": "Arraiján",
            },
        )
        self.assertNotIn("email", record)


if __name__ == "__main__":
    unittest.main()
