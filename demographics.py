"""Datos demográficos anónimos, separados de las preguntas políticas."""

import unicodedata
from typing import NamedTuple


AGE_FIELD_ID = "dem_age_range"
DISTRICT_FIELD_ID = "dem_district"

AGE_RANGES = (
    "18 a 24 años",
    "25 a 34 años",
    "35 a 44 años",
    "45 a 54 años",
    "55 a 64 años",
    "65 años o más",
)

DISTRICTS_BY_REGION = {
    "Bocas del Toro": (
        "Almirante",
        "Bocas del Toro",
        "Changuinola",
        "Chiriquí Grande",
    ),
    "Coclé": (
        "Aguadulce",
        "Antón",
        "La Pintada",
        "Natá",
        "Olá",
        "Penonomé",
    ),
    "Colón": (
        "Chagres",
        "Colón",
        "Donoso",
        "Omar Torrijos Herrera",
        "Portobelo",
        "Santa Isabel",
    ),
    "Chiriquí": (
        "Alanje",
        "Barú",
        "Boquerón",
        "Boquete",
        "Bugaba",
        "David",
        "Dolega",
        "Gualaca",
        "Remedios",
        "Renacimiento",
        "San Félix",
        "San Lorenzo",
        "Tierras Altas",
        "Tolé",
    ),
    "Darién": (
        "Chepigana",
        "Pinogana",
        "Santa Fe",
    ),
    "Herrera": (
        "Chitré",
        "Las Minas",
        "Los Pozos",
        "Ocú",
        "Parita",
        "Pesé",
        "Santa María",
    ),
    "Los Santos": (
        "Guararé",
        "Las Tablas",
        "Los Santos",
        "Macaracas",
        "Pedasí",
        "Pocrí",
        "Tonosí",
    ),
    "Panamá": (
        "Balboa",
        "Chepo",
        "Chimán",
        "Panamá",
        "San Miguelito",
        "Taboga",
    ),
    "Panamá Oeste": (
        "Arraiján",
        "Capira",
        "Chame",
        "La Chorrera",
        "San Carlos",
    ),
    "Veraguas": (
        "Atalaya",
        "Calobre",
        "Cañazas",
        "La Mesa",
        "Las Palmas",
        "Mariato",
        "Montijo",
        "Río de Jesús",
        "San Francisco",
        "Santa Fe",
        "Santiago",
        "Soná",
    ),
    "Comarca Emberá-Wounaan": (
        "Cémaco",
        "Sambú",
    ),
    "Comarca Ngäbe-Buglé": (
        "Besikó",
        "Jirondai",
        "Kankintú",
        "Kusapín",
        "Mironó",
        "Müna",
        "Nole Duima",
        "Ñürüm",
        "Santa Catalina o Calovébora (Bledeshia)",
    ),
    "Comarca Naso Tjër Di": (
        "Distrito Especial Naso Tjër Di",
    ),
}


class DistrictOption(NamedTuple):
    """Conserva territorio, distrito y etiqueta como valores independientes."""

    region: str
    district: str
    label: str
    official: bool = True


EXTERIOR_OPTION = DistrictOption(
    region="Exterior",
    district="Fuera de Panamá",
    label="Exterior — Resido fuera de Panamá",
    official=False,
)


def normalize_text(value):
    """Permite buscar sin distinguir mayúsculas, minúsculas ni tildes."""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def build_official_district_options():
    """Construye las 82 opciones oficiales en el orden territorial indicado."""
    options = []
    for region, districts in DISTRICTS_BY_REGION.items():
        for district in sorted(districts, key=normalize_text):
            options.append(
                DistrictOption(
                    region=region,
                    district=district,
                    label=f"{region} — {district}",
                )
            )
    return tuple(options)


OFFICIAL_DISTRICT_OPTIONS = build_official_district_options()
ALL_RESIDENCE_OPTIONS = OFFICIAL_DISTRICT_OPTIONS + (EXTERIOR_OPTION,)


def filter_residence_options(query):
    """Filtra las opciones sin aceptar valores territoriales inventados."""
    normalized_query = normalize_text(query.strip())
    if not normalized_query:
        return ALL_RESIDENCE_OPTIONS
    return tuple(
        option
        for option in ALL_RESIDENCE_OPTIONS
        if normalized_query in normalize_text(option.label)
    )


def is_valid_age_range(value):
    """Impide continuar si no se eligió uno de los seis rangos permitidos."""
    return value in AGE_RANGES


def is_valid_residence_option(value):
    """Impide continuar con texto libre u opciones territoriales inventadas."""
    return value in ALL_RESIDENCE_OPTIONS


def build_demographic_record(age_range, region, district):
    """Prepara los tres campos para un futuro registro anónimo agregado."""
    return {
        "age_range": age_range,
        "residence_region": region,
        "residence_district": district,
    }
