from dash import Input, Output, html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import locale
import pandas as pd
from queries import (
    get_grupos_farmacologicos, get_regionales,
    get_kpi_personas, get_kpi_formulas, get_kpi_costo_promedio,
    get_kpi_costo_total, get_costo_variacion, get_dispensacion_tiempo,
    get_top_medicamentos, get_costo_pbs, get_costo_municipio,
    get_costo_tipo_entrega, get_antidiabeticos_variacion,
    get_antidiabetico_mas_costoso, get_antidiabeticos_costo_promedio,
    get_antidiabeticos_costo_total, get_antidiabeticos_detalle
)

def format_money(value):
    if value is None:
        return "$0"
    return f"${value:,.0f}".replace(",", ".")

def register_callbacks(app):

    @app.callback(
        [Output('filtro-grupo', 'options'),
         Output('filtro-regional', 'options')],
        [Input('filtro-grupo', 'id')] # dummy input
    )
    def load_filter_options(_):
        grupos = get_grupos_farmacologicos()
        regionales = get_regionales()
        
        opt_grupos = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': g, 'value': g} for g in grupos]
        opt_regionales = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': r, 'value': r} for r in regionales]
        return opt_grupos, opt_regionales

    @app.callback(
        [
            Output('kpi-personas', 'children'),
            Output('kpi-formulas', 'children'),
            Output('kpi-costo-promedio', 'children'),
            Output('kpi-costo-total', 'children'),
            Output('kpi-variacion', 'children'),
            Output('grafico-tiempo', 'figure'),
            Output('grafico-top-medicamentos', 'figure'),
            Output('tabla-top-medicamentos-legend', 'children'),
            Output('grafico-pbs', 'figure'),
            Output('grafico-municipios', 'figure'),
            Output('grafico-tipo-entrega', 'figure')
        ],
        [
            Input('filtro-grupo', 'value'),
            Input('filtro-anio', 'value'),
            Input('filtro-mes', 'value'),
            Input('filtro-regional', 'value')
        ]
    )
    def update_dashboard(grupo, anio, mes, regional):
        # KPIs
        personas = get_kpi_personas(grupo, anio, mes, regional)
        formulas = get_kpi_formulas(grupo, anio, mes, regional)
        costo_promedio = get_kpi_costo_promedio(grupo, anio, mes, regional)
        costo_total = get_kpi_costo_total(grupo, anio, mes, regional)
        c2020, c2021, variacion = get_costo_variacion(grupo, anio, mes, regional)

        kpi_p = f"{personas:,.0f}".replace(",", ".")
        kpi_f = f"{formulas:,.0f}".replace(",", ".")
        kpi_cp = format_money(costo_promedio)
        kpi_ct = format_money(costo_total)

        if variacion is not None:
            if variacion > 0:
                kpi_var = f"+{variacion:.2f}%"
            elif variacion < 0:
                kpi_var = f"{variacion:.2f}%"
            else:
                kpi_var = "0.00%"
        else:
            if c2020 == 0 and c2021 > 0:
                kpi_var = "N/A (Sin base 2020)"
            elif c2020 == 0 and c2021 == 0:
                kpi_var = "0.00%"
            else:
                kpi_var = "N/A"

        # Gráficos
        
        # Tiempo
        df_tiempo = get_dispensacion_tiempo(grupo, anio, mes, regional)
        if not df_tiempo.empty:
            meses_map = {'01':'Enero', '02':'Febrero', '03':'Marzo', '04':'Abril', 
                         '05':'Mayo', '06':'Junio', '07':'Julio', '08':'Agosto', 
                         '09':'Septiembre', '10':'Octubre', '11':'Noviembre', '12':'Diciembre'}
            df_tiempo['fecha_str'] = df_tiempo['mes'].map(meses_map) + " " + df_tiempo['anio']
            fig_tiempo = px.line(df_tiempo, x='fecha_str', y='formulas', 
                                 title="Dispensación de medicamentos en el tiempo",
                                 labels={'fecha_str': 'Mes-Año', 'formulas': 'Fórmulas distintas'},
                                 markers=True)
        else:
            fig_tiempo = go.Figure().update_layout(title="No hay datos disponibles")

        # Top Medicamentos
        df_top = get_top_medicamentos(grupo, anio, mes, regional)
        if not df_top.empty:
            df_top = df_top.copy()
            df_top['id_med'] = [f"MED-{i+1}" for i in range(len(df_top))]
            
            # Para la gráfica, invertimos el orden para que MED-1 quede arriba en la barra horizontal
            df_top_plot = df_top.sort_values(by='costo_total', ascending=True)
            fig_top = px.bar(
                df_top_plot,
                x='costo_total',
                y='id_med',
                orientation='h',
                title="Top 10 medicamentos por costo total",
                labels={'id_med': 'ID Medicamento', 'costo_total': 'Costo Total'},
                hover_data={'descripcion': True, 'costo_total': False, 'id_med': False}
            )
            fig_top.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>ID: %{y}<br>Costo Total: %{x:$,.0f}<extra></extra>"
            )
            fig_top.update_layout(
                yaxis_title="Identificador",
                xaxis_title="Costo Total",
                margin=dict(l=60, r=20, t=40, b=40)
            )

            # Leyenda / Tabla debajo de la gráfica
            table_header = [
                html.Thead(html.Tr([
                    html.Th("ID", style={'width': '20%', 'textAlign': 'center'}),
                    html.Th("Medicamento", style={'width': '80%'})
                ]))
            ]
            rows = []
            for _, r in df_top.iterrows():
                rows.append(html.Tr([
                    html.Td(html.Span(r['id_med'], className="badge bg-primary text-white"), style={'textAlign': 'center'}),
                    html.Td(r['descripcion'], style={'fontSize': '0.82rem', 'wordBreak': 'break-word'})
                ]))
            legend_top = dbc.Table(
                table_header + [html.Tbody(rows)],
                bordered=True,
                hover=True,
                responsive=True,
                striped=True,
                size="sm",
                className="mt-2 shadow-sm"
            )
        else:
            fig_top = go.Figure().update_layout(title="No hay datos disponibles")
            legend_top = html.P("No hay datos disponibles para los filtros seleccionados.", className="text-muted text-center")

        # PBS
        df_pbs = get_costo_pbs(grupo, anio, mes, regional)
        if not df_pbs.empty:
            fig_pbs = px.bar(df_pbs, x='pbs', y='costo_total', 
                             title="Costo de medicamentos PBS vs NO PBS",
                             labels={'pbs': 'PBS', 'costo_total': 'Costo Total'})
        else:
            fig_pbs = go.Figure().update_layout(title="No hay datos disponibles")

        # Municipios
        df_mun = get_costo_municipio(grupo, anio, mes, regional)
        if not df_mun.empty:
            df_mun = df_mun.sort_values(by='costo_total', ascending=True)
            fig_mun = px.bar(df_mun, x='costo_total', y='municipio_caf', orientation='h',
                             title="Costo por municipio de dispensación",
                             labels={'municipio_caf': 'Municipio', 'costo_total': 'Costo Total'})
        else:
            fig_mun = go.Figure().update_layout(title="No hay datos disponibles")

        # Tipo entrega
        df_tipo = get_costo_tipo_entrega(grupo, anio, mes, regional)
        if not df_tipo.empty:
            fig_tipo = px.bar(df_tipo, x='tipo_entrega', y='costo_total',
                              title="Costo según tipo de entrega",
                              labels={'tipo_entrega': 'Tipo de Entrega', 'costo_total': 'Costo Total'})
        else:
            fig_tipo = go.Figure().update_layout(title="No hay datos disponibles")

        return kpi_p, kpi_f, kpi_cp, kpi_ct, kpi_var, fig_tiempo, fig_top, legend_top, fig_pbs, fig_mun, fig_tipo

    @app.callback(
        [
            Output('kpi-anti-costo-total', 'children'),
            Output('kpi-anti-variacion', 'children'),
            Output('kpi-anti-top-nombre', 'children'),
            Output('kpi-anti-top-costo', 'children'),
            Output('kpi-anti-costo-promedio', 'children'),
            Output('tabla-antidiabeticos', 'data'),
            Output('tabla-antidiabeticos', 'columns')
        ],
        [Input('filtro-grupo', 'id')] # dummy input para que se ejecute al inicio
    )
    def update_antidiabeticos(_):
        costo_total = get_antidiabeticos_costo_total()
        kpi_ct = format_money(costo_total)

        c2020, c2021, var = get_antidiabeticos_variacion()
        if var is not None:
            if var > 0:
                kpi_var = f"El costo aumentó {var:.2f}% entre 2020 y 2021."
            elif var < 0:
                kpi_var = f"El costo disminuyó {abs(var):.2f}% entre 2020 y 2021."
            else:
                kpi_var = "El costo se mantuvo estable."
        else:
            if c2020 == 0 and c2021 > 0:
                kpi_var = f"El costo en 2021 fue {format_money(c2021)} (sin registros previos en 2020)."
            elif c2020 == 0 and c2021 == 0:
                kpi_var = "El costo se mantuvo estable."
            else:
                kpi_var = "No hay datos suficientes para comparar 2020 y 2021."

        top_nom, top_costo = get_antidiabetico_mas_costoso()
        kpi_top_nom = top_nom
        kpi_top_costo = format_money(top_costo)

        costo_prom = get_antidiabeticos_costo_promedio()
        kpi_cp = format_money(costo_prom)

        df_detalle = get_antidiabeticos_detalle()
        if not df_detalle.empty:
            # Formateamos un poco la tabla
            df_detalle['costo_total'] = df_detalle['costo_total'].apply(lambda x: format_money(x) if pd.notnull(x) else "$0")
            df_detalle['costo_promedio_formula'] = df_detalle['costo_promedio_formula'].apply(lambda x: format_money(x) if pd.notnull(x) else "$0")
            
            columns = [{"name": i, "id": i} for i in df_detalle.columns]
            data = df_detalle.to_dict('records')
        else:
            columns = []
            data = []

        return kpi_ct, kpi_var, kpi_top_nom, kpi_top_costo, kpi_cp, data, columns
