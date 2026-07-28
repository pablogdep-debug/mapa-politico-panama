"""Preguntas y opciones del formulario político.

Este archivo solo guarda datos. Los cálculos se agregarán en otra etapa.
"""


# Cada texto se copió literalmente de los documentos del proyecto.
QUESTIONS = [
    {
        "id": "q01",
        "text": "Las decisiones públicas deberían basarse en la ciencia y la evidencia, aunque la solución más eficiente no le guste a la comunidad afectada.",
    },
    {
        "id": "q02",
        "text": "Prefiero un político que resuelva las urgencias de su gente hoy, aunque le quede menos tiempo para planes y leyes de largo plazo.",
    },
    {
        "id": "q03",
        "text": "Todas las familias —heterosexuales u homosexuales— deberían tener los mismos derechos, aunque eso cambie normas tradicionales sobre el matrimonio.",
    },
    {
        "id": "q04",
        "text": "En las comunidades más violentas, recuperar el orden va primero, aunque por un tiempo se posterguen los programas sociales y de empleo.",
    },
    {
        "id": "q05",
        "text": "Podría votar por candidatos de partidos distintos si me parecen los más capaces.",
    },
    {
        "id": "q06",
        "text": "El gobierno debería intervenir menos en la economía, aunque eso signifique menos subsidios y menos incentivos.",
    },
    {
        "id": "q07",
        "text": "Si estuviera en mis manos decidir los cargos de dirección del gobierno, preferiría nombrar a personas de confianza que compartan el proyecto político antes que a otras con mayor preparación técnica.",
    },
    {
        "id": "q08",
        "text": "Las leyes y la educación deberían reflejar los valores religiosos y las costumbres de Panamá, aunque no todos los compartan.",
    },
    {
        "id": "q09",
        "text": "La delincuencia se reduce más con educación, empleo y deporte para los jóvenes que con mano dura, aunque los resultados tarden más.",
    },
    {
        "id": "q10",
        "text": "Cuando una comunidad lleva años esperando una obra, es razonable comenzarla antes de completar todos los trámites, siempre que no se comprometan la seguridad ni el presupuesto.",
    },
    {
        "id": "q11",
        "text": "Ningún partido tiene mi voto asegurado. Debe ganárselo en cada elección, sin importar lo bien que me haya representado en el pasado.",
    },
    {
        "id": "q12",
        "text": "El gobierno debe poder ponerles reglas estrictas a industrias como la minería, aunque eso limite decisiones de las empresas.",
    },
    {
        "id": "q13",
        "text": "El Estado debería darle un reconocimiento especial a la familia tradicional por encima de otros modelos de familia.",
    },
    {
        "id": "q14",
        "text": "La policía necesita más autoridad para detener y requisar ante sospechas, aunque aumente el riesgo de revisar a personas inocentes.",
    },
    {
        "id": "q15",
        "text": "Panamá debería adoptar las nuevas tecnologías con rapidez, aunque algunos empleos tradicionales desaparezcan.",
    },
    {
        "id": "q16",
        "text": "Me parece normal que un gobierno dé prioridad para algunos puestos a quienes trabajaron en su campaña.",
    },
    {
        "id": "q17",
        "text": "Si un partido representa mis ideas, vale mantenerle la lealtad aunque no me convenzan todos sus candidatos.",
    },
    {
        "id": "q18",
        "text": "El Estado no debería meterse en cómo los adultos viven, forman pareja o crean familia, mientras no dañen a nadie.",
    },
    {
        "id": "q19",
        "text": "Prefiero que no suban los impuestos, aunque tenga que pagar por mi cuenta algunos servicios cuando los necesite.",
    },
    {
        "id": "q20",
        "text": "El progreso del país no debe dejar atrás nuestras tradiciones culturales y religiosas.",
    },
    {
        "id": "q21",
        "text": "La seguridad de los barrios mejora más cuando la policía se gana la confianza de la comunidad que cuando aumenta los patrullajes y retenes.",
    },
    {
        "id": "q22",
        "text": "Aceptaría pagar más impuestos si eso mejora la educación, la salud y los servicios públicos.",
    },
    {
        "id": "q23",
        "text": "El Estado debe fijar límites morales en temas que afectan a los menores, como la educación sexual, aunque algunas familias prefieran decidir solas.",
    },
    {
        "id": "q24",
        "text": "Los partidos fuertes ayudan a que los planes de país no se engaveten con cada gobierno nuevo, aunque dificulten la entrada de nuevas fuerzas.",
    },
]


# El texto que ve la persona se convierte en un número del 1 al 5.
LIKERT_OPTIONS = {
    "Totalmente en desacuerdo": 1,
    "En desacuerdo": 2,
    "Ni de acuerdo ni en desacuerdo": 3,
    "De acuerdo": 4,
    "Totalmente de acuerdo": 5,
}
