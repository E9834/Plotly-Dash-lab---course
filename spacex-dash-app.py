import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# ===== DATA =====
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# Opzioni dropdown
sites = sorted(spacex_df['Launch Site'].unique().tolist())
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sites
]

# ===== APP =====
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True,
        style={'width': '50%'}
    ),
    html.Br(),

    # TASK 2: Pie chart (un SOLO Graph con questo id)
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: RangeSlider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,
        value=[min_payload, max_payload],
        marks={min_payload: str(min_payload), max_payload: str(max_payload)}
    ),
    html.Br(),

    # TASK 4: Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ===== CALLBACKS =====

# Pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        d = spacex_df[spacex_df['class'] == 1]
        by_site = d.groupby('Launch Site', as_index=False)['class'].count()
        fig = px.pie(by_site, values='class', names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        d = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = d['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Success vs Failure for {selected_site}')
    return fig

# Scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    m = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    d = spacex_df[m]
    if selected_site != 'ALL':
        d = d[d['Launch Site'] == selected_site]

    fig = px.scatter(
        d,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Correlation between Payload and Success for All Sites'
               if selected_site == 'ALL'
               else f'Correlation between Payload and Success for {selected_site}')
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

    


