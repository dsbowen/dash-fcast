import dash_fcast as fcast
import dash_fcast.distributions as dist

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import ALL, Input, Output, State

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
        html.Br(),
        dbc.Card([
            dbc.CardHeader('Forecast'),
            dbc.CardBody([
                dist.Table(
                    id='Forecast',
                    datatable={
                        'editable': True,
                        'style_as_list_view': True,
                        'row_deletable': True
                    },
                    row_addable=True
                ),
                html.Br()
            ])
        ]),
        html.Br(),
        html.Div(id='graphs'),
        html.Br()
    ], className='container')

    dist.Table.register_callbacks(app)

    # @app.callback(
    #     Output('graphs', 'children'),
    #     [Input({'type': 'dist-state': 'dist-id': 'Forecast'}, 'children')]
    # )
    # def update_graphs(fcast_state):
    #     fcast_dist = dist.Table.load(fcast_state)

    #     pdf = go.Figure([fcast_dist.pdf_plot()])
    #     pdf.update_layout(
    #         transition_duration=500, 
    #         title={
    #             'text': 'Probability density', 
    #             'x': .5, 
    #             'xanchor': 'center'
    #         },
    #         legend={'orientation': 'h'},
    #         barmode='overlay',
    #         yaxis={'rangemode': 'tozero'}
    #     )

    #     cdf = go.Figure([fcast_dist.cdf_plot()])
    #     cdf.update_layout(
    #         transition_duration=500, 
    #         title={
    #             'text': 'Cumulative distribution', 
    #             'x': .5, 
    #             'xanchor': 'center'
    #         },
    #         legend={'orientation': 'h'}
    #     )

    #     return dbc.Row([
    #         dbc.Col([dcc.Graph(figure=pdf)]), 
    #         dbc.Col([dcc.Graph(figure=cdf)])
    #     ])

    return app

app = create_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)