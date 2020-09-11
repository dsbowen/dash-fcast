import dash_fcast as fcast
import dash_fcast.distributions as dist

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Br(),
    dist.Moments(id='Forecast'),
    html.Br(),
    fcast.Table(
        id='Table', 
        datatable={'editable': True, 'row_deletable': True},
        row_addable=True
    ),
    html.Div(id='graphs')
], className='container')

dist.Moments.register_callbacks(app)
fcast.Table.register_callbacks(app)

@app.callback(
    Output('graphs', 'children'),
    [
        Input(dist.Moments.get_id('Forecast'), 'children'),
        Input(fcast.Table.get_id('Table'), 'children')
    ]
)
def update_graphs(dist_state, table_state):
    distribution = dist.Moments.load(dist_state)
    table = fcast.Table.load(table_state)
    pdf = go.Figure([distribution.pdf_plot(), table.bar_plot('Forecast')])
    pdf.update_layout(transition_duration=500, title='PDF')
    cdf = go.Figure([distribution.cdf_plot()])
    cdf.update_layout(transition_duration=500, title='CDF')
    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
    app.run_server(debug=True)