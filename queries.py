from database import fetch_dataframe, execute_scalar, execute_query

def _build_where_clause(grupo, anio, mes, regional):
    conditions = []
    params = []
    
    # We only care about 2020 and 2021 as stated in instructions unless filtered
    conditions.append("strftime('%Y', fecha_entrega) IN ('2020', '2021')")
    
    if grupo and grupo != 'Todos':
        conditions.append("grupo_fco_economico = ?")
        params.append(grupo)
        
    if anio and anio != 'Todos':
        conditions.append("strftime('%Y', fecha_entrega) = ?")
        params.append(str(anio))
        
    if mes and mes != 'Todos':
        conditions.append("strftime('%m', fecha_entrega) = ?")
        params.append(str(mes).zfill(2))
        
    if regional and regional != 'Todos':
        conditions.append("regional_caf = ?")
        params.append(regional)
        
    where_clause = " AND ".join(conditions)
    return f"WHERE {where_clause}", tuple(params)


def get_kpi_personas(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"SELECT COUNT(DISTINCT id) FROM dispensacion {where}"
    res = execute_scalar(query, params)
    return res if res else 0

def get_kpi_formulas(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"SELECT COUNT(DISTINCT formula) FROM dispensacion {where}"
    res = execute_scalar(query, params)
    return res if res else 0

def get_kpi_costo_promedio(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT AVG(costo_formula) AS costo_promedio_formula
    FROM (
        SELECT formula, SUM(costo_total) AS costo_formula
        FROM dispensacion
        {where}
        GROUP BY formula
    ) AS formulas
    """
    res = execute_scalar(query, params)
    return res if res else 0

def get_kpi_costo_total(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"SELECT SUM(costo_total) FROM dispensacion {where}"
    res = execute_scalar(query, params)
    return res if res else 0

def get_costo_variacion(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, 'Todos', mes, regional)
    
    query = f"""
    SELECT
        costo_2020,
        costo_2021,
        ((costo_2021 - costo_2020) / NULLIF(costo_2020, 0)) * 100 AS variacion_porcentual
    FROM (
        SELECT
            SUM(CASE WHEN strftime('%Y', fecha_entrega) = '2020' THEN costo_total ELSE 0 END) AS costo_2020,
            SUM(CASE WHEN strftime('%Y', fecha_entrega) = '2021' THEN costo_total ELSE 0 END) AS costo_2021
        FROM dispensacion
        {where}
    )
    """
    row = execute_query(query, params)
    if row and row[0]:
        c2020 = row[0]['costo_2020'] or 0
        c2021 = row[0]['costo_2021'] or 0
        var = row[0]['variacion_porcentual']
        return c2020, c2021, var
    return 0, 0, None

def get_dispensacion_tiempo(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT
        strftime('%Y', fecha_entrega) AS anio,
        strftime('%m', fecha_entrega) AS mes,
        COUNT(DISTINCT formula) AS formulas
    FROM dispensacion
    {where}
    GROUP BY strftime('%Y', fecha_entrega), strftime('%m', fecha_entrega)
    ORDER BY anio, mes
    """
    return fetch_dataframe(query, params)

def get_top_medicamentos(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT descripcion, SUM(costo_total) AS costo_total
    FROM dispensacion
    {where}
    GROUP BY descripcion
    ORDER BY costo_total DESC
    LIMIT 10
    """
    return fetch_dataframe(query, params)

def get_costo_pbs(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT pbs, SUM(costo_total) AS costo_total
    FROM dispensacion
    {where}
    GROUP BY pbs
    ORDER BY costo_total DESC
    """
    return fetch_dataframe(query, params)

def get_costo_municipio(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT municipio_caf, SUM(costo_total) AS costo_total
    FROM dispensacion
    {where}
    GROUP BY municipio_caf
    ORDER BY costo_total DESC
    LIMIT 10
    """
    return fetch_dataframe(query, params)

def get_costo_tipo_entrega(grupo, anio, mes, regional):
    where, params = _build_where_clause(grupo, anio, mes, regional)
    query = f"""
    SELECT tipo_entrega, SUM(costo_total) AS costo_total
    FROM dispensacion
    {where}
    GROUP BY tipo_entrega
    ORDER BY costo_total DESC
    """
    return fetch_dataframe(query, params)

def get_grupos_farmacologicos():
    query = "SELECT DISTINCT grupo_fco_economico FROM dispensacion WHERE grupo_fco_economico IS NOT NULL ORDER BY grupo_fco_economico"
    rows = execute_query(query)
    return [row['grupo_fco_economico'] for row in rows if row['grupo_fco_economico']]

def get_regionales():
    query = "SELECT DISTINCT regional_caf FROM dispensacion WHERE regional_caf IS NOT NULL ORDER BY regional_caf"
    rows = execute_query(query)
    return [row['regional_caf'] for row in rows if row['regional_caf']]

# --- ANTIDIABETICOS ---

def get_antidiabeticos_variacion():
    query = """
    SELECT
        costo_2020,
        costo_2021,
        ((costo_2021 - costo_2020) / NULLIF(costo_2020, 0)) * 100 AS variacion_porcentual
    FROM (
        SELECT
            SUM(CASE WHEN strftime('%Y', fecha_entrega) = '2020' THEN costo_total ELSE 0 END) AS costo_2020,
            SUM(CASE WHEN strftime('%Y', fecha_entrega) = '2021' THEN costo_total ELSE 0 END) AS costo_2021
        FROM dispensacion
        WHERE grupo_fco_economico = ?
    )
    """
    params = ("ANTIDIABETICOS",)
    row = execute_query(query, params)
    if row and row[0]:
        c2020 = row[0]['costo_2020'] or 0
        c2021 = row[0]['costo_2021'] or 0
        var = row[0]['variacion_porcentual']
        return c2020, c2021, var
    return 0, 0, None

def get_antidiabetico_mas_costoso():
    query = """
    SELECT descripcion, SUM(costo_total) AS costo_total
    FROM dispensacion
    WHERE grupo_fco_economico = ?
    GROUP BY descripcion
    ORDER BY costo_total DESC
    LIMIT 1
    """
    params = ("ANTIDIABETICOS",)
    row = execute_query(query, params)
    if row and row[0]:
        return row[0]['descripcion'], row[0]['costo_total']
    return "N/A", 0

def get_antidiabeticos_costo_promedio():
    query = """
    SELECT AVG(costo_formula) AS costo_promedio_formula
    FROM (
        SELECT formula, SUM(costo_total) AS costo_formula
        FROM dispensacion
        WHERE grupo_fco_economico = ?
        GROUP BY formula
    ) AS formulas
    """
    params = ("ANTIDIABETICOS",)
    res = execute_scalar(query, params)
    return res if res else 0

def get_antidiabeticos_costo_total():
    query = """
    SELECT SUM(costo_total) AS costo_total
    FROM dispensacion
    WHERE strftime('%Y', fecha_entrega) IN ('2020', '2021') AND grupo_fco_economico = ?
    """
    params = ("ANTIDIABETICOS",)
    res = execute_scalar(query, params)
    return res if res else 0

def get_antidiabeticos_detalle():
    query = """
    SELECT
        descripcion AS medicamento,
        SUM(costo_total) AS costo_total,
        COUNT(DISTINCT formula) AS numero_formulas,
        SUM(costo_total) / NULLIF(COUNT(DISTINCT formula), 0) AS costo_promedio_formula
    FROM dispensacion
    WHERE grupo_fco_economico = ?
    GROUP BY descripcion
    ORDER BY costo_total DESC
    """
    params = ("ANTIDIABETICOS",)
    return fetch_dataframe(query, params)
