"""Preguntas y opciones del formulario político.

Este archivo solo guarda datos. Los cálculos se agregarán en otra etapa.
"""


# Cada texto se copió literalmente de los documentos del proyecto.
QUESTIONS = [
    {
        "id": "q01",
        "text": "Las decisiones del gobierno deberían basarse primero en la ciencia, aunque choquen con algunas costumbres o creencias religiosas.",
    },
    {
        "id": "q02",
        "text": "Para mí, un buen político es alguien que resuelve problemas concretos para su gente.",
    },
    {
        "id": "q03",
        "text": "Todas las familias deberían tener los mismos derechos, aunque no sean una familia tradicional.",
    },
    {
        "id": "q04",
        "text": "En los lugares peligrosos, lo primero debe ser recuperar el orden, aunque algunas medidas sean fuertes.",
    },
    {
        "id": "q05",
        "text": "Yo podría votar por personas de distintos partidos, dependiendo de quién me parezca más capaz.",
    },
    {
        "id": "q06",
        "text": "La gente y las empresas funcionarían mejor sin que el gobierno estuviera diciéndoles todo el tiempo qué pueden o no pueden hacer.",
    },
    {
        "id": "q07",
        "text": "Dar puestos o contratos a amigos del partido le hace daño al país, aunque esas personas hayan trabajado por el político.",
    },
    {
        "id": "q08",
        "text": "Las leyes y lo que se enseña en las escuelas deberían tomar en cuenta los valores religiosos y las costumbres de Panamá.",
    },
    {
        "id": "q09",
        "text": "La delincuencia se reduce mejor dando más educación, trabajo, deporte y oportunidades en los barrios.",
    },
    {
        "id": "q10",
        "text": "Es normal apoyar a un político que ayuda a conseguir trabajo, becas, contratos o soluciones para la gente que lo respalda.",
    },
    {
        "id": "q11",
        "text": "Ningún partido debería recibir el voto para siempre; cada candidato tiene que ganárselo.",
    },
    {
        "id": "q12",
        "text": "Hay momentos en que el gobierno tiene que poner reglas claras para evitar abusos y proteger a la mayoría.",
    },
    {
        "id": "q13",
        "text": "El gobierno debería defender especialmente la familia formada por un hombre, una mujer y sus hijos.",
    },
    {
        "id": "q14",
        "text": "Para bajar la delincuencia, la policía necesita más presencia en las calles y más libertad para actuar con firmeza.",
    },
    {
        "id": "q15",
        "text": "Panamá debería aceptar nuevas tecnologías y nuevas ideas, aunque eso cambie algunas formas antiguas de hacer las cosas.",
    },
    {
        "id": "q16",
        "text": "Los puestos y contratos del gobierno deberían dárselos a los más preparados, aunque no tengan contactos políticos.",
    },
    {
        "id": "q17",
        "text": "Cuando alguien se identifica con un partido, debería seguir apoyándolo aunque no le gusten todos sus candidatos.",
    },
    {
        "id": "q18",
        "text": "El gobierno no debería meterse en cómo los adultos deciden vivir su vida, formar pareja o crear una familia.",
    },
    {
        "id": "q19",
        "text": "El gobierno debería cobrar menos impuestos y poner menos trámites, aunque también pueda ofrecer menos ayudas y servicios.",
    },
    {
        "id": "q20",
        "text": "Para avanzar como país, no deberíamos dejar de lado nuestras tradiciones religiosas y culturales.",
    },
    {
        "id": "q21",
        "text": "Darle demasiado poder a la policía puede terminar en abusos contra gente inocente.",
    },
    {
        "id": "q22",
        "text": "Vale la pena pagar más impuestos si eso sirve para mejorar la educación, la salud y las ayudas para quienes más lo necesitan.",
    },
    {
        "id": "q23",
        "text": "Hay valores morales que deberían protegerse por ley, aunque no todo el mundo esté de acuerdo.",
    },
    {
        "id": "q24",
        "text": "Es importante mantenerse fiel a un partido, incluso cuando está pasando por un mal momento.",
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
