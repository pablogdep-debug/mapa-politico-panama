"""Diseño visual del mapa político de dos ejes."""

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
from matplotlib.patches import Circle, Rectangle


PROFILES_DIR = Path(__file__).resolve().parent / "assets" / "profiles"
POLITICAL_ASSETS_DIR = PROFILES_DIR / "political"
SOCIAL_ASSETS_DIR = PROFILES_DIR / "social"


# Cada entrada define el fondo, los textos y el futuro personaje de un cuadrante.
QUADRANT_STYLES = (
    {
        "name": "EL RESUELVE",
        "phrase": "Ayuda, soluciones y resultados",
        "color": "#D8E8F3",
        "rectangle": (-100, 0, 100, 100),
        "title_position": (-50, 90),
        "image_extent": (-94, -14, 18, 72),
        "phrase_position": (-50, 80),
        "asset": "el_resuelve.png",
    },
    {
        "name": "EL GERENTE PÚBLICO",
        "phrase": "Capacidad, reglas claras y transparencia",
        "color": "#DCEEDB",
        "rectangle": (0, 0, 100, 100),
        "title_position": (50, 90),
        "image_extent": (14, 94, 18, 72),
        "phrase_position": (50, 80),
        "asset": "el_gerente_publico.png",
    },
    {
        "name": "EL CONECTADO",
        "phrase": "Menos trámites; los contactos ayudan",
        "color": "#F4E5C8",
        "rectangle": (-100, -100, 100, 100),
        "title_position": (-50, -90),
        "image_extent": (-94, -14, -72, -18),
        "phrase_position": (-50, -80),
        "asset": "el_conectado.png",
    },
    {
        "name": "DÉJAME TRABAJAR",
        "phrase": "Reglas iguales y libertad para producir",
        "color": "#E8DDF1",
        "rectangle": (0, -100, 100, 100),
        "title_position": (50, -90),
        "image_extent": (14, 94, -72, -18),
        "phrase_position": (50, -80),
        "asset": "dejame_trabajar.png",
    },
)


SOCIAL_QUADRANT_STYLES = (
    {
        "name": "CONSERVADOR MODERNO",
        "phrase": "Tradición familiar con confianza en la ciencia",
        "color": "#DCEBE8",
        "rectangle": (-100, 0, 100, 100),
        "title_position": (-50, 90),
        "image_position": (-50, 47),
        "phrase_position": (-50, 80),
        "asset": "conservador_moderno.png",
    },
    {
        "name": "PROGRESISTA MODERNO",
        "phrase": "Autonomía personal, derechos y modernidad",
        "color": "#DFE9F2",
        "rectangle": (0, 0, 100, 100),
        "title_position": (50, 90),
        "image_position": (50, 47),
        "phrase_position": (50, 80),
        "asset": "progresista_moderno.png",
    },
    {
        "name": "GUARDIÁN DE LA FAMILIA",
        "phrase": "Religión, costumbre y orden moral",
        "color": "#F2E0D6",
        "rectangle": (-100, -100, 100, 100),
        "title_position": (-50, -90),
        "image_position": (-50, -47),
        "phrase_position": (-50, -80),
        "asset": "guardian_de_la_familia.png",
    },
    {
        "name": "VIVE Y DEJA VIVIR",
        "phrase": "Autonomía personal y baja imposición moral",
        "color": "#EADFEA",
        "rectangle": (0, -100, 100, 100),
        "title_position": (50, -90),
        "image_position": (50, -47),
        "phrase_position": (50, -80),
        "asset": "vive_y_deja_vivir.png",
    },
)


def _load_profile_image(path):
    """Carga una imagen si existe; si falta o es inválida, devuelve None."""
    if not path.exists():
        return None

    try:
        return plt.imread(path)
    except (OSError, ValueError):
        return None


def _add_profile_image(axis, image, extent):
    """Coloca una ilustración tenue dentro de una zona segura del cuadrante."""
    # Las ilustraciones ya traen su nombre y lema en la franja inferior.
    # Esa franja se recorta para no repetir los textos del propio mapa.
    visible_height = max(1, int(image.shape[0] * 0.82))
    illustration = image[:visible_height].copy()

    # Los PNG entregados tienen un fondo blanco. Lo convertimos en una
    # transparencia gradual para conservar los bordes suaves de la acuarela.
    if illustration.ndim == 3 and illustration.shape[2] >= 3:
        rgb = illustration[..., :3].astype(float)
        if rgb.max() > 1:
            rgb /= 255
        white_distance = 1 - rgb.min(axis=2)
        soft_alpha = np.clip(white_distance / 0.065, 0, 1) * 0.88
        if illustration.shape[2] == 4:
            original_alpha = illustration[..., 3].astype(float)
            if original_alpha.max() > 1:
                original_alpha /= 255
            soft_alpha *= original_alpha
        illustration = np.dstack((rgb, soft_alpha))

    axis.imshow(
        illustration,
        extent=extent,
        interpolation="bilinear",
        zorder=2,
    )


def _draw_quadrants(axis):
    """Dibuja fondos, nombres, frases y personajes disponibles."""
    for style in QUADRANT_STYLES:
        left, bottom, width, height = style["rectangle"]
        background = Rectangle(
            (left, bottom),
            width,
            height,
            facecolor=style["color"],
            edgecolor="none",
            alpha=0.55,
            zorder=0,
        )
        axis.add_patch(background)

        axis.text(
            *style["title_position"],
            style["name"],
            ha="center",
            va="center",
            fontfamily="DejaVu Sans",
            fontsize=15,
            fontweight="bold",
            fontstretch="semi-expanded",
            color="#25313B",
            zorder=8,
        )
        axis.text(
            *style["phrase_position"],
            textwrap.fill(style["phrase"], width=31),
            ha="center",
            va="center",
            fontfamily="DejaVu Sans",
            fontsize=7.2,
            fontweight="normal",
            color="#46515A",
            linespacing=1.05,
            zorder=8,
        )

        image = _load_profile_image(POLITICAL_ASSETS_DIR / style["asset"])
        if image is not None:
            _add_profile_image(axis, image, style["image_extent"])


def _draw_social_quadrants(axis):
    """Dibuja el sistema visual y las imágenes opcionales del plano social."""
    for style in SOCIAL_QUADRANT_STYLES:
        left, bottom, width, height = style["rectangle"]
        axis.add_patch(
            Rectangle(
                (left, bottom),
                width,
                height,
                facecolor=style["color"],
                edgecolor="none",
                alpha=0.55,
                zorder=0,
            )
        )
        axis.text(
            *style["title_position"],
            style["name"],
            ha="center",
            va="center",
            fontfamily="DejaVu Sans",
            fontsize=13,
            fontweight="bold",
            fontstretch="semi-expanded",
            color="#25313B",
            zorder=8,
        )
        axis.text(
            *style["phrase_position"],
            textwrap.fill(style["phrase"], width=31),
            ha="center",
            va="center",
            fontfamily="DejaVu Sans",
            fontsize=7.2,
            fontweight="normal",
            color="#46515A",
            linespacing=1.05,
            zorder=8,
        )

        image = _load_profile_image(SOCIAL_ASSETS_DIR / style["asset"])
        if image is not None:
            # El plano social conserva el soporte opcional anterior.
            largest_side = max(image.shape[0], image.shape[1])
            size = 90 / largest_side
            height = image.shape[0] * size
            width = image.shape[1] * size
            center_x, center_y = style["image_position"]
            axis.imshow(
                image,
                extent=(
                    center_x - width / 2,
                    center_x + width / 2,
                    center_y - height / 2,
                    center_y + height / 2,
                ),
                alpha=0.46,
                interpolation="bilinear",
                zorder=2,
            )


def _draw_center_and_boundaries(axis):
    """Resalta suavemente el centro y las posiciones sobre los ejes."""
    center = Circle(
        (0, 0),
        radius=7,
        facecolor="#FFFFFF",
        edgecolor="#778188",
        linewidth=0.8,
        alpha=0.48,
        zorder=6,
    )
    axis.add_patch(center)
    axis.text(
        0,
        -9,
        "centro",
        ha="center",
        va="center",
        fontsize=5.8,
        fontweight="normal",
        color="#657078",
        zorder=7,
    )


def _point_label_layout(x, y):
    """Mantiene la etiqueta dentro del mapa incluso cerca de sus bordes."""
    horizontal_alignment = "right" if x >= 72 else "left"
    vertical_alignment = "top" if y >= 72 else "bottom"
    horizontal_offset = -11 if x >= 72 else 11
    vertical_offset = -11 if y >= 72 else 11
    return horizontal_offset, vertical_offset, horizontal_alignment, vertical_alignment


def create_map(x, y):
    """Crea el mapa y coloca el punto exactamente en las coordenadas recibidas."""
    figure, axis = plt.subplots(figsize=(8, 8))

    axis.set_xlim(-100, 100)
    axis.set_ylim(-100, 100)
    _draw_quadrants(axis)
    _draw_center_and_boundaries(axis)

    axis.grid(True, linestyle="--", linewidth=0.7, alpha=0.35, zorder=5)
    axis.axhline(0, color="#44515A", linewidth=1.5, zorder=7)
    axis.axvline(0, color="#44515A", linewidth=1.5, zorder=7)

    # Las guías y el punto quedan por encima de fondos, textos e imágenes.
    axis.plot([x, x], [0, y], color="#252A2E", linewidth=1.5, linestyle=":", zorder=9)
    axis.plot([0, x], [y, y], color="#252A2E", linewidth=1.5, linestyle=":", zorder=9)
    axis.scatter(
        x,
        y,
        s=250,
        color="#E63946",
        edgecolors="#111111",
        linewidths=2.5,
        zorder=10,
    )

    horizontal_offset, vertical_offset, horizontal_alignment, vertical_alignment = (
        _point_label_layout(x, y)
    )
    point_label = axis.annotate(
        f"Tú\n{x:.1f}, {y:.1f}",
        (x, y),
        xytext=(horizontal_offset, vertical_offset),
        textcoords="offset points",
        ha=horizontal_alignment,
        va=vertical_alignment,
        fontsize=9.2,
        fontweight="bold",
        color="white",
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "#18232C",
            "edgecolor": "white",
            "linewidth": 1.2,
            "alpha": 0.96,
        },
        zorder=11,
    )
    point_label.get_bbox_patch().set_path_effects(
        [path_effects.SimplePatchShadow(offset=(1, -1), alpha=0.22), path_effects.Normal()]
    )

    axis.set_xlabel("Favores y contactos  ←  →  Mérito y capacidad")
    axis.set_ylabel("Gobierno pequeño  ←  →  Gobierno activo")
    axis.set_title(
        "Estado y forma de hacer política",
        loc="left",
        fontsize=18,
        fontweight="bold",
        color="#1F2B33",
        pad=16,
    )
    axis.set_aspect("equal")
    figure.tight_layout()

    return figure


def create_social_map(x_social, y_social):
    """Crea una versión sencilla del plano de familia y modernidad."""
    figure, axis = plt.subplots(figsize=(8, 8))

    _draw_social_quadrants(axis)

    axis.set_xlim(-100, 100)
    axis.set_ylim(-100, 100)
    axis.add_patch(
        Circle(
            (0, 0),
            radius=7,
            facecolor="white",
            edgecolor="#778188",
            linewidth=0.8,
            alpha=0.48,
            zorder=5,
        )
    )
    axis.text(
        0,
        -9,
        "centro social",
        ha="center",
        va="center",
        fontsize=5.6,
        fontweight="normal",
        color="#657078",
        zorder=6,
    )

    axis.grid(True, linestyle="--", linewidth=0.7, alpha=0.35, zorder=4)
    axis.axhline(0, color="#44515A", linewidth=1.5, zorder=7)
    axis.axvline(0, color="#44515A", linewidth=1.5, zorder=7)
    axis.plot(
        [x_social, x_social],
        [0, y_social],
        color="#252A2E",
        linewidth=1.5,
        linestyle=":",
        zorder=8,
    )
    axis.plot(
        [0, x_social],
        [y_social, y_social],
        color="#252A2E",
        linewidth=1.5,
        linestyle=":",
        zorder=8,
    )
    axis.scatter(
        x_social,
        y_social,
        s=250,
        color="#E63946",
        edgecolors="#111111",
        linewidths=2.5,
        zorder=10,
    )
    social_x_offset, social_y_offset, social_ha, social_va = _point_label_layout(
        x_social, y_social
    )
    social_point_label = axis.annotate(
        f"Tú\n{x_social:.1f}, {y_social:.1f}",
        (x_social, y_social),
        xytext=(social_x_offset, social_y_offset),
        textcoords="offset points",
        ha=social_ha,
        va=social_va,
        fontsize=9.2,
        fontweight="bold",
        color="white",
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "#18232C",
            "edgecolor": "white",
            "linewidth": 1.2,
            "alpha": 0.96,
        },
        zorder=11,
    )
    social_point_label.get_bbox_patch().set_path_effects(
        [path_effects.SimplePatchShadow(offset=(1, -1), alpha=0.22), path_effects.Normal()]
    )

    axis.set_xlabel(
        "Tradición moral y familia tradicional  ←  →  "
        "Autonomía personal y diversidad"
    )
    axis.set_ylabel(
        "Costumbre, religión y autoridad moral  ←  →  "
        "Ciencia, secularidad y modernización"
    )
    axis.set_title(
        "Valores sociales, familia y modernidad",
        loc="left",
        fontsize=18,
        fontweight="bold",
        color="#1F2B33",
        pad=16,
    )
    axis.set_aspect("equal")
    figure.tight_layout()
    return figure
