import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px


df = pd.read_csv('us-counties.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("US Counties COVID-19 Data"),
    dcc.Dropdown(
        id='state-option',
        options=[{'label': state, 'value': state} for state in sorted(df['state'].unique())],
        multi=True,
        placeholder="Select State"
    ),
    dcc.Dropdown(
        id='county-option',
        multi=True,
        placeholder="Select County"
    ),
    dcc.Dropdown(
        id='date-option',
        options=[{'label': date, 'value': date} for date in df['date'].unique()],
        multi=True,
        placeholder="Select Date"
    ),
    dcc.Graph(id='bar-chart')
])

@app.callback(
    Output('county-option', 'options'),
    Input('state-option', 'value')
)
def update_county_options(selected_states):
    if not selected_states:
        return []
    county_options = [{'label': county, 'value': county} for county in sorted(df[df['state'].isin(selected_states)]['county'].unique())]
    return county_options

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('state-option', 'value'),
     Input('county-option', 'value'),
     Input('date-option', 'value')]
)
def update_bar_chart(selected_states, selected_counties, selected_dates):
    if not (selected_states and selected_counties and selected_dates):
        return dash.no_update

    filtered_df = df.copy()

    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    if selected_counties:
        filtered_df = filtered_df[filtered_df['county'].isin(selected_counties)]
    if selected_dates:
        filtered_df = filtered_df[filtered_df['date'].isin(selected_dates)]

    grouped_data = filtered_df.groupby(['state', 'county', 'date'])[['cases', 'deaths']].sum().reset_index()

    fig = px.bar(
        data_frame=grouped_data.melt(id_vars=['state', 'county', 'date'], var_name='Type', value_name='Count'),
        x='county',
        y='Count',
        color='Type',
        barmode='group',
        labels={'Count': 'Values', 'county': 'Counties'},
        title="COVID-19 Cases and Deaths",
        width=400
    )

    return fig

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8050, debug=False)
