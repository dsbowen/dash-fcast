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
    dist.Table(
        id='Forecast',
        datatable={'row_deletable': True},
        row_addable=True,
        scalable=True,
        smoother=True
    ),
    html.Div(id='graphs')
], className='container')

dist.Table.register_callbacks(app)

@app.callback(
    Output('graphs', 'children'),
    [Input(dist.Table.get_id('Forecast'), 'children')]
)
def update_graphs(dist_state):
    distribution = dist.Table.load(dist_state)
    pdf = go.Figure([distribution.pdf_plot(), distribution.bar_plot()])
    pdf.update_layout(transition_duration=500, title='PDF')
    cdf = go.Figure([distribution.cdf_plot()])
    cdf.update_layout(transition_duration=500, title='CDF')
    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
    app.run_server(debug=True)