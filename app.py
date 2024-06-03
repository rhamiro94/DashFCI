#Importo librerias
import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
#Defino df en funcion de csv previamente definido
df = pd.read_csv("datos_fci.csv")

# Definir variables que servirán para los dropdowns
categorias = df['Categoria'].unique()
fondos = df['Nombre'].unique()

# Crear la aplicación Dash
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("FCIS ARGY 2024", style={'textAlign': 'center', 'marginBottom': '30px'}),

    html.Div([
        html.Div([
            html.Label("Selecciona un fondo:"),
            dcc.Dropdown(
                id='fondo-dropdown',
                options=[{'label': fondo, 'value': fondo} for fondo in fondos],
                value=[],
                multi=False,
                placeholder="Selecciona un fondo"
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'marginRight': '5%'}),
                # Nuevo dropdown para seleccionar la categoría
        html.Div([
            html.Label("Selecciona una categoría:"),
            dcc.Dropdown(
                id='categoria-dropdown',
                options=[{'label': cat, 'value': cat} for cat in categorias],
                value=categorias[0]
            ),
        ], style={'width': '45%', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px'}),

    dcc.Graph(id='rendimientos-grafico'),

    html.Div([
        dash_table.DataTable(
            id='tabla-top-20',
        columns=[
                {'name': 'Nombre', 'id': 'Nombre'},
                {'name': 'Sociedad_Gerente', 'id': 'SG'},
                {'name': 'VarCt-15', 'id': 'VarCt-15'},
                {'name': 'Categoria', 'id': 'Categoria'}
            ],
        style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
        )    
    ])

], style={'padding': '20px'})

def obtener_top_20_quincenal(df, categoria):
    df_filtrado = df[df['Categoria'] == categoria]
    df_filtrado = df_filtrado[['Nombre', 'SG', 'VarCt-15', 'Categoria']]
    df_filtrado = df_filtrado.sort_values(by='VarCt-15', ascending=False)
    # Filtrar para que no se repita la sociedad gerente
    df_filtrado = df_filtrado.drop_duplicates(subset=['SG'])
    # Seleccionar los top 20
    top_20_quincenal = df_filtrado.head(20)
    return top_20_quincenal

@app.callback(
    Output('tabla-top-20', 'data'),
    [Input('categoria-dropdown', 'value')]
)
def update_top20_table(categoria):
    if not categoria:
        return []
    top20 = obtener_top_20_quincenal(df, categoria)
    return top20.to_dict('records')

@app.callback(
    Output('rendimientos-grafico', 'figure'),
    [Input('fondo-dropdown', 'value')]
)
def update_graph(selected_fondo):
    fig = make_subplots(rows=1, cols=4, subplot_titles=(
        'Rendimiento Diario', 'Rendimiento Quincenal', 'Rendimiento 100 Días', 'Rendimiento Anual'))

    if not selected_fondo:
        # Si no hay fondo seleccionado, graficar todos los datos
        rendimiento_promediodiario = df.groupby('Categoria')['Var%'].mean().reset_index()
        rendimiento_promedio15 = df.groupby('Categoria')['VarCt-15'].mean().reset_index()
        rendimiento_promedio100 = df.groupby('Categoria')['VarCt-104'].mean().reset_index()
        rendimiento_promedioanual = df.groupby('Categoria')['VarCanual'].mean().reset_index()

        # Agregar barras para cada tipo de rendimiento en los cuadrantes correspondientes
        fig.add_trace(go.Bar(x=rendimiento_promediodiario['Var%'], y=rendimiento_promediodiario['Categoria'], 
                             orientation='h', marker=dict(color='skyblue'), name='Rendimiento Diario'), row=1, col=1)
        fig.add_trace(go.Bar(x=rendimiento_promedio15['VarCt-15'], y=rendimiento_promedio15['Categoria'], 
                             orientation='h', marker=dict(color='salmon'), name='Rendimiento Quincenal'), row=1, col=2)
        fig.add_trace(go.Bar(x=rendimiento_promedio100['VarCt-104'], y=rendimiento_promedio100['Categoria'], 
                             orientation='h', marker=dict(color='lightgreen'), name='Rendimiento 100 Días'), row=1, col=3)
        fig.add_trace(go.Bar(x=rendimiento_promedioanual['VarCanual'], y=rendimiento_promedioanual['Categoria'], 
                             orientation='h', marker=dict(color='gray'), name='Rendimiento Anual'), row=1, col=4)
    else:
        # Si se selecciona un fondo, filtrar los datos y graficarlos
        df_fondo = df[df['Nombre'] == selected_fondo]
        rendimiento_promediodiario = df_fondo.groupby('Categoria')['Var%'].mean().reset_index()
        rendimiento_promedio15 = df_fondo.groupby('Categoria')['VarCt-15'].mean().reset_index()
        rendimiento_promedio100 = df_fondo.groupby('Categoria')['VarCt-104'].mean().reset_index()
        rendimiento_promedioanual = df_fondo.groupby('Categoria')['VarCanual'].mean().reset_index()

        # Agregar barras para cada tipo de rendimiento en los cuadrantes correspondientes
        fig.add_trace(go.Bar(x=rendimiento_promediodiario['Var%'], y=rendimiento_promediodiario['Categoria'], 
                             orientation='h', marker=dict(color='lightblue'), name='Rendimiento Diario'), row=1, col=1)
        fig.add_trace(go.Bar(x=rendimiento_promedio15['VarCt-15'], y=rendimiento_promedio15['Categoria'], 
                             orientation='h', marker=dict(color='lightcoral'), name='Rendimiento Quincenal'), row=1, col=2)
        fig.add_trace(go.Bar(x=rendimiento_promedio100['VarCt-104'], y=rendimiento_promedio100['Categoria'], 
                             orientation='h', marker=dict(color='lightgreen'), name='Rendimiento 100 Días'), row=1, col=3)
        fig.add_trace(go.Bar(x=rendimiento_promedioanual['VarCanual'], y=rendimiento_promedioanual['Categoria'], 
                             orientation='h', marker=dict(color='gray'), name='Rendimiento Anual'), row=1, col=4)

    fig.update_layout(height=600, width=1200, showlegend=False)
    # Ocultar las etiquetas del eje y en todos los gráficos
    for col in range(2, 5):
         fig.update_yaxes(showticklabels=False, row=1, col=col)

    return fig
if __name__ == '__main__':
    app.run_server(debug=True)