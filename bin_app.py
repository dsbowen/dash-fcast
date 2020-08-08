import dash_fcast as fcast

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

DATA_COLOR, FCAST_COLOR = px.colors.qualitative.D3[0:2]

smoother = fcast.BinSmoother('Forecast')

def create_app():
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=[{
            "name": "viewport", 
            "content": "width=device-width, initial-scale=1"
        }]
    )

    app.layout = html.Div([
        *smoother.elicitation(app),
        html.Div(id='graphs')
    ], className='container')

    @app.callback(
        Output('graphs', 'children'),
        [Input('Forecast', 'children'), Input('Forecast-table', 'data')]
    )
    def update_graphs(state_dict, records):
        smoother = fcast.BinSmoother.load(state_dict)

        pdf = go.Figure([
            smoother.pdf_plot(line={'color': FCAST_COLOR}),
            fcast.bins_bar_plot(
                records, 'Forecast', marker_color=FCAST_COLOR, opacity=.4
            )
        ])
        pdf.update_layout(
            transition_duration=500, 
            title={
                'text': 'Probability density', 
                'x': .5, 
                'xanchor': 'center'
            },
            legend={'orientation': 'h'},
            barmode='overlay'
        )

        cdf = go.Figure([
            smoother.cdf_plot(line={'color': FCAST_COLOR}),

        ])
        cdf.update_layout(
            transition_duration=500, 
            title={
                'text': 'Cumulative distribution', 
                'x': .5, 
                'xanchor': 'center'
            },
            legend={'orientation': 'h'}
        )

        return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

    return app

app = create_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)