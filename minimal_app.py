import dash_fcast as fcast
import dash_fcast.distributions as dist

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dist.Moments(id='my-dist-id'),
    fcast.Table(
        id='my-table-id', 
        datatable={'editable': True, 'row_deletable': True},
        row_addable=True
    ),
    html.Div(id='graphs')
])

dist.Moments.register_callbacks(app)
fcast.Table.register_callbacks(app)

@app.callback(
    Output('graphs', 'children'),
    [
        Input(dist.Moments.get_id('my-dist-id'), 'children'),
        Input(fcast.Table.get_id('my-table-id'), 'children')
    ]
)
def update_graphs(dist_state, table_state):
    distribution = dist.Moments.load(dist_state)
    table = fcast.Table.load(table_state)
    pdf = go.Figure([distribution.pdf_plot(), table.bar_plot('my-dist-id')])
    pdf.update_layout(transition_duration=500)
    cdf = go.Figure([distribution.cdf_plot()])
    cdf.update_layout(transition_duration=500)
    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
    app.run_server(debug=True)