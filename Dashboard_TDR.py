# %%
#%pip install altair

# %%
import dash
from dash import dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import altair as alt

df_analysis = pd.read_excel('df_final.xlsx')
df_riesgo_todo = pd.read_excel('TDR_riesgo.xlsx')
df_riesgo = df_riesgo_todo[df_riesgo_todo['Año'] == 2025].copy()


# %%
# crear app
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap", 
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
]

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

# brand kit
azul = '#002C73'
amarillo = '#F9B233'
amarillo_2 = '#FFD367'
azul_2 = '#1E3982'
azul_3 = '#4353A1'
azul_claro = "#D3E0F6"
blanco = '#FFFFFF'
negro = '#1B1B1B'
negative = '#73002C'
success = '#2C7301'


# %%
# Sidebar
def sidebar():
    return html.Div([
        html.H5("Menú", className="text-white"),
        html.Hr(style={'border-color': azul_3}),
        
        dbc.Nav([
            #inicio
            dbc.NavLink([
                html.I(className="fas fa-home me-2"), "Inicio"], 
                href="/inicio", active="exact", className="text-white nav-link-custom"
            ),
            #resumen 
            dbc.NavLink([
                html.I(className="fas fa-chart-line me-2"),
                "Resumen  ",
                html.I(className="fas fa-chevron-down ms-auto", id="icono-resumen")  # ms-auto es icono a la derecha
                ], href="#", className="text-white nav-link-custom", id="resumen-toggle", style={"cursor": "pointer"}
            ),

            #Submenú resumen
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavLink("Costos", href="/resumen/costos", active="exact", className="ms-4"),
                    dbc.NavLink("Análisis por km", href="/resumen/analisiskm", active="exact", className="ms-4"),
                ], vertical=True, pills=True),
                id="submenu-resumen",
                is_open=False
            ),

            #rankings   
            dbc.NavLink([
                html.I(className="fas fa-chart-bar me-2"),
                "Rankings"
            ], href="/rankings", active="exact", className="text-white nav-link-custom"),

            #fuzzy   
            dbc.NavLink([
                html.I(className="fas fa-file-alt me-2"),
                "Monitoreo Fuzzy"
            ], href="/fuzzy", active="exact", className="text-white nav-link-custom"),

            #simulador   
            dbc.NavLink([
                html.I(className="fas fa-calculator me-2"),
                "Simulador CPK"
            ], href="/simulador", active="exact", className="text-white nav-link-custom"),

            #subir archivos
            dbc.NavLink([
                html.I(className="fas fa-folder me-2"),
                "Subir archivos"
            ], href="/archivos", active="exact", className="text-white nav-link-custom"),
        ], vertical=True, pills=True),

    ], id="sidebar", style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "1rem",
        "background-color": azul_2,
        "color": "white",
        "overflow-x": "hidden",
        "transition": "all 0.3s",
        "box-shadow": "2px 0 5px rgba(0,0,0,0.1)"
    })

# Layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar(),
    html.Div(id='page-content', style={
        'margin-left': '16rem',
        'padding': '2rem',
        'background-color': '#f8f9fa',
        'min-height': '100vh'
    })
])


# %%
#LAYOUT INICIO

# Período SIN mantenimiento: Oct-Dic 2024 
df_sin_mant = df_analysis[df_analysis['Mes'].str.startswith('2024')].copy()

# Período CON mantenimiento: Ene-Mar 2025 
df_con_mant = df_analysis[(df_analysis['Mes'].str.startswith('2025')) & 
                      (df_analysis['mantenimiento_total'].notna())].copy()

# Cálculo de CPK
def cpk_sin_mantenimiento(df_analysis):
    
    # CPK sin mantenimiento
    df_analysis['combustible_cpk'] = np.where(df_analysis['kmstotales'] > 0, 
                                   df_analysis['Costo por carga'] / df_analysis['kmstotales'], 0)
    df_analysis['casetas_cpk'] = np.where(df_analysis['kmstotales'] > 0,
                               df_analysis['Costo Caseta'] / df_analysis['kmstotales'], 0)
    
    #NaN
    df_analysis['combustible_cpk'] = df_analysis['combustible_cpk'].fillna(0)
    df_analysis['casetas_cpk'] = df_analysis['casetas_cpk'].fillna(0)
    
    df_analysis['cpk_parcial'] = df_analysis['combustible_cpk'] + df_analysis['casetas_cpk']
    
    return df_analysis

def cpk_con_mantenimiento(df_analysis):
    
    
    # CPK completo
    df_analysis['combustible_cpk'] = np.where(df_analysis['kmstotales'] > 0, 
                                   df_analysis['Costo por carga'] / df_analysis['kmstotales'], 0)
    df_analysis['casetas_cpk'] = np.where(df_analysis['kmstotales'] > 0,
                               df_analysis['Costo Caseta'] / df_analysis['kmstotales'], 0)
    df_analysis['mantenimiento_cpk'] = np.where(df_analysis['kmstotales'] > 0,
                                     df_analysis['mantenimiento_total'] / df_analysis['kmstotales'], 0)
    
    #NaN
    df_analysis['combustible_cpk'] = df_analysis['combustible_cpk'].fillna(0)
    df_analysis['casetas_cpk'] = df_analysis['casetas_cpk'].fillna(0)
    df_analysis['mantenimiento_cpk'] = df_analysis['mantenimiento_cpk'].fillna(0)
    
    df_analysis['cpk_total'] = df_analysis['combustible_cpk'] + df_analysis['casetas_cpk'] + df_analysis['mantenimiento_cpk']
    df_analysis['cpk_parcial'] = df_analysis['combustible_cpk'] + df_analysis['casetas_cpk']  # Para comparación
    
    return df_analysis

df_sin_mant = cpk_sin_mantenimiento(df_sin_mant)
df_con_mant = cpk_con_mantenimiento(df_con_mant)

# Layout de inicio
def layout_inicio():
    return html.Div([
        html.Div([
            html.H2("TDR Control Center", className="mb-4", style={'color': blanco, 'fontWeight': 'bold', 'fontFamily': 'Roboto'}),
        ], style={
            'background': f"linear-gradient(135deg, {azul} 0%, {azul_2} 100%)",
            'padding': '1rem',
            'border-radius': '12px',
            'margin-bottom': '1rem',
            'text-align': 'center'}),
        
        dbc.Row([
            # Filtro de mantenimiento
            dbc.Col([
                html.Label("Tipo de análisis:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.RadioItems(
                    id='filtro-mantenimiento',
                    options=[
                        {'label': ' Sin Mantenimiento (2024)', 'value': 'sin'},
                        {'label': ' Con Mantenimiento (2025)', 'value': 'con'}
                    ],
                    value='sin',
                    inline=True,
                    labelStyle={'margin-right': '20px'},
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de mes
            dbc.Col([
                html.Label("Mes:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-mes',
                    options=[], 
                    multi = True,
                    value=['todos'] ,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de cliente
            dbc.Col([
                html.Label("Cliente:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-cliente',
                    options=[],  
                    multi = True,
                    value=['todos'] ,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de flota
            dbc.Col([
                html.Label("Flota (Unidad):", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-flota',
                    options=[],
                    multi = True,
                    value=['todos'] ,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        ], className="mb-4", style={'backgroundColor': azul_claro, 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 6px 20px rgba(0, 0, 0, 0.2)'}),
        
        # KPIs
        dbc.Row([
            # CPK Promedio
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("CPK Promedio", className="text-muted", 
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-cpk-promedio", children="$0.00", 
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': azul}),
                        html.P("por kilómetro", className="text-muted small", 
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
            
            # CPK Máximo
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("CPK Máximo", className="text-muted",
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-cpk-maximo", children="$0.00",
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': negative}),
                        html.P("por kilómetro", className="text-muted small",
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
            
            # CPK Mínimo
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("CPK Mínimo", className="text-muted",
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-cpk-minimo", children="$0.00",
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': success}),
                        html.P("por kilómetro", className="text-muted small",
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
        ]),
        
        dbc.Row([
            # Unidades de Flota
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Unidades de Flota", className="text-muted",
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-unidades", children="0",
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': azul_2}),
                        html.P("unidades registradas", className="text-muted small",
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
            
            # Kilómetros Recorridos
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Kilómetros Recorridos", className="text-muted",
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-kilometros", children="0",
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': azul_2}),
                        html.P("kilómetros totales", className="text-muted small",
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
            
            # Costo por Carga
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Costo por Carga Promedio", className="text-muted",
                               style={'fontFamily': 'Roboto', 'fontSize': '14px'}),
                        html.H3(id="kpi-costo-carga", children="$0",
                               style={'fontFamily': 'Roboto', 'fontWeight': 'bold', 'color': amarillo}),
                        html.P("promedio total", className="text-muted small",
                              style={'fontFamily': 'Roboto', 'marginBottom': 0})
                    ])
                ], style={'border': f'2px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})
            ], width=4, className="mb-3"),
        ]),

        dbc.Row([
            dbc.Col(
                html.Img(src='/assets/TDR_Imagen.jpg', style={'width' : '1120px', 'height' : "300px"}))
                ])
    ])

# Callback para actualizar opciones de mes y cliente por el mantenimiento
@callback(
    [Output('filtro-mes', 'options'),
     Output('filtro-mes', 'value'),  # Agregar este output
     Output('filtro-cliente', 'options'),
     Output('filtro-cliente', 'value')],  # Agregar este output
    Input('filtro-mantenimiento', 'value')
)
def actualizar_opciones_filtros(tipo_mantenimiento):
    if tipo_mantenimiento == 'sin':
        df = df_sin_mant
    else:
        df = df_con_mant
    
    # Opciones de mes
    meses_opciones = [{'label': 'Todos', 'value': 'todos'}]
    meses_opciones.extend([{'label': mes, 'value': mes} for mes in sorted(df['Mes'].unique())])
    
    # Opciones de cliente
    clientes_opciones = [{'label': 'Todos', 'value': 'todos'}]
    clientes_opciones.extend([{'label': cliente, 'value': cliente} for cliente in sorted(df['Cliente'].unique())])
    
    #'Todos' como valor default
    return meses_opciones, ['todos'], clientes_opciones, ['todos']

# Callback para actualizar opciones de flota
@callback(
    [Output('filtro-flota', 'options'),
     Output('filtro-flota', 'value')],  
    [Input('filtro-mantenimiento', 'value'),
     Input('filtro-cliente', 'value'),
     Input('filtro-mes', 'value')]
)
def actualizar_opciones_flota(tipo_mantenimiento, cliente, mes):
    df_filtrado = df_sin_mant.copy() if tipo_mantenimiento == 'sin' else df_con_mant.copy()

    # Filtrar por cliente (si no se selecciona 'todos')
    if 'todos' not in cliente:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(cliente)]

    # Filtrar por mes (si no se selecciona 'todos')
    if 'todos' not in mes:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(mes)]

    #opciones de flota sin repetir
    flotas_unicas = sorted(df_filtrado['Unidad'].dropna().unique())

    opciones = [{'label': 'Todas', 'value': 'todos'}]
    opciones += [{'label': f'Unidad {str(flota)}', 'value': flota} for flota in flotas_unicas]

    return opciones, ['todos']

@callback(
    [Output('kpi-cpk-promedio', 'children'),
     Output('kpi-cpk-maximo', 'children'),
     Output('kpi-cpk-minimo', 'children'),
     Output('kpi-unidades', 'children'),
     Output('kpi-kilometros', 'children'),
     Output('kpi-costo-carga', 'children')],
    [Input('filtro-mantenimiento', 'value'),
     Input('filtro-mes', 'value'),
     Input('filtro-cliente', 'value'),
     Input('filtro-flota', 'value')]
)
def actualizar_kpis(tipo_mantenimiento, mes, cliente, flota):
    if tipo_mantenimiento == 'sin':
        df_filtrado = df_sin_mant.copy()
        cpk_column = 'cpk_parcial'
    else:
        df_filtrado = df_con_mant.copy()
        cpk_column = 'cpk_total'

    if 'todos' not in mes:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(mes)]
    
    if 'todos' not in cliente:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(cliente)]

    if 'todos' not in flota:
        df_filtrado = df_filtrado[df_filtrado['Unidad'].isin(flota)]
    
    # Calcular KPIs
    if len(df_filtrado) > 0:
        
        cpk_promedio = f"${df_filtrado[cpk_column].mean():.2f}"
        
        # Para máximo y mínimo, sí excluir valores 0 tiene sentido
        df_cpk_no_cero = df_filtrado[df_filtrado[cpk_column] > 0]
        if len(df_cpk_no_cero) > 0:
            cpk_maximo = f"${df_cpk_no_cero[cpk_column].max():.2f}"
            cpk_minimo = f"${df_cpk_no_cero[cpk_column].min():.2f}"
        else:
            cpk_maximo = "$0.00"
            cpk_minimo = "$0.00"
        
        # Unidades únicas
        unidades = f"{df_filtrado['Unidad'].nunique():,}"
        
        # Kilómetros totales
        kilometros = f"{df_filtrado['kmstotales'].sum():,.0f}"
        
        # Costo por carga promedio
        costo_carga = f"${df_filtrado['Costo por carga'].mean():,.0f}"
    else:
        cpk_promedio = "$0.00"
        cpk_maximo = "$0.00"
        cpk_minimo = "$0.00"
        unidades = "0"
        kilometros = "0"
        costo_carga = "$0"
    
    return cpk_promedio, cpk_maximo, cpk_minimo, unidades, kilometros, costo_carga

# %%
# Layout Costos

def create_kpi_card_costos(title, value, subtitle=None, color=azul):
    return dbc.Card([
        dbc.CardBody([
            html.H3(f"${value:,.2f}", 
                   style={'color': color, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
            html.P(title, 
                   className="text-muted mb-1", 
                   style={'fontSize': '14px', 'fontFamily': 'Roboto'}),
            html.P(subtitle, 
                   className="text-muted mb-0", 
                   style={'fontSize': '12px', 'fontFamily': 'Roboto'}) if subtitle else None
        ])
    ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '100%', 'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'})

def create_cost_card_costos(title, value, color=azul):
    """Crear tarjetas de costos usando estilos existentes"""
    return dbc.Card([
        dbc.CardBody([
            html.H4(f"${value:,.0f}", 
                   style={'color': color, 'fontWeight': 'bold', 'marginBottom': '0', 
                         'textAlign': 'center', 'fontFamily': 'Roboto'}),
            html.P(title, 
                   className="text-muted mb-0", 
                   style={'fontSize': '16px', 'textAlign': 'center', 'fontFamily': 'Roboto'})
        ])
    ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '120px'})
def layout_costos():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("Análisis de Costos - CPK",
                       style={
                           'color': azul, 
                           'marginBottom': '10px', 
                           'fontWeight': 'bold', 
                           'fontFamily': 'Roboto'})
            ])
        ]),
        
        
        dbc.Row([
            # Filtro de mantenimiento
            dbc.Col([
                html.Label("Tipo de análisis:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.RadioItems(
                    id='filtro-mantenimiento-costos',
                    options=[
                        {'label': ' Sin Mantenimiento (2024)', 'value': 'sin'},
                        {'label': ' Con Mantenimiento (2025)', 'value': 'con'},
                        {'label': ' Todos los períodos', 'value': 'todos'}
                    ],
                    value='todos',  
                    inline=True,
                    labelStyle={'margin-right': '20px'},
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de mes
            dbc.Col([
                html.Label("Mes:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-mes-costos',
                    options=[], 
                    multi = True,
                    value=['todos'],
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de cliente
            dbc.Col([
                html.Label("Cliente:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-cliente-costos',
                    options=[], 
                    multi = True,
                    value=['todos'],
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de flota
            dbc.Col([
                html.Label("Flota (Unidad):", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-flota-costos',
                    options=[],
                    multi = True,
                    value=['todos'],
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        ], className="mb-4", style={
            'backgroundColor': azul_claro, 
            'padding': '20px', 
            'borderRadius': '10px', 
            'border': '2px solid ' + azul_claro,
            'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'
        }),
        
        # KPIs
        dbc.Row([
            dbc.Col(html.Div(id='kpi-cards-costos'))
        ], className="mb-4"),
        
        # Gráficos principales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Distribución de Costos", 
                               style={'marginBottom': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='pie-chart-costos')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ], width=6),
            
            dbc.Col([
                html.Div(id='cost-cards-costos')
            ], width=6)
        ], className="mb-4"),
        
        # Gráfico de evolución
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Evolución del CPK", 
                               style={'marginBottom': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='line-chart-costos')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ])
        ])
    ])

# Callback para actualizar opciones de mes y cliente según mantenimiento 
@callback(
    [Output('filtro-mes-costos', 'options'),
     Output('filtro-mes-costos', 'value'), 
     Output('filtro-cliente-costos', 'options'),
     Output('filtro-cliente-costos', 'value')],  
    Input('filtro-mantenimiento-costos', 'value')
)
def actualizar_opciones_filtros_costos(tipo_mantenimiento):
    if tipo_mantenimiento == 'sin':
        df = df_sin_mant
    elif tipo_mantenimiento == 'con':
        df = df_con_mant
    else:  
        df = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    # Opciones de mes
    meses_opciones = [{'label': 'Todos', 'value': 'todos'}]
    meses_opciones.extend([{'label': mes, 'value': mes} for mes in sorted(df['Mes'].unique())])
    
    # Opciones de cliente
    clientes_opciones = [{'label': 'Todos', 'value': 'todos'}]
    clientes_opciones.extend([{'label': cliente, 'value': cliente} for cliente in sorted(df['Cliente'].unique())])
    
    # 'Todos' como valor default
    return meses_opciones, ['todos'], clientes_opciones, ['todos']

# Callback para actualizar opciones de flota 
@callback(
    [Output('filtro-flota-costos', 'options'),
     Output('filtro-flota-costos', 'value')],  
    [Input('filtro-mantenimiento-costos', 'value'),
     Input('filtro-cliente-costos', 'value'),
     Input('filtro-mes-costos', 'value')]
)
def actualizar_opciones_flota_costos(tipo_mantenimiento, cliente, mes):
    if tipo_mantenimiento == 'sin':
        df_filtrado = df_sin_mant.copy()
    elif tipo_mantenimiento == 'con':
        df_filtrado = df_con_mant.copy()
    else:  # todos
        df_filtrado = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    
    if 'todos' not in cliente:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(cliente)]
    
    if 'todos' not in mes:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(mes)]
    
    flotas_unicas = sorted(df_filtrado['Unidad'].dropna().unique())
    
    opciones = [{'label': 'Todas', 'value': 'todos'}]
    opciones.extend([{'label': f'Unidad {str(flota)}', 'value': flota} for flota in flotas_unicas])
    
    # Siempre retornar 'todos' como valor default
    return opciones, ['todos']

# Callback actualizado para el dashboard de costos
@callback(
    [Output('kpi-cards-costos', 'children'),
     Output('pie-chart-costos', 'figure'),
     Output('cost-cards-costos', 'children'),
     Output('line-chart-costos', 'figure')],
    [Input('filtro-mantenimiento-costos', 'value'),
     Input('filtro-mes-costos', 'value'),
     Input('filtro-cliente-costos', 'value'),
     Input('filtro-flota-costos', 'value')]
)
def update_costs_dashboard(tipo_mantenimiento, mes, cliente, flota):
    
    # Preparar datos según período
    if tipo_mantenimiento == 'sin':
        df_active = df_sin_mant.copy()
        cpk_column = 'cpk_parcial'
        show_maintenance = False
    elif tipo_mantenimiento == 'con':
        df_active = df_con_mant.copy()
        cpk_column = 'cpk_total'
        show_maintenance = True
    else:  
        df_sin = df_sin_mant.copy()
        df_sin['periodo'] = 'Sin Mantenimiento'
        df_sin['cpk_total'] = df_sin['cpk_parcial'] 
        
        df_con = df_con_mant.copy()
        df_con['periodo'] = 'Con Mantenimiento'
        
        df_active = pd.concat([df_sin, df_con], ignore_index=True)
        cpk_column = 'cpk_total'
        show_maintenance = True
    
    # Aplicar filtros
    if 'todos' not in mes:
        df_active = df_active[df_active['Mes'].isin(mes)]
    
    if 'todos' not in cliente:
        df_active = df_active[df_active['Cliente'].isin(cliente)]
    
    if 'todos' not in flota:
        df_active = df_active[df_active['Unidad'].isin(flota)]
    
    # Validar que hay datos
    if df_active.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No hay datos para los filtros seleccionados", 
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=azul_2, family='Roboto')
        )
        empty_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        return [], empty_fig, [], empty_fig
    
    # 1. Calcular KPIs
    cpk_promedio = df_active[cpk_column].mean()
    cpk_maximo = df_active[cpk_column].max()
    cpk_minimo = df_active[df_active[cpk_column] > 0][cpk_column].min() if len(df_active[df_active[cpk_column] > 0]) > 0 else 0
    desviacion_std = df_active[cpk_column].std()
    
    kpi_cards = dbc.Row([
        dbc.Col([create_kpi_card_costos("CPK PROMEDIO", cpk_promedio, "$/km", azul)], width=3),
        dbc.Col([create_kpi_card_costos("CPK MÁXIMO", cpk_maximo, "$/km", negative)], width=3),
        dbc.Col([create_kpi_card_costos("CPK MÍNIMO", cpk_minimo, "$/km", success)], width=3),
        dbc.Col([create_kpi_card_costos("DESVIACIÓN ESTD.", desviacion_std, "$/km", azul_2)], width=3),
    ])
    
    # 2. Gráfico de Pie - Distribución de costos
    cost_data = {
        'Combustible': df_active['Costo por carga'].sum(),
        'Casetas': df_active['Costo Caseta'].sum()
    }
    
    if show_maintenance and 'mantenimiento_total' in df_active.columns:
        cost_data['Mantenimiento'] = df_active['mantenimiento_total'].sum()
    
    colors = [amarillo, azul_3, negative] if show_maintenance else [amarillo, azul_3]
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=list(cost_data.keys()),
        values=list(cost_data.values()),
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Costo: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    pie_fig.update_layout(
        showlegend=True,
        height=400,
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto')
    )
    
    # 3. Tarjetas de Costos
    cost_cards_children = [
        dbc.Row([
            dbc.Col([create_cost_card_costos("Combustible", cost_data['Combustible'], amarillo)], width=12),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([create_cost_card_costos("Casetas", cost_data['Casetas'], azul_3)], width=12),
        ], className="mb-3" if show_maintenance else "")
    ]
    
    if show_maintenance and 'Mantenimiento' in cost_data:
        cost_cards_children.append(
            dbc.Row([
                dbc.Col([create_cost_card_costos("Mantenimiento", cost_data.get('Mantenimiento', 0), negative)], width=12),
            ])
        )
    
    cost_cards = html.Div(cost_cards_children)
    
    # 4. Gráfico de líneas - Evolución CPK
    if 'Mes' in df_active.columns:
        df_time = df_active.groupby('Mes').agg({
            cpk_column: 'mean',
            'kmstotales': 'sum',
            'Costo por carga': 'sum',
            'Costo Caseta': 'sum'
        }).reset_index()
        
        # Calcular CPK por componente
        df_time['CPK_Combustible'] = df_time['Costo por carga'] / df_time['kmstotales']
        df_time['CPK_Casetas'] = df_time['Costo Caseta'] / df_time['kmstotales']
        
        if show_maintenance and 'mantenimiento_total' in df_active.columns:
            df_time['Mantenimiento_Total'] = df_active.groupby('Mes')['mantenimiento_total'].sum().values
            df_time['CPK_Mantenimiento'] = df_time['Mantenimiento_Total'] / df_time['kmstotales']
    
        line_fig = go.Figure()
        
        # Línea principal - CPK Total/Parcial
        line_fig.add_trace(go.Scatter(
            x=df_time['Mes'], 
            y=df_time[cpk_column],
            mode='lines+markers',
            name=f'CPK {"Total" if show_maintenance else "Parcial"}',
            line=dict(color=azul, width=4),
            marker=dict(size=10)
        ))
        
        # Líneas de componentes
        line_fig.add_trace(go.Scatter(
            x=df_time['Mes'], 
            y=df_time['CPK_Combustible'],
            mode='lines+markers',
            name='CPK Combustible',
            line=dict(color=amarillo, width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
        line_fig.add_trace(go.Scatter(
            x=df_time['Mes'], 
            y=df_time['CPK_Casetas'],
            mode='lines+markers',
            name='CPK Casetas',
            line=dict(color=azul_3, width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
        if show_maintenance and 'CPK_Mantenimiento' in df_time.columns:
            line_fig.add_trace(go.Scatter(
                x=df_time['Mes'], 
                y=df_time['CPK_Mantenimiento'],
                mode='lines+markers',
                name='CPK Mantenimiento',
                line=dict(color=negative, width=2, dash='dot'),
                marker=dict(size=6)
            ))
        
        line_fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="CPK ($/km)",
            hovermode='x unified',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Roboto'),
            showlegend=True,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1,
                font=dict(size=12)
            ),
            xaxis=dict(showgrid=True, gridcolor=azul_claro),
            yaxis=dict(showgrid=True, gridcolor=azul_claro)
        )
    else:
        line_fig = go.Figure()
    
    return kpi_cards, pie_fig, cost_cards, line_fig

# %%
# LAYOUT KM
def categorize_km(km_value):
    """Categorizar kilómetros en rangos"""
    if km_value == 0:
        return "0 km"
    elif 0 < km_value <= 1000:
        return "1-1000 km"
    elif 1000 < km_value <= 5000:
        return "1001-5000 km"
    elif 5000 < km_value <= 10000:
        return "5001-10,000 km"
    else:
        return "10,001 km+"

# Agregar columna de rangos a los dataframes
df_sin_mant['Rango_KM'] = df_sin_mant['kmstotales'].apply(categorize_km)
df_con_mant['Rango_KM'] = df_con_mant['kmstotales'].apply(categorize_km)

#Crear indicadores
def create_cpk_indicator_km(cpk_value, total_units): 
    return dbc.Card([
    dbc.CardBody([
        html.Div([
            html.H1(
                f"${cpk_value:.2f}",
                style={
                    'color': azul,
                    'fontWeight': 'bold',
                    'margin': '0',
                    'fontSize': '3rem',
                    'fontFamily': 'Roboto'
                }
            ),
            html.H4(
                "CPK Promedio",
                style={
                    'color': negro,
                    'margin': '10px 0 5px 0',
                    'fontWeight': 'normal',
                    'fontFamily': 'Roboto'
                }
            ),
            html.P(
                f"Basado en {total_units} unidades",
                style={
                    'color': negro,
                    'margin': '0',
                    'fontSize': '14px',
                    'fontFamily': 'Roboto'
                }
            )
        ],
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'height': '100%',
            'textAlign': 'center'
        })
    ])
], style={
    'height': '400px',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
    'border': f'3px solid {azul_3}',
    'borderRadius': '15px',
    'background': f'linear-gradient(100deg, {blanco} 0%, {azul_claro} 90%)'
})

# Layout de Análisis por km
def layout_km():
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Análisis por Kilómetros", 
                       style={
                           'color': azul, 
                           'marginBottom': '10px', 
                           'fontWeight': 'bold',
                           'fontFamily': 'Roboto'
                       })
            ])
        ]),
        
        dbc.Row([
            # Filtro de mantenimiento
            dbc.Col([
                html.Label("Tipo de análisis:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.RadioItems(
                    id='filtro-mantenimiento-km',
                    options=[
                        {'label': ' Sin Mantenimiento (2024)', 'value': 'sin'},
                        {'label': ' Con Mantenimiento (2025)', 'value': 'con'},
                        {'label': ' Todos los períodos', 'value': 'todos'}
                    ],
                    value='todos',  
                    inline=True,
                    labelStyle={'margin-right': '20px'},
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de mes
            dbc.Col([
                html.Label("Mes:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-mes-km',
                    options=[],  
                    value='todos',
                    multi = True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de cliente
            dbc.Col([
                html.Label("Cliente:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-cliente-km',
                    options=[],  
                    value='todos',
                    multi = True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de flota
            dbc.Col([
                html.Label("Flota (Unidad):", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-flota-km',
                    options=[],
                    value='todos',
                    multi = True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        ], className="mb-4", style={
            'backgroundColor': azul_claro, 
            'padding': '20px', 
            'borderRadius': '10px', 
            'border': '2px solid ' + azul_claro,
            'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'
        }),
        
        
        # Filtros por rango de kilometraje
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Filtro por Rangos de Kilometraje", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        html.Div([
                            html.P("Selecciona el rango de kilómetros para analizar:",
                                   style={'marginBottom': '15px', 'color': negro, 'fontFamily': 'Roboto'}),
                            html.Div(id='km-filter-buttons')
                        ])
                    ])
                ], style={'border': f'1px solid {azul_claro}', 'marginBottom': '20px'})
            ])
        ]),
        
        # Indicador principal y gráfico de pastel
        dbc.Row([
            dbc.Col([
                html.Div(id='cpk-indicator-km')
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Composición de Costos", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='pie-chart-km')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ], width=8)
        ], style={'marginBottom': '20px'}),
        
        # Info adicional
        dbc.Row([
            dbc.Col([
                html.Div(id='summary-stats-km')
            ])
        ]),
        
        dcc.Store(id='selected-km-range', data='todos')
    ])

# Callback para actualizar opciones de mes y cliente según mantenimiento (km)
@callback(
    [Output('filtro-mes-km', 'options'),
     Output('filtro-mes-km', 'value'),
     Output('filtro-cliente-km', 'options'),
     Output('filtro-cliente-km', 'value')],
    Input('filtro-mantenimiento-km', 'value')
)
def actualizar_opciones_filtros_km(tipo_mantenimiento):
    if tipo_mantenimiento == 'sin':
        df = df_sin_mant
    elif tipo_mantenimiento == 'con':
        df = df_con_mant
    else: 
        df = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    # Opciones de mes
    meses_opciones = [{'label': 'Todos', 'value': 'todos'}]
    meses_opciones.extend([{'label': mes, 'value': mes} for mes in sorted(df['Mes'].unique())])
    
    # Opciones de cliente
    clientes_opciones = [{'label': 'Todos', 'value': 'todos'}]
    clientes_opciones.extend([{'label': cliente, 'value': cliente} for cliente in sorted(df['Cliente'].unique())])
    
    return meses_opciones, ['todos'], clientes_opciones, ['todos']

# Callback para actualizar opciones de flota (km)
@callback(
    [Output('filtro-flota-km', 'options'),
     Output('filtro-flota-km', 'value')],
    [Input('filtro-mantenimiento-km', 'value'),
     Input('filtro-cliente-km', 'value'),
     Input('filtro-mes-km', 'value')]
)
def actualizar_opciones_flota_km(tipo_mantenimiento, cliente, mes):
    if tipo_mantenimiento == 'sin':
        df_filtrado = df_sin_mant.copy()
    elif tipo_mantenimiento == 'con':
        df_filtrado = df_con_mant.copy()
    else: 
        df_filtrado = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    # Filtrar por cliente
    if isinstance(cliente, list):
        if 'todos' not in cliente and len(cliente) > 0:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(cliente)]
    elif cliente != 'todos':
        df_filtrado = df_filtrado[df_filtrado['Cliente'] == cliente]
    
    # Filtrar por mes
    if isinstance(mes, list):
        if 'todos' not in mes and len(mes) > 0:
            df_filtrado = df_filtrado[df_filtrado['Mes'].isin(mes)]
    elif mes != 'todos':
        df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
    
    # opciones de flota
    flotas_unicas = sorted(df_filtrado['Unidad'].dropna().unique())
    
    opciones = [{'label': 'Todas', 'value': 'todos'}]
    opciones.extend([{'label': f'Unidad {int(flota)}', 'value': flota} for flota in flotas_unicas])
    
    return opciones, ['todos']

@callback(
    Output('km-segment-indicator', 'children'),
    [Input('filtro-mantenimiento-km', 'value'),
     Input('filtro-mes-km', 'value'),
     Input('filtro-cliente-km', 'value'),
     Input('filtro-flota-km', 'value')]
)
def mostrar_segmento_km(tipo_mantenimiento, mes, cliente, flota):
    
    if tipo_mantenimiento == 'sin':
        df_filtrado = df_sin_mant.copy()
    elif tipo_mantenimiento == 'con':
        df_filtrado = df_con_mant.copy()
    else:  
        df_filtrado = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    # Aplicar filtros - mes
    if isinstance(mes, list):
        if 'todos' not in mes and len(mes) > 0:
            df_filtrado = df_filtrado[df_filtrado['Mes'].isin(mes)]
    elif mes != 'todos':
        df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
    
    # Aplicar filtros - cliente
    if isinstance(cliente, list):
        if 'todos' not in cliente and len(cliente) > 0:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(cliente)]
    elif cliente != 'todos':
        df_filtrado = df_filtrado[df_filtrado['Cliente'] == cliente]
    
    # Aplicar filtros - flota
    if isinstance(flota, list):
        if 'todos' not in flota and len(flota) > 0:
            df_filtrado = df_filtrado[df_filtrado['Unidad'].isin(flota)]
    elif flota != 'todos' and flota is not None:
        df_filtrado = df_filtrado[df_filtrado['Unidad'] == flota]

# Callback para clicks en los botones de kilometraje
@callback(
    Output('selected-km-range', 'data'),
    [Input({'type': 'km-filter-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State('selected-km-range', 'data')],
    prevent_initial_call=True
)
def update_selected_range(n_clicks_list, current_range):
    """Actualizar rango seleccionado cuando se hace clic en un botón"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return 'todos'
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Extraer el índice del botón clickeado
    import json
    button_info = json.loads(triggered_id.split('.')[0])
    selected_range = button_info['index']
    
    return selected_range

# Callback actualizado para los botones de filtro
@callback(
    Output('km-filter-buttons', 'children'),
    [Input('filtro-mantenimiento-km', 'value'),
     Input('filtro-mes-km', 'value'),
     Input('filtro-cliente-km', 'value'),
     Input('filtro-flota-km', 'value'),
     Input('selected-km-range', 'data')]
)
def update_km_filter_buttons(tipo_mantenimiento, mes, cliente, flota, selected_range):
    if tipo_mantenimiento == 'sin':
        df_active = df_sin_mant.copy()
    elif tipo_mantenimiento == 'con':
        df_active = df_con_mant.copy()
    else: 
        df_active = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    # Aplicar filtros - mes
    if isinstance(mes, list):
        if 'todos' not in mes and len(mes) > 0:
            df_active = df_active[df_active['Mes'].isin(mes)]
    elif mes != 'todos':
        df_active = df_active[df_active['Mes'] == mes]
    
    # Aplicar filtros - cliente
    if isinstance(cliente, list):
        if 'todos' not in cliente and len(cliente) > 0:
            df_active = df_active[df_active['Cliente'].isin(cliente)]
    elif cliente != 'todos':
        df_active = df_active[df_active['Cliente'] == cliente]
    
    # Aplicar filtros - flota
    if isinstance(flota, list):
        if 'todos' not in flota and len(flota) > 0:
            df_active = df_active[df_active['Unidad'].isin(flota)]
    elif flota != 'todos' and flota is not None:
        df_active = df_active[df_active['Unidad'] == flota]
    
    range_counts = df_active['Rango_KM'].value_counts()
    
    # Crear botones
    buttons = [
        dbc.Button(
            f"Todos ({len(df_active)} unidades)",
            id={'type': 'km-filter-btn', 'index': 'todos'},
            color='warning' if selected_range == 'todos' else 'secondary',  # Cambiar color si está seleccionado
            outline=selected_range != 'todos',  # Sin outline si está seleccionado
            size='sm',
            style={
                'margin': '5px',
                'borderRadius': '20px',
                'fontWeight': 'bold',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'fontFamily': 'Roboto',
                'backgroundColor': amarillo_2 if selected_range == 'todos' else None,
                'border': 'none' if selected_range == 'todos' else None
            }
        )
    ]
    
    # Rangos ordenados
    ranges_order = ["0 km", "1-1000 km", "1001-5000 km", "5001-10,000 km", "10,001 km+"] 
    
    for rango in ranges_order:
        count = range_counts.get(rango, 0)
        if count > 0:
            is_selected = selected_range == rango
            buttons.append(
                dbc.Button(
                    f"{rango} ({count})",
                    id={'type': 'km-filter-btn', 'index': rango},
                    color='primary' if is_selected else 'secondary',
                    outline=not is_selected,
                    size='sm',
                    style={
                        'margin': '5px',
                        'borderRadius': '20px',
                        'fontFamily': 'Roboto',
                        'fontWeight': 'bold' if is_selected else 'normal'
                    }
                )
            )
    
    return buttons

# Callback actualizado para el análisis principal
@callback(
    [Output('cpk-indicator-km', 'children'),
     Output('pie-chart-km', 'figure'),
     Output('summary-stats-km', 'children')],
    [Input('filtro-mantenimiento-km', 'value'),
     Input('filtro-mes-km', 'value'),
     Input('filtro-cliente-km', 'value'),
     Input('filtro-flota-km', 'value'),
     Input('selected-km-range', 'data')]
)
def update_analysis_dashboard_km(tipo_mantenimiento, mes, cliente, flota, selected_range):
    
    if tipo_mantenimiento == 'sin':
        df_active = df_sin_mant.copy()
        cpk_column = 'cpk_parcial'
    elif tipo_mantenimiento == 'con':
        df_active = df_con_mant.copy()
        cpk_column = 'cpk_total'
    else:
        df_sin = df_sin_mant.copy()
        df_sin['cpk_total'] = df_sin['cpk_parcial']  # Para consistencia
        df_con = df_con_mant.copy()
        df_active = pd.concat([df_sin, df_con], ignore_index=True)
        cpk_column = 'cpk_total'
    
    # Aplicar filtros - mes
    if isinstance(mes, list):
        if 'todos' not in mes and len(mes) > 0:
            df_active = df_active[df_active['Mes'].isin(mes)]
    elif mes != 'todos':
        df_active = df_active[df_active['Mes'] == mes]
    
    # Aplicar filtros - cliente
    if isinstance(cliente, list):
        if 'todos' not in cliente and len(cliente) > 0:
            df_active = df_active[df_active['Cliente'].isin(cliente)]
    elif cliente != 'todos':
        df_active = df_active[df_active['Cliente'] == cliente]
    
    # Aplicar filtros - flota
    if isinstance(flota, list):
        if 'todos' not in flota and len(flota) > 0:
            df_active = df_active[df_active['Unidad'].isin(flota)]
    elif flota != 'todos' and flota is not None:
        df_active = df_active[df_active['Unidad'] == flota]
    
    # Aplicar filtro de rango de kilometraje
    if selected_range != 'todos':
        df_active = df_active[df_active['Rango_KM'] == selected_range]
    
    # Validar que hay datos
    if df_active.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No hay datos para los filtros seleccionados", 
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=azul_2, family='Roboto')
        )
        empty_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        return [], empty_fig, []

    # 1. Calcular CPK promedio 
    df_with_km = df_active[df_active['kmstotales'] > 0]
    
    if len(df_with_km) > 0:
        cpk_promedio = df_with_km[cpk_column].mean()
    else:
        cpk_promedio = 0
    
    total_units = len(df_active)  
    
    cpk_indicator = create_cpk_indicator_km(cpk_promedio, total_units)
    
    # 2. Gráfico de pastel - Composición de costos (con datos filtrados)
    cost_totals = {
        'Combustible': df_active['Costo por carga'].sum(),
        'Casetas': df_active['Costo Caseta'].sum()
    }
    
    # Agregar mantenimiento solo si está disponible
    if 'mantenimiento_total' in df_active.columns and tipo_mantenimiento != 'sin':
        cost_totals['Mantenimiento'] = df_active['mantenimiento_total'].sum()
    
    # Filtrar costos con valor > 0
    cost_totals = {k: v for k, v in cost_totals.items() if v > 0}
    
    # Si no hay costos, mostrar mensaje
    if not cost_totals:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No hay costos para mostrar", 
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=azul_2, family='Roboto')
        )
        empty_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        pie_fig = empty_fig
    else:
        color_map = {
            'Combustible': amarillo,
            'Mantenimiento': negative,
            'Casetas': azul_3
        }
        
        pie_colors = [color_map.get(label, azul) for label in cost_totals.keys()]
        
        pie_fig = go.Figure(data=[go.Pie(
            labels=list(cost_totals.keys()),
            values=list(cost_totals.values()),
            hole=0.4,
            marker_colors=pie_colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Costo Total: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        pie_fig.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Roboto'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
    
    # 3. Estadísticas resumidas (con datos filtrados)
    total_km = df_active['kmstotales'].sum()
    total_cost = sum(cost_totals.values()) if cost_totals else 0
    avg_km_per_unit = df_active['kmstotales'].mean() if len(df_active) > 0 else 0
    
    summary_stats = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_units:,}", 
                           style={'color': azul, 'fontWeight': 'bold', 'margin': '0', 'fontFamily': 'Roboto'}),
                    html.P("Unidades Analizadas", 
                           style={'color': negro, 'margin': '5px 0 0 0', 'fontFamily': 'Roboto'})
                ], style={'textAlign': 'center'})
            ], style={'height': '100px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                     'border': f'1px solid {azul_claro}', 'borderRadius': '10px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_km:,.0f}", 
                           style={'color': success, 'fontWeight': 'bold', 'margin': '0', 'fontFamily': 'Roboto'}),
                    html.P("Kilómetros Totales", 
                           style={'color': negro, 'margin': '5px 0 0 0', 'fontFamily': 'Roboto'})
                ], style={'textAlign': 'center'})
            ], style={'height': '100px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                     'border': f'1px solid {azul_claro}', 'borderRadius': '10px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${total_cost:,.0f}", 
                           style={'color': negative, 'fontWeight': 'bold', 'margin': '0', 'fontFamily': 'Roboto'}),
                    html.P("Costo Total", 
                           style={'color': negro, 'margin': '5px 0 0 0', 'fontFamily': 'Roboto'})
                ], style={'textAlign': 'center'})
            ], style={'height': '100px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                     'border': f'1px solid {azul_claro}', 'borderRadius': '10px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_km_per_unit:,.0f}", 
                           style={'color': azul_2, 'fontWeight': 'bold', 'margin': '0', 'fontFamily': 'Roboto'}),
                    html.P("Promedio KM/Unidad", 
                           style={'color': negro, 'margin': '5px 0 0 0', 'fontFamily': 'Roboto'})
                ], style={'textAlign': 'center'})
            ], style={'height': '100px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                     'border': f'1px solid {azul_claro}', 'borderRadius': '10px'})
        ], width=3),
    ])
    
    return cpk_indicator, pie_fig, summary_stats

# %%
# Layout de Rankings
def layout_rankings():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("Rankings - CPK por Unidad, Cliente o Proyecto", 
                       style={'color': azul, 'fontWeight': 'bold', 'fontFamily': 'Roboto', 'marginBottom': '10px'}),
                html.P("Visualiza las mejores y peores unidades, clientes o proyectos según su CPK",
                       style={'color': negro, 'fontSize': '16px', 'fontFamily': 'Roboto', 'marginBottom': '30px'})
            ])
        ]),
        
        dbc.Row([
            # Filtro de mantenimiento
            dbc.Col([
                html.Label("Tipo de análisis:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.RadioItems(
                    id='filtro-mantenimiento-ranking',
                    options=[
                        {'label': ' Sin Mantenimiento (2024)', 'value': 'sin'},
                        {'label': ' Con Mantenimiento (2025)', 'value': 'con'},
                        {'label': ' Todos los períodos', 'value': 'todos'}
                    ],
                    value='todos',
                    inline=True,
                    labelStyle={'margin-right': '20px'},
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de mes
            dbc.Col([
                html.Label("Mes:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-mes-ranking',
                    options=[], 
                    value=['todos'],
                    multi=True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de categoría
            dbc.Col([
                html.Label("Categoría:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-categoria-ranking',
                    options=[
                        {'label': 'Unidad', 'value': 'Unidad'},
                        {'label': 'Cliente', 'value': 'Cliente'},
                        {'label': 'Proyecto', 'value': 'Proyecto'}
                    ],
                    value='Unidad',
                    multi=False,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro tipo ranking
            dbc.Col([
                html.Label("Tipo de Ranking:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-tipo-ranking',
                    options=[
                        {'label': 'Top 10 (Mejores)', 'value': 'top'},
                        {'label': 'Bottom 10 (Peores)', 'value': 'bottom'}
                    ],
                    value='top',
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        ], className="mb-4", style={
            'backgroundColor': azul_claro, 
            'padding': '20px', 
            'borderRadius': '10px', 
            'border': '2px solid ' + azul_claro,
            'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'
        }),
        
        # KPIs del ranking
        dbc.Row([
            dbc.Col(html.Div(id='kpis-ranking'))
        ], className="mb-4"),
        
        # Gráfico principal
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Ranking de CPK", 
                               id="titulo-ranking",
                               style={'marginBottom': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-ranking")
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ])
        ], className="mb-4"),
        
        # Tabla de detalles
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Tabla de Detalles", 
                               style={'marginBottom': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id="tabla-ranking",
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'fontFamily': 'Roboto',
                                'fontSize': '14px'
                            },
                            style_header={
                                'fontWeight': 'bold',
                                'backgroundColor': azul_claro,
                                'color': azul,
                                'fontFamily': 'Roboto'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            page_size=10
                        )
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ])
        ])
    ])

# Callback para actualizar opciones de mes según mantenimiento (ranking)
@callback(
    [Output('filtro-mes-ranking', 'options'),
     Output('filtro-mes-ranking', 'value')],
    Input('filtro-mantenimiento-ranking', 'value')
)
def actualizar_opciones_mes_ranking(tipo_mantenimiento):
    if tipo_mantenimiento == 'sin':
        df = df_sin_mant
    elif tipo_mantenimiento == 'con':
        df = df_con_mant
    else:  
        df = pd.concat([df_sin_mant, df_con_mant], ignore_index=True)
    
    meses_opciones = [{'label': 'Todos', 'value': 'todos'}]
    meses_opciones.extend([{'label': mes, 'value': mes} for mes in sorted(df['Mes'].unique())])

    return meses_opciones, ['todos']

# Callback principal 
@callback(
    [Output("grafico-ranking", "figure"),
     Output("tabla-ranking", "data"),
     Output("tabla-ranking", "columns"),
     Output("titulo-ranking", "children"),
     Output("kpis-ranking", "children")],
    [Input('filtro-mantenimiento-ranking', 'value'),
     Input('filtro-mes-ranking', 'value'),
     Input('filtro-categoria-ranking', 'value'),
     Input('filtro-tipo-ranking', 'value')]
)
def actualizar_dashboard_ranking(tipo_mantenimiento, meses, categoria, tipo_ranking):
    
    if tipo_mantenimiento == 'sin':
        df_active = df_sin_mant.copy()
        cpk_column = 'cpk_parcial'
        periodo_texto = "Sin Mantenimiento (2024)"
    elif tipo_mantenimiento == 'con':
        df_active = df_con_mant.copy()
        cpk_column = 'cpk_total'
        periodo_texto = "Con Mantenimiento (2025)"
    else:  
        df_sin = df_sin_mant.copy()
        df_sin['cpk_total'] = df_sin['cpk_parcial']  
        df_con = df_con_mant.copy()
        df_active = pd.concat([df_sin, df_con], ignore_index=True)
        cpk_column = 'cpk_total'
        periodo_texto = "Todos los Períodos"
    
    # Filtrar por mes
    if isinstance(meses, list):
        if 'todos' not in meses and len(meses) > 0:
            df_active = df_active[df_active['Mes'].isin(meses)]
    
    # Filtrar valores válidos
    df_filtrado = df_active[df_active[cpk_column] > 0].copy()
    
    if df_filtrado.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No hay datos para los filtros seleccionados",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=azul_2, family='Roboto')
        )
        empty_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        return empty_fig, [], [], "Sin datos", []
    
    agg_dict = {
        cpk_column: 'mean',
        'kmstotales': 'sum'
    }
    
    # Solo agregar Unidad si no estamos agrupando por ella
    if categoria != 'Unidad':
        agg_dict['Unidad'] = 'nunique'
    
    df_agg = df_filtrado.groupby(categoria).agg(agg_dict).reset_index()
    
    if categoria == 'Unidad':
        df_agg['num_unidades'] = 1
    else:
        df_agg.rename(columns={'Unidad': 'num_unidades'}, inplace=True)
    
    # Renombrar 
    df_agg.columns = [categoria, 'CPK_Promedio', 'KM_Totales', 'Num_Unidades']
    
    # Ordenar y tomar top/bottom 10
    df_agg = df_agg.sort_values(by='CPK_Promedio', ascending=(tipo_ranking == "top")).head(10)
    
    titulo = f"{'Top' if tipo_ranking == 'top' else 'Bottom'} 10 - {categoria} ({periodo_texto})"
    if isinstance(meses, list) and 'todos' not in meses and len(meses) > 0:
        titulo += f" - {', '.join(meses)}"
    
    # gráfico de barras de top y bottom
    color_bar = success if tipo_ranking == "top" else negative
    
    fig = px.bar(
        df_agg,
        x=categoria,
        y='CPK_Promedio',
        text='CPK_Promedio',
        color_discrete_sequence=[color_bar]
    )
    
    fig.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_type='category',
        yaxis_title="CPK Promedio ($/km)",
        xaxis_title=categoria,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto'),
        height=500,
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=azul_claro)
    )
    
    #KPIs
    mejor_cpk = df_agg['CPK_Promedio'].min() if tipo_ranking == "top" else df_agg['CPK_Promedio'].max()
    peor_cpk = df_agg['CPK_Promedio'].max() if tipo_ranking == "top" else df_agg['CPK_Promedio'].min()
    promedio_cpk = df_agg['CPK_Promedio'].mean()
    total_km = df_agg['KM_Totales'].sum()
    
    kpis = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${mejor_cpk:.2f}", 
                           style={'color': success if tipo_ranking == "top" else negative, 
                                 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P(f"{'Mejor' if tipo_ranking == 'top' else 'Peor'} CPK", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${promedio_cpk:.2f}", 
                           style={'color': azul, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("CPK Promedio del Grupo", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${abs(mejor_cpk - peor_cpk):.2f}", 
                           style={'color': amarillo, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("Rango de Variación", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_km:,.0f}", 
                           style={'color': azul_2, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("KM Totales", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
    ])
    
    df_tabla = df_agg.copy()
    df_tabla['CPK_Promedio'] = df_tabla['CPK_Promedio'].round(2)
    df_tabla['KM_Totales'] = df_tabla['KM_Totales'].round(0).astype(int)
    
    # Agregar ranking
    df_tabla['Ranking'] = range(1, len(df_tabla) + 1)
    df_tabla = df_tabla[['Ranking', categoria, 'CPK_Promedio', 'KM_Totales', 'Num_Unidades']]
    
    data = df_tabla.to_dict("records")
    columns = [
        {"name": "Ranking", "id": "Ranking"},
        {"name": categoria, "id": categoria},
        {"name": "CPK Promedio ($/km)", "id": "CPK_Promedio", "type": "numeric", "format": {"specifier": "$.2f"}},
        {"name": "KM Totales", "id": "KM_Totales", "type": "numeric", "format": {"specifier": ","}},
        {"name": "Unidades", "id": "Num_Unidades"}
    ]
    
    return fig, data, columns, titulo, kpis

# %%
#Layout Fuzzy
def layout_fuzzy():
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Monitoreo Fuzzy - Análisis de Riesgo", 
                       style={'color': azul, 'fontWeight': 'bold', 'fontFamily': 'Roboto', 'marginBottom': '10px'}),
                html.P("Basado en lógica difusa (Solo datos 2025)",
                       style={'color': negro, 'fontSize': '16px', 'fontFamily': 'Roboto', 'marginBottom': '30px'})
            ])
        ]),
        
        dbc.Row([
            # Filtro de mes
            dbc.Col([
                html.Label("Mes:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-mes-fuzzy',
                    options=[],  
                    value=['todos'],
                    multi=True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de cliente
            dbc.Col([
                html.Label("Cliente:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-cliente-fuzzy',
                    options=[],  
                    value=['todos'],
                    multi=True,
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
            
            # Filtro de flota
            dbc.Col([
                html.Label("Flota (Unidad):", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.Dropdown(
                    id='filtro-flota-fuzzy',
                    options=[],
                    value='todos',
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        
            
            # Filtro de categoría de riesgo
            dbc.Col([
                html.Label("Categoría de Riesgo:", style={'fontWeight': 'bold', 'color': azul_2}),
                dcc.RadioItems(
                    id='filtro-riesgo-fuzzy',
                    options=[
                        {'label': ' Todos', 'value': 'todos'},
                        {'label': ' Alto', 'value': 'alto'},
                        {'label': ' Medio', 'value': 'medio'},
                        {'label': ' Bajo', 'value': 'bajo'}
                    ],
                    value='todos',
                    inline=True,
                    labelStyle={'margin-right': '15px'},
                    style={'fontFamily': 'Roboto'}
                )
            ], width=3),
        ], className="mb-4", style={
            'backgroundColor': azul_claro, 
            'padding': '10px', 
            'borderRadius': '10px', 
            'border': '2px solid ' + azul_claro,
            'boxShadow': '0px 4px 12px rgba(0, 0, 0, 0.1)'
        }),
        
        # KPIs de Riesgo
        dbc.Row([
            dbc.Col(html.Div(id='kpis-fuzzy'))
        ], className="mb-4"),
        
        dbc.Row([
            # Gráfico de barras interactivo
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Distribución y Análisis por Categoría de Riesgo", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='grafico-barras-fuzzy')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ], width=6),
            
            # Scatter plot CPK vs Riesgo
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("CPK vs Riesgo Difuso", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='scatter-fuzzy')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ], width=6)
        ], className="mb-4"),

        # Boxplot 
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Comparación: Alto Riesgo vs Bajo/Medio Riesgo", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='boxplot-comparacion-fuzzy')
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ])
        ], className="mb-4"),
        
        # Tabla de unidades de alto riesgo
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Unidades con Mayor Riesgo Operativo", 
                               id='titulo-tabla-fuzzy',
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id="tabla-fuzzy",
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'fontFamily': 'Roboto',
                                'fontSize': '14px'
                            },
                            style_header={
                                'fontWeight': 'bold',
                                'backgroundColor': azul_claro,
                                'color': azul,
                                'fontFamily': 'Roboto'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                },
                                {
                                    'if': {
                                        'filter_query': '{categoria_riesgo_difuso} = alto',
                                        'column_id': 'categoria_riesgo_difuso'
                                    },
                                    'backgroundColor': negative,
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{categoria_riesgo_difuso} = medio',
                                        'column_id': 'categoria_riesgo_difuso'
                                    },
                                    'backgroundColor': amarillo,
                                    'color': negro,
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{categoria_riesgo_difuso} = bajo',
                                        'column_id': 'categoria_riesgo_difuso'
                                    },
                                    'backgroundColor': success,
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            ],
                            page_size=15
                        )
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ])
        ])
    ])

# Callback para actualizar opciones de filtros
@callback(
    [Output('filtro-mes-fuzzy', 'options'),
     Output('filtro-cliente-fuzzy', 'options')],
    Input('filtro-mes-fuzzy', 'id')  
)
def actualizar_opciones_fuzzy(_):
    df_riesgo['Mes'] = df_riesgo['Mes'].astype(str)

    # Opciones de mes
    meses_opciones = [{'label': 'Todos', 'value': 'todos'}]
    meses_opciones.extend([{'label': mes, 'value': mes} for mes in sorted(df_riesgo['Mes'].unique())])
    
    # Opciones de cliente
    clientes_opciones = [{'label': 'Todos', 'value': 'todos'}]
    clientes_opciones.extend([{'label': cliente, 'value': cliente} for cliente in sorted(df_riesgo['Cliente'].unique())])
    
    return meses_opciones, clientes_opciones

# Callback para actualizar opciones de filtros
@callback(
    Output('filtro-flota-fuzzy', 'options'),
    [Input('filtro-mes-fuzzy', 'value'),
     Input('filtro-cliente-fuzzy', 'value')]
)
def actualizar_flota_fuzzy(meses, clientes):
    df_filtrado = df_riesgo.copy()
    
    df_filtrado['Mes'] = df_filtrado['Mes'].astype(str)
    
    # Filtrar por mes
    if isinstance(meses, list) and 'todos' not in meses and len(meses) > 0:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
    
    # Filtrar por cliente
    if isinstance(clientes, list) and 'todos' not in clientes and len(clientes) > 0:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]

    # Crear opciones de flotas únicas
    flotas = sorted(df_filtrado['Unidad'].dropna().unique())

    opciones = [{'label': 'Todas', 'value': 'todos'}]
    opciones.extend([{'label': f'Unidad {int(flota)}', 'value': flota} for flota in flotas])

    return opciones

# Callback principal 
@callback(
    [Output('kpis-fuzzy', 'children'),
     Output('grafico-barras-fuzzy', 'figure'),
     Output('scatter-fuzzy', 'figure'),
     Output('boxplot-comparacion-fuzzy', 'figure'),
     Output('tabla-fuzzy', 'data'),
     Output('tabla-fuzzy', 'columns'),
     Output('titulo-tabla-fuzzy', 'children')],
    [Input('filtro-mes-fuzzy', 'value'),
     Input('filtro-cliente-fuzzy', 'value'),
     Input('filtro-flota-fuzzy', 'value'),
     Input('filtro-riesgo-fuzzy', 'value')]
)
def actualizar_dashboard_fuzzy(meses, clientes, flota, categoria_riesgo):
    df_filtrado = df_riesgo.copy()
    
    df_filtrado['Mes'] = df_filtrado['Mes'].astype(str)
    
    # Filtrar por mes
    if isinstance(meses, list) and 'todos' not in meses and len(meses) > 0:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
    
    # Filtrar por cliente
    if isinstance(clientes, list) and 'todos' not in clientes and len(clientes) > 0:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]

    # Filtrar por flota
    if flota != 'todos' and flota is not None:
        df_filtrado = df_filtrado[df_filtrado['Unidad'] == flota]
    
    # Filtrar por categoría de riesgo
    if categoria_riesgo != 'todos':
        df_filtrado = df_filtrado[df_filtrado['categoria_riesgo_difuso'] == categoria_riesgo]
    
    # Verificar si hay datos
    if df_filtrado.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No hay datos para los filtros seleccionados",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=azul_2, family='Roboto')
        )
        empty_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        return [], empty_fig, empty_fig, empty_fig, [], [], "Sin datos"
    
    # 1. KPIs
    total_unidades = df_filtrado['Unidad'].nunique()
    unidades_alto_riesgo = len(df_filtrado[df_filtrado['categoria_riesgo_difuso'] == 'alto']['Unidad'].unique())
    riesgo_promedio = df_filtrado['riesgo_difuso'].mean()
    cpk_promedio = df_filtrado['CPK_total'].mean()
    
    kpis = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_unidades:,}", 
                           style={'color': azul, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("Unidades Totales", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{unidades_alto_riesgo}", 
                           style={'color': negative, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("Unidades Alto Riesgo", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{riesgo_promedio:.2f}", 
                           style={'color': amarillo, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("Riesgo Promedio", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${cpk_promedio:.2f}", 
                           style={'color': azul_2, 'fontWeight': 'bold', 'marginBottom': '0', 'fontFamily': 'Roboto'}),
                    html.P("CPK Promedio", 
                           className="text-muted", 
                           style={'fontSize': '14px', 'fontFamily': 'Roboto', 'marginBottom': '0'})
                ])
            ], style={'border': f'1px solid {azul_claro}', 'borderRadius': '10px', 'height': '90px'})
        ], width=3),
    ])
    
    # 2. Gráfico de barras
    conteo_riesgo = df_filtrado['categoria_riesgo_difuso'].value_counts().reset_index()
    conteo_riesgo.columns = ['categoria', 'conteo']
    
    # subplots
    from plotly.subplots import make_subplots
    
    fig_barras = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Distribución por Riesgo", "Promedios por Variable"),
        column_widths=[0.4, 0.6]
    )
    
    # Gráfico izquierdo - Conteo
    color_map = {'alto': negative, 'medio': amarillo, 'bajo': success}
    colors = [color_map.get(cat, azul) for cat in conteo_riesgo['categoria']]
    
    fig_barras.add_trace(
        go.Bar(
            x=conteo_riesgo['categoria'],
            y=conteo_riesgo['conteo'],
            marker_color=colors,
            name='Unidades',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Gráfico derecho - Promedios
    variables_difusas = ['kmstotales', 'mantenimiento_total', 'Costo por carga']
    promedios = []
    for var in variables_difusas:
        promedio = df_filtrado[var].mean()
        promedios.append(promedio)
    
    fig_barras.add_trace(
        go.Bar(
            x=variables_difusas,
            y=promedios,
            marker_color=[azul_3, negative, amarillo],
            name='Promedio',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig_barras.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto')
    )
    
    # 3. Scatter plot
    fig_scatter = px.scatter(
        df_filtrado,
        x='CPK_total',
        y='riesgo_difuso',
        color='categoria_riesgo_difuso',
        color_discrete_map={'alto': negative, 'medio': amarillo, 'bajo': success},
        hover_data=['Unidad', 'Cliente', 'kmstotales'],
        title=''
    )
    
    fig_scatter.update_traces(marker=dict(size=8))
    fig_scatter.update_layout(
        xaxis_title='CPK Total ($/km)',
        yaxis_title='Valor de Riesgo Difuso',
        legend_title='Categoría de Riesgo',
        xaxis_range=[0, min(150, df_filtrado['CPK_total'].max() * 1.1)],
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto')
    )

    # 4. Boxplot
    alto_riesgo = df_filtrado[df_filtrado['riesgo_difuso'] >= 7].copy()
    bajo_medio_riesgo = df_filtrado[df_filtrado['riesgo_difuso'] < 7].copy()
    
    variables = ['kmstotales', 'mantenimiento_total', 'Costo por carga']
    nombres_variables = ['Kilómetros Totales', 'Mantenimiento Total', 'Costo por Carga']
    
    from plotly.subplots import make_subplots
    fig_boxplot = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Alto Riesgo - Kilómetros', 'Bajo/Medio Riesgo - Kilómetros',
            'Alto Riesgo - Mantenimiento', 'Bajo/Medio Riesgo - Mantenimiento',
            'Alto Riesgo - Combustible', 'Bajo/Medio Riesgo - Combustible'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    for i, (var, nombre) in enumerate(zip(variables, nombres_variables)):

        if len(alto_riesgo) > 0:
            fig_boxplot.add_trace(
                go.Box(
                    y=alto_riesgo[var],
                    name=f'Alto Riesgo',
                    marker_color=negative,
                    showlegend=(i == 0)
                ),
                row=i+1, col=1
            )
        
        # Bajo/Medio riesgo 
        if len(bajo_medio_riesgo) > 0:
            fig_boxplot.add_trace(
                go.Box(
                    y=bajo_medio_riesgo[var],
                    name=f'Bajo/Medio Riesgo',
                    marker_color=azul_3,
                    showlegend=(i == 0)
                ),
                row=i+1, col=2
            )
    fig_boxplot.update_layout(
        height=800,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    fig_boxplot.update_yaxes(title_text="Kilómetros", row=1, col=1)
    fig_boxplot.update_yaxes(title_text="Kilómetros", row=1, col=2)
    fig_boxplot.update_yaxes(title_text="$ Mantenimiento", row=2, col=1)
    fig_boxplot.update_yaxes(title_text="$ Mantenimiento", row=2, col=2)
    fig_boxplot.update_yaxes(title_text="$ Combustible", row=3, col=1)
    fig_boxplot.update_yaxes(title_text="$ Combustible", row=3, col=2)
    
    # 5. Tabla de alto riesgo
    df_tabla = df_filtrado[df_filtrado['riesgo_difuso'] >= 7][[
        'Unidad', 'Mes', 'Cliente', 'CPK_total', 'mantenimiento_total',
        'Costo por carga', 'Costo Caseta', 'kmstotales',
        'riesgo_difuso', 'categoria_riesgo_difuso'
    ]].sort_values(by='riesgo_difuso', ascending=False).head(20)
    
    # Formatear columnas numéricas
    df_tabla['CPK_total'] = df_tabla['CPK_total'].round(2)
    df_tabla['mantenimiento_total'] = df_tabla['mantenimiento_total'].round(0)
    df_tabla['Costo por carga'] = df_tabla['Costo por carga'].round(0)
    df_tabla['Costo Caseta'] = df_tabla['Costo Caseta'].round(0)
    df_tabla['kmstotales'] = df_tabla['kmstotales'].round(0)
    df_tabla['riesgo_difuso'] = df_tabla['riesgo_difuso'].round(2)
    
    data = df_tabla.to_dict("records")
    columns = [
        {"name": "Unidad", "id": "Unidad"},
        {"name": "Mes", "id": "Mes"},
        {"name": "Cliente", "id": "Cliente"},
        {"name": "CPK Total", "id": "CPK_total", "type": "numeric", "format": {"specifier": "$.2f"}},
        {"name": "Mantenimiento", "id": "mantenimiento_total", "type": "numeric", "format": {"specifier": "$,"}},
        {"name": "Combustible", "id": "Costo por carga", "type": "numeric", "format": {"specifier": "$,"}},
        {"name": "Casetas", "id": "Costo Caseta", "type": "numeric", "format": {"specifier": "$,"}},
        {"name": "KM Totales", "id": "kmstotales", "type": "numeric", "format": {"specifier": ","}},
        {"name": "Riesgo", "id": "riesgo_difuso", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Categoría", "id": "categoria_riesgo_difuso"}
    ]
    
    titulo_tabla = f"Unidades con Mayor Riesgo Operativo (≥ 7.0) - {len(df_tabla)} unidades"
    
    return kpis, fig_barras, fig_scatter, fig_boxplot, data, columns, titulo_tabla

# %%
# Función de cálculo actualizada
def calcular_cpk_simulador(precio_gasolina, litros_cargados, kilometros, costo_mantenimiento_total, costo_casetas_total):
    """Calcular CPK basado en los valores del viaje"""
    
    # Costo total de combustible
    costo_combustible_total = precio_gasolina * litros_cargados
    
    # CPK por componente
    cpk_combustible = costo_combustible_total / kilometros if kilometros > 0 else 0
    cpk_mantenimiento = costo_mantenimiento_total / kilometros if kilometros > 0 else 0
    cpk_casetas = costo_casetas_total / kilometros if kilometros > 0 else 0
    
    # CPK total
    cpk_total = cpk_combustible + cpk_mantenimiento + cpk_casetas
    
    return {
        'combustible': cpk_combustible,
        'mantenimiento': cpk_mantenimiento,
        'casetas': cpk_casetas,
        'total': cpk_total,
        'costo_combustible_total': costo_combustible_total,
        'costo_mantenimiento_total': costo_mantenimiento_total,
        'costo_casetas_total': costo_casetas_total
    }

# Layout del simulador
def layout_simulador():
    return html.Div([
        # Header
        html.Div([
            html.H2("Simulador CPK", className="mb-4", style={'color': blanco, 'fontWeight': 'bold', 'fontFamily': 'Roboto'}),
        ], style={
            'background': f"linear-gradient(135deg, {azul} 0%, {azul_2} 100%)",
            'padding': '1rem',
            'border-radius': '12px',
            'margin-bottom': '1rem',
            'text-align': 'center'}),
        
        dbc.Row([
            # Panel de controles
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Parámetros del Viaje", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        # Precio gasolina
                        html.Div([
                            html.Label("Precio de Gasolina ($/litro):", 
                                     style={'fontWeight': 'bold', 'color': azul_2, 'fontFamily': 'Roboto'}),
                            html.Div(id="precio-display-sim", 
                                   style={'color': azul_3, 'fontWeight': 'bold', 'fontSize': '18px', 'fontFamily': 'Roboto'}),
                            dcc.Slider(
                                id='precio-slider-sim', 
                                min=18, 
                                max=30, 
                                step=0.1, 
                                value=24.5,
                                marks={18: '$18', 22: '$22', 26: '$26', 30: '$30'},
                                tooltip={"placement": "bottom", "always_visible": False}
                            )
                        ], className="mb-4"),
                        
                        # Litros a cargar
                        html.Div([
                            html.Label("Litros a cargar en el viaje:", 
                                     style={'fontWeight': 'bold', 'color': azul_2, 'fontFamily': 'Roboto'}),
                            html.Div(id="litros-display-sim", 
                                   style={'color': azul_3, 'fontWeight': 'bold', 'fontSize': '18px', 'fontFamily': 'Roboto'}),
                            dcc.Slider(
                                id='litros-slider-sim', 
                                min=50, 
                                max=500, 
                                step=10, 
                                value=200,
                                marks={50: '50L', 200: '200L', 350: '350L', 500: '500L'},
                                tooltip={"placement": "bottom", "always_visible": False}
                            )
                        ], className="mb-4"),
                        
                        # Kilómetros de la ruta
                        html.Div([
                            html.Label("Kilómetros de la ruta:", 
                                     style={'fontWeight': 'bold', 'color': azul_2, 'fontFamily': 'Roboto'}),
                            html.Div(id="kilometros-display-sim", 
                                   style={'color': azul_3, 'fontWeight': 'bold', 'fontSize': '18px', 'fontFamily': 'Roboto'}),
                            dcc.Slider(
                                id='kilometros-slider-sim', 
                                min=100, 
                                max=2000, 
                                step=50, 
                                value=800,
                                marks={100: '100km', 600: '600km', 1200: '1200km', 2000: '2000km'},
                                tooltip={"placement": "bottom", "always_visible": False}
                            )
                        ], className="mb-4"),
                        
                        # Costo de mantenimiento
                        html.Div([
                            html.Label("Costo de mantenimiento total ($):", 
                                     style={'fontWeight': 'bold', 'color': azul_2, 'fontFamily': 'Roboto'}),
                            html.Div(id="mantenimiento-display-sim", 
                                   style={'color': azul_3, 'fontWeight': 'bold', 'fontSize': '18px', 'fontFamily': 'Roboto'}),
                            dcc.Slider(
                                id='mantenimiento-slider-sim', 
                                min=0, 
                                max=20000, 
                                step=100, 
                                value=5000,
                                marks={0: '$0', 5000: '$5k', 10000: '$10k', 20000: '$20k'},
                                tooltip={"placement": "bottom", "always_visible": False}
                            )
                        ], className="mb-4"),
                        
                        # Costo de casetas
                        html.Div([
                            html.Label("Costo de casetas total ($):", 
                                     style={'fontWeight': 'bold', 'color': azul_2, 'fontFamily': 'Roboto'}),
                            html.Div(id="casetas-display-sim", 
                                   style={'color': azul_3, 'fontWeight': 'bold', 'fontSize': '18px', 'fontFamily': 'Roboto'}),
                            dcc.Slider(
                                id='casetas-slider-sim', 
                                min=0, 
                                max=5000, 
                                step=50, 
                                value=2000,
                                marks={0: '$0', 1000: '$1k', 3000: '$3k', 5000: '$5k'},
                                tooltip={"placement": "bottom", "always_visible": False}
                            )
                        ], className="mb-4"),
                        
                        # Botón reset
                        dbc.Button(
                            "Restablecer valores", 
                            id="reset-button-sim", 
                            color="warning",
                            outline=True,
                            style={'width': '100%', 'fontFamily': 'Roboto', 'fontWeight': 'bold'}
                        )
                    ])
                ], style={'border': f'1px solid {azul_claro}', 'height': '100%'})
            ], width=5),
            
            # Panel de resultados
            dbc.Col([
                # CPK Total
                dbc.Card([
                    dbc.CardBody([
                        html.H5("CPK TOTAL SIMULADO", 
                               style={'textAlign': 'center', 'color': blanco, 'marginBottom': '10px', 'fontFamily': 'Roboto'}),
                        html.H1(id="cpk-resultado-sim", 
                               style={'textAlign': 'center', 'color': blanco, 'fontWeight': 'bold', 'fontFamily': 'Roboto'})
                    ], style={
                        'background': f"linear-gradient(135deg, {azul} 0%, {azul_3} 100%)",
                        'borderRadius': '12px',
                        'padding': '20px'
                    })
                ], className="mb-3", style={'border': 'none'}),
                
                # Gráfica de composición
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Composición del CPK", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        dcc.Graph(id='grafica-composicion-sim', style={'height': '300px'})
                    ])
                ], style={'border': f'1px solid {azul_claro}'}, className="mb-3"),
                
                # Tabla de resultados detallados
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Desglose Detallado", 
                               style={'margin': '0', 'color': azul, 'fontFamily': 'Roboto'})
                    ], style={'backgroundColor': azul_claro, 'border': 'none'}),
                    dbc.CardBody([
                        html.Div(id="tabla-resultados-sim")
                    ])
                ], style={'border': f'1px solid {azul_claro}'})
            ], width=7)
        ])
    ])

# Callbacks para actualizar displays
@callback(
    [Output('precio-display-sim', 'children'),
     Output('litros-display-sim', 'children'),
     Output('kilometros-display-sim', 'children'),
     Output('mantenimiento-display-sim', 'children'),
     Output('casetas-display-sim', 'children')],
    [Input('precio-slider-sim', 'value'),
     Input('litros-slider-sim', 'value'),
     Input('kilometros-slider-sim', 'value'),
     Input('mantenimiento-slider-sim', 'value'),
     Input('casetas-slider-sim', 'value')]
)
def actualizar_displays(precio, litros, kilometros, mantenimiento, casetas):
    return (
        f"${precio:.1f}",
        f"{litros} litros",
        f"{kilometros:,} km",
        f"${mantenimiento:,}",
        f"${casetas:,}"
    )

# Callback principal 
@callback(
    [Output('cpk-resultado-sim', 'children'),
     Output('grafica-composicion-sim', 'figure'),
     Output('tabla-resultados-sim', 'children')],
    [Input('precio-slider-sim', 'value'),
     Input('litros-slider-sim', 'value'),
     Input('kilometros-slider-sim', 'value'),
     Input('mantenimiento-slider-sim', 'value'),
     Input('casetas-slider-sim', 'value')]
)
def actualizar_simulador(precio, litros, kilometros, mantenimiento, casetas):
    # Calcular CPK
    resultados = calcular_cpk_simulador(precio, litros, kilometros, mantenimiento, casetas)
    
    # 1. CPK Total
    cpk_total_display = f"${resultados['total']:.2f}/km"
    
    # 2. Gráfica de composición
    fig = go.Figure(data=[go.Pie(
        labels=['Combustible', 'Mantenimiento', 'Casetas'],
        values=[resultados['combustible'], resultados['mantenimiento'], resultados['casetas']],
        hole=0.4,
        marker_colors=[amarillo, negative, azul_3],
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>CPK: $%{value:.2f}/km<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=True,
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto')
    )
    
    # 3. Tabla de resultados
    tabla = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Concepto", style={'padding': '10px', 'borderBottom': f'2px solid {azul_claro}'}),
                html.Th("Costo Total", style={'padding': '10px', 'borderBottom': f'2px solid {azul_claro}', 'textAlign': 'right'}),
                html.Th("CPK ($/km)", style={'padding': '10px', 'borderBottom': f'2px solid {azul_claro}', 'textAlign': 'right'})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td("Combustible", style={'padding': '8px', 'fontWeight': 'bold', 'color': azul_2}),
                html.Td(f"${resultados['costo_combustible_total']:,.2f}", style={'padding': '8px', 'textAlign': 'right'}),
                html.Td(f"${resultados['combustible']:.2f}", style={'padding': '8px', 'textAlign': 'right', 'color': amarillo, 'fontWeight': 'bold'})
            ]),
            html.Tr([
                html.Td("Mantenimiento", style={'padding': '8px', 'fontWeight': 'bold', 'color': azul_2}),
                html.Td(f"${resultados['costo_mantenimiento_total']:,.2f}", style={'padding': '8px', 'textAlign': 'right'}),
                html.Td(f"${resultados['mantenimiento']:.2f}", style={'padding': '8px', 'textAlign': 'right', 'color': negative, 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'rgb(248,248,248)'}),
            html.Tr([
                html.Td("Casetas", style={'padding': '8px', 'fontWeight': 'bold', 'color': azul_2}),
                html.Td(f"${resultados['costo_casetas_total']:,.2f}", style={'padding': '8px', 'textAlign': 'right'}),
                html.Td(f"${resultados['casetas']:.2f}", style={'padding': '8px', 'textAlign': 'right', 'color': azul_3, 'fontWeight': 'bold'})
            ]),
            html.Tr([
                html.Td("TOTAL", style={'padding': '8px', 'fontWeight': 'bold', 'color': azul, 'borderTop': f'2px solid {azul_claro}'}),
                html.Td(f"${resultados['costo_combustible_total'] + resultados['costo_mantenimiento_total'] + resultados['costo_casetas_total']:,.2f}", 
                       style={'padding': '8px', 'textAlign': 'right', 'fontWeight': 'bold', 'borderTop': f'2px solid {azul_claro}'}),
                html.Td(f"${resultados['total']:.2f}", 
                       style={'padding': '8px', 'textAlign': 'right', 'color': azul, 'fontWeight': 'bold', 'fontSize': '18px', 'borderTop': f'2px solid {azul_claro}'})
            ], style={'backgroundColor': azul_claro})
        ])
    ], style={'width': '100%', 'fontFamily': 'Roboto'})
    
    return cpk_total_display, fig, tabla

# Callback para reset
@callback(
    [Output('precio-slider-sim', 'value'),
     Output('litros-slider-sim', 'value'),
     Output('kilometros-slider-sim', 'value'),
     Output('mantenimiento-slider-sim', 'value'),
     Output('casetas-slider-sim', 'value')],
    Input('reset-button-sim', 'n_clicks'),
    prevent_initial_call=True
)
def reset_valores(n_clicks):
    # Valores default
    return 24.5, 200, 800, 5000, 2000

# %%
# Layout de Carga de Archivos (versión simple)
def layout_archivos():
    return html.Div([
        html.H2("Carga de Archivos", 
               style={'color': azul, 'fontWeight': 'bold', 'marginBottom': '20px'}),
        
        # Área para subir archivo
        dbc.Card([
            dbc.CardBody([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Arrastra un archivo CSV aquí o ',
                        html.A('haz clic para seleccionar', style={'color': azul})
                    ]),
                    style={
                        'width': '100%',
                        'height': '100px',
                        'lineHeight': '100px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'borderColor': azul_claro,
                        'textAlign': 'center',
                        'backgroundColor': 'white'
                    }
                )
            ])
        ], style={'marginBottom': '20px'}),
        
        html.Div(id='mensaje-carga'),
        
        # Tabla para mostrar datos
        html.Div(id='tabla-datos')
    ])
@callback(
    [Output('mensaje-carga', 'children'),
     Output('tabla-datos', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def cargar_archivo(contents, filename):
    if contents is None:
        return '', ''
    
    try:
        import base64
        import io
        
        # Decodificar el archivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Leer el CSV
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Mensaje de éxito
        mensaje = dbc.Alert(
            f"Archivo '{filename}' cargado correctamente! ({len(df)} filas)",
            color="success"
        )
        
        # Mostrar tabla
        tabla = dash_table.DataTable(
            data=df.head(10).to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': azul_claro,
                'fontWeight': 'bold'
            },
            page_size=10
        )
        
        return mensaje, tabla
        
    except:
        # Mensaje de error
        mensaje = dbc.Alert(
            "✗ Error al cargar el archivo. Asegúrate de que sea un CSV válido.",
            color=amarillo
        )
        return mensaje, ''

# %%
# callbacks

# layout desplegable resumen
@callback(
    Output("submenu-resumen", "is_open"),
    Input("resumen-toggle", "n_clicks"),
    State("submenu-resumen", "is_open")
)
def toggle_resumen_submenu(n, is_open):
    if n:
        return not is_open
    return is_open


# %%
# Callback para navegación entre páginas
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/inicio' or pathname == '/':
        return layout_inicio()
    elif pathname == '/resumen/costos':
        return layout_costos()
    elif pathname == '/resumen/analisiskm':
        return layout_km()
    elif pathname == '/rankings':
        return layout_rankings()
    elif pathname == '/fuzzy':
        return layout_fuzzy()
    elif pathname == '/simulador':
        return layout_simulador()
    elif pathname == '/archivos':
        return layout_archivos()
    else:
        return html.Div([
            html.H1("404: Página no encontrada", className="text-danger"),
            html.P("La página que buscas no existe."),
            dbc.Button("Volver al inicio", href="/inicio", color="primary")
        ])
    
server = app.server
if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=10000)

# %%



