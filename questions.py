"""Preguntas y opciones del formulario político.

Este archivo solo guarda datos. Los cálculos se agregarán en otra etapa.
"""


# Cada texto se copió literalmente de los documentos del proyecto.
QUESTIONS = [
    {
        "id": "q01",
        "text": "La ciencia puede ayudar a resolver problemas técnicos y debería tener un peso importante en las decisiones de política pública, incluso cuando sus conclusiones no coincidan con la opinión de quienes viven en los lugares donde esas decisiones se aplican.",
    },
    {
        "id": "q02",
        "text": "Un buen político es quien resuelve problemas concretos para su gente, aunque no siempre impulse grandes reformas.",
    },
    {
        "id": "q03",
        "text": "Todas las familias, ya sean de padres heterosexuales u homosexuales, deberían recibir los mismos derechos y el mismo reconocimiento por parte del Estado.",
    },
    {
        "id": "q04",
        "text": "En comunidades con altos niveles de violencia, recuperar el orden debe ser la prioridad, incluso antes de resolver otros problemas sociales.",
    },
    {
        "id": "q05",
        "text": "No tendría problema en votar por candidatos de distintos partidos si considero que son las personas más capaces.",
    },
    {
        "id": "q06",
        "text": "Mientras menos intervenga el gobierno en la economía, ya sea con subsidios, incentivos o controles de precios, mayores serán las oportunidades para las personas y las empresas.",
    },
    {
        "id": "q07",
        "text": "Las instituciones del Estado deberían valorar más las capacidades de las personas y los resultados de sus buenas ideas que los compromisos políticos adquiridos con donantes o durante las campañas.",
    },
    {
        "id": "q08",
        "text": "Las leyes y la educación también deberían reflejar los valores culturales y religiosos que forman parte de la identidad panameña.",
    },
    {
        "id": "q09",
        "text": "La mejor forma de reducir la delincuencia es invertir más en educación, empleo, deporte y oportunidades para los jóvenes.",
    },
    {
        "id": "q10",
        "text": "Si un político demuestra que ayuda realmente a su comunidad, me parece razonable apoyarlo nuevamente con mi voto, ya sea que busque la reelección o aspire a otro cargo.",
    },
    {
        "id": "q11",
        "text": "Ningún partido debería contar con mi voto por costumbre; cada elección debe ganarse nuevamente.",
    },
    {
        "id": "q12",
        "text": "Hay situaciones en las que el gobierno debe intervenir para proteger a la población, aunque eso implique más regulaciones.",
    },
    {
        "id": "q13",
        "text": "Aunque existan distintos modelos de familia, el Estado debería dar un reconocimiento especial a la familia tradicional.",
    },
    {
        "id": "q14",
        "text": "Para enfrentar la delincuencia, la policía necesita contar con mayor autoridad y libertad para actuar con firmeza.",
    },
    {
        "id": "q15",
        "text": "Panamá debería adoptar nuevas tecnologías e innovaciones con rapidez, aunque eso transforme formas tradicionales de hacer las cosas o deje sin empleo a algunas personas.",
    },
    {
        "id": "q16",
        "text": "Cuando una persona ha trabajado activamente para que un proyecto político llegue al gobierno, es comprensible que espere ser tomada en cuenta para una oportunidad laboral si cumple con los requisitos del puesto.",
    },
    {
        "id": "q17",
        "text": "Cuando un partido representa bien mis ideas, considero importante mantenerle la lealtad aunque no me convenzan todos sus candidatos.",
    },
    {
        "id": "q18",
        "text": "Mientras no hagan daño a otras personas, el Estado no debería intervenir en las decisiones personales sobre cómo vivir, formar pareja o construir una familia.",
    },
    {
        "id": "q19",
        "text": "Prefiero pagar menos impuestos, aunque eso signifique que el Estado ofrezca menos servicios y ayudas.",
    },
    {
        "id": "q20",
        "text": "El progreso del país no debería lograrse sacrificando nuestras tradiciones culturales y religiosas.",
    },
    {
        "id": "q21",
        "text": "Dar demasiado poder a las fuerzas de seguridad puede terminar afectando los derechos de personas inocentes.",
    },
    {
        "id": "q22",
        "text": "Estoy dispuesto a pagar más impuestos si eso mejora de forma clara la educación, la salud y otros servicios públicos.",
    },
    {
        "id": "q23",
        "text": "Existen valores morales fundamentales que las leyes deberían proteger, aunque no toda la sociedad esté de acuerdo.",
    },
    {
        "id": "q24",
        "text": "Los partidos políticos fuertes son importantes porque dan estabilidad y continuidad a los proyectos del país.",
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
