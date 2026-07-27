"""Preguntas y opciones del formulario político.

Este archivo solo guarda datos. Los cálculos se agregarán en otra etapa.
"""


# Cada texto se copió literalmente de los documentos del proyecto.
QUESTIONS = [
    {
        "id": "q01",
        "text": "La ciencia y la evidencia técnica deberían pesar mucho en las decisiones públicas, incluso cuando la solución más eficiente no guste a la comunidad afectada. Por ejemplo, un hospital puede ubicarse donde atienda a más personas, aunque los vecinos del lugar escogido se opongan.",
    },
    {
        "id": "q02",
        "text": "Un buen político debe atender las necesidades inmediatas de su gente. Puede responder a urgencias, apoyar a damnificados o ayudar a familias en dificultades, aunque eso deje menos tiempo y recursos para proyectos de largo plazo, como trabajar en comisiones, elaborar planes estratégicos o crear nuevas leyes.",
    },
    {
        "id": "q03",
        "text": "Todas las familias, formadas por parejas heterosexuales u homosexuales, deberían recibir los mismos derechos y el mismo reconocimiento del Estado. Esto puede exigir cambios en normas tradicionales sobre el matrimonio y la familia.",
    },
    {
        "id": "q04",
        "text": "En comunidades con altos niveles de violencia, recuperar el orden debe ser la primera prioridad. Durante un tiempo, eso puede dejar en segundo plano la lucha contra la pobreza, las mejoras educativas y la creación de oportunidades de empleo.",
    },
    {
        "id": "q05",
        "text": "No tendría problema en votar por candidatos de distintos partidos si considero que son las personas más capaces. Lo haría aunque eso produzca un gobierno formado por personas con ideas e intereses diferentes.",
    },
    {
        "id": "q06",
        "text": "El gobierno debería intervenir menos en la economía mediante subsidios, incentivos y controles de precios. Esto daría más libertad a las personas y las empresas para crear oportunidades, aunque implique reducir apoyos como los subsidios educativos para niños de escasos recursos o los incentivos destinados al crecimiento de industrias como el turismo.",
    },
    {
        "id": "q07",
        "text": "Al escoger a una persona para un puesto público, la preparación debería pesar más que la confianza personal o política. Eso puede significar trabajar con alguien que no apoyó al gobierno, o incluso con una persona vinculada a la oposición.",
    },
    {
        "id": "q08",
        "text": "Las leyes y la educación deberían reflejar parte de los valores culturales y religiosos de Panamá. La tradición católica y las costumbres más arraigadas merecen un lugar especial, aunque no todos los ciudadanos las compartan.",
    },
    {
        "id": "q09",
        "text": "La mejor forma de reducir la delincuencia es invertir en educación, empleo y actividades deportivas de calidad para los jóvenes. Sus resultados pueden tardar más que los de las medidas de mano dura, pero buscan reducir las causas sociales del delito.",
    },
    {
        "id": "q10",
        "text": "Si un político ayuda de verdad a su comunidad mediante obras y atención a las necesidades de los más pobres, es razonable volver a apoyarlo. Esto vale aunque busque la reelección, aspire a otro cargo o lleve muchos años en la política.",
    },
    {
        "id": "q11",
        "text": "Ningún partido debería recibir mi voto por costumbre. Cada elección debe ganárselo nuevamente, aunque ese partido me haya representado bien en el pasado.",
    },
    {
        "id": "q12",
        "text": "A veces el gobierno debe imponer más reglas para proteger a la población. Puede hacerlo frente a industrias potencialmente contaminantes, como la minería o el petróleo, o para proteger a los jóvenes en internet, aunque eso limite algunas decisiones de empresas y familias.",
    },
    {
        "id": "q13",
        "text": "Aunque existen distintos modelos de familia, el Estado debería dar un reconocimiento especial a la familia tradicional. Sus defensores consideran que aporta estabilidad en la crianza y continuidad de valores, aunque las demás familias también merezcan protección legal.",
    },
    {
        "id": "q14",
        "text": "Para enfrentar la delincuencia, la policía necesita más autoridad para actuar con firmeza. Debería poder detener o requisar ante situaciones sospechosas, aunque eso aumente el riesgo de que algunas personas inocentes sean revisadas o detenidas.",
    },
    {
        "id": "q15",
        "text": "Panamá debería adoptar nuevas tecnologías e innovaciones con rapidez. Esto puede transformar formas tradicionales de trabajar o dejar a algunas personas sin empleo, pero puede considerarse un costo necesario para avanzar.",
    },
    {
        "id": "q16",
        "text": "Es comprensible que una persona que trabajó activamente para llevar un proyecto político al gobierno espere una oportunidad laboral, siempre que cumpla con los requisitos. En Panamá, el empleo escasea y muchas personas ven la política como una posible vía para conseguir trabajo.",
    },
    {
        "id": "q17",
        "text": "Si un partido representa bien mis ideas, considero importante mantenerle la lealtad y fortalecerlo con mi apoyo. Esto puede aplicarse aunque no me convenzan todos sus candidatos o decisiones, e incluso cuando algunos de sus integrantes enfrenten acusaciones graves de corrupción.",
    },
    {
        "id": "q18",
        "text": "El Estado no debería intervenir en las decisiones personales sobre cómo vivir, formar pareja o construir una familia, mientras no se haga daño a otras personas. Esto debe respetarse aunque esas decisiones no coincidan con las costumbres de la mayoría.",
    },
    {
        "id": "q19",
        "text": "Prefiero pagar menos impuestos, aunque eso implique calles con menor mantenimiento, menos inversión en escuelas o servicios públicos más limitados. Reducir el gasto también puede evitar que la burocracia crezca demasiado.",
    },
    {
        "id": "q20",
        "text": "El progreso del país no debería dejar atrás nuestras tradiciones culturales y religiosas. La educación y la vida pública deben reservar espacio para la historia nacional, el patriotismo, la tradición católica y la cultura latinoamericana, aunque algunas personas prefieran una enseñanza más neutral.",
    },
    {
        "id": "q21",
        "text": "Dar demasiado poder a las fuerzas de seguridad puede afectar los derechos de personas inocentes. Sin embargo, limitar su autoridad también puede dificultar una respuesta rápida frente al crimen.",
    },
    {
        "id": "q22",
        "text": "Estoy dispuesto a pagar más impuestos si eso mejora de manera clara la educación, la salud y otros servicios públicos. Aceptaría tener menos dinero disponible para mis propios gastos.",
    },
    {
        "id": "q23",
        "text": "En temas que influyen en la formación de los menores, el Estado debería fijar límites basados en valores morales. Esto incluye la educación sexual y los contenidos que pueden ver en internet, aunque algunas familias prefieran tomar esas decisiones por su cuenta.",
    },
    {
        "id": "q24",
        "text": "Los partidos políticos fuertes ayudan a dar continuidad a los planes del país. Pueden evitar que cada nuevo gobierno engavete lo anterior y permitir que los proyectos políticos se consoliden, aunque también dificulten la entrada de nuevas fuerzas.",
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
