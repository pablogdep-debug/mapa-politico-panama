# mapa-politico-panama

## Brújula Política de Panamá

Aplicación desarrollada con Python y Streamlit. En esta primera etapa, el
proyecto contiene únicamente su estructura inicial y una pantalla de inicio.

## Requisitos

- Python 3.9 o superior
- Las dependencias indicadas en `requirements.txt`

## Instalación

```powershell
python -m pip install -r requirements.txt
```

## Ejecución

```powershell
python -m streamlit run app.py
```

Después, abre la dirección local que Streamlit muestra en la terminal,
normalmente `http://localhost:8501`.

## Estructura

- `app.py`: punto de entrada de la aplicación.
- `questions.py`: módulo reservado para las preguntas.
- `scoring.py`: módulo reservado para el cálculo de puntuaciones.
- `interpretations.py`: módulo reservado para interpretar los resultados.
- `requirements.txt`: dependencias de Python.
- `README.md`: instrucciones y documentación general.
