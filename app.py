import dash
import dash_bootstrap_components as dbc
from layout import create_layout
from callbacks import register_callbacks

# Configurar Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Medicamentos"

# Cargar el layout
app.layout = create_layout(app)

# Registrar los callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
