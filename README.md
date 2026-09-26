# Dashboard de Dispensación de Medicamentos

Este es un dashboard interactivo construido con Dash y Plotly en Python. Se conecta a una base de datos local SQLite (`medicamentos.db`) para analizar datos de medicamentos dispensados por una EPS durante 2020 y 2021.

## Requisitos

- Python 3.7+
- Entorno virtual (recomendado)

## Instalación Local

1. Activa tu entorno virtual (si ya tienes uno llamado `venv`):
   ```bash
   venv\Scripts\activate
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Asegúrate de que el archivo `medicamentos.db` esté en la raíz del proyecto.

## Ejecución

Ejecuta el archivo principal:
```bash
python app.py
```
Abre un navegador y visita `http://127.0.0.1:8050/`.
