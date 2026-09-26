from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

def create_layout(app):
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Dashboard de Dispensación de Medicamentos - EPS", className="text-center text-primary mt-4"), width=12),
            dbc.Col(html.H4("Análisis de medicamentos dispensados durante 2020 y 2021", className="text-center text-secondary mb-4"), width=12)
        ]),

        # FILA 2 - FILTROS
        dbc.Row([
            dbc.Col([
                html.Label("Grupo Farmacológico"),
                dcc.Dropdown(id='filtro-grupo', value='Todos')
            ], width=3),
            dbc.Col([
                html.Label("Año"),
                dcc.Dropdown(id='filtro-anio', 
                             options=[
                                 {'label': 'Todos', 'value': 'Todos'},
                                 {'label': '2020', 'value': '2020'},
                                 {'label': '2021', 'value': '2021'}
                             ], value='Todos')
            ], width=3),
            dbc.Col([
                html.Label("Mes"),
                dcc.Dropdown(id='filtro-mes', 
                             options=[
                                 {'label': 'Todos', 'value': 'Todos'},
                                 {'label': 'Enero', 'value': '01'},
                                 {'label': 'Febrero', 'value': '02'},
                                 {'label': 'Marzo', 'value': '03'},
                                 {'label': 'Abril', 'value': '04'},
                                 {'label': 'Mayo', 'value': '05'},
                                 {'label': 'Junio', 'value': '06'},
                                 {'label': 'Julio', 'value': '07'},
                                 {'label': 'Agosto', 'value': '08'},
                                 {'label': 'Septiembre', 'value': '09'},
                                 {'label': 'Octubre', 'value': '10'},
                                 {'label': 'Noviembre', 'value': '11'},
                                 {'label': 'Diciembre', 'value': '12'}
                             ], value='Todos')
            ], width=3),
            dbc.Col([
                html.Label("Regional CAF"),
                dcc.Dropdown(id='filtro-regional', value='Todos')
            ], width=3),
        ], className="mb-4"),

        # FILA 1 - KPI GENERALES
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Personas con dispensaciones"), dbc.CardBody(html.H3(id="kpi-personas"))], color="light"), width=2),
            dbc.Col(dbc.Card([dbc.CardHeader("Fórmulas dispensadas"), dbc.CardBody(html.H3(id="kpi-formulas"))], color="light"), width=2),
            dbc.Col(dbc.Card([dbc.CardHeader("Costo promedio por fórmula"), dbc.CardBody(html.H3(id="kpi-costo-promedio"))], color="light"), width=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Costo total"), dbc.CardBody(html.H3(id="kpi-costo-total"))], color="light"), width=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Variación 2020-2021"), dbc.CardBody(html.H4(id="kpi-variacion"))], color="light"), width=2),
        ], className="mb-4"),

        # FILA 3 - GRÁFICO DE LÍNEAS
        dbc.Row([
            dbc.Col(dcc.Graph(id="grafico-tiempo"), width=12)
        ], className="mb-4"),

        # FILA 4
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="grafico-top-medicamentos"),
                html.Div(id="tabla-top-medicamentos-legend", className="mt-2")
            ], width=6),
            dbc.Col(dcc.Graph(id="grafico-pbs"), width=6)
        ], className="mb-4"),

        # FILA 5
        dbc.Row([
            dbc.Col(dcc.Graph(id="grafico-municipios"), width=6),
            dbc.Col(dcc.Graph(id="grafico-tipo-entrega"), width=6)
        ], className="mb-4"),

        html.Hr(),

        # FILA 6 - SECCIÓN ANTIDIABETICOS
        dbc.Row([
            dbc.Col(html.H2("Análisis del grupo farmacológico ANTIDIABETICOS", className="text-center text-info mt-4 mb-4"), width=12)
        ]),

        # FILA 7 - KPI ANTIDIABETICOS
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Costo total ANTIDIABETICOS"), dbc.CardBody(html.H4(id="kpi-anti-costo-total"))], color="info", inverse=True), width=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Variación del costo"), dbc.CardBody(html.H5(id="kpi-anti-variacion"))], color="info", inverse=True), width=3),
            dbc.Col(dbc.Card([dbc.CardHeader("ANTIDIABETICO con mayor costo"), dbc.CardBody([html.H6(id="kpi-anti-top-nombre"), html.H5(id="kpi-anti-top-costo")])], color="info", inverse=True), width=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Costo promedio de una fórmula ANTIDIABETICA"), dbc.CardBody(html.H4(id="kpi-anti-costo-promedio"))], color="info", inverse=True), width=3),
        ], className="mb-4"),

        # FILA 8 - TABLA ANTIDIABETICOS
        dbc.Row([
            dbc.Col([
                html.H4("Detalle de medicamentos ANTIDIABETICOS"),
                dash_table.DataTable(
                    id='tabla-antidiabeticos',
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '5px'},
                    style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
                    sort_action="native",
                )
            ], width=12)
        ], className="mb-5")

    ], fluid=True)
