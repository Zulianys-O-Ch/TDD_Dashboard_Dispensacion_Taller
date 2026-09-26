import sqlite3
import pandas as pd
import os

DB_PATH = "medicamentos.db"

def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"El archivo {DB_PATH} no se encontró en el directorio actual.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    if params is None:
        params = ()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def execute_scalar(query, params=None):
    if params is None:
        params = ()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    finally:
        conn.close()

def fetch_dataframe(query, params=None):
    if params is None:
        params = ()
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()
