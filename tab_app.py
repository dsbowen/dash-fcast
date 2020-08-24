import dash_fcast as fcast
import dash_fcast.distributions as dist

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import ALL, Input, Output, State

ACTUAL_COLOR, FCAST_COLOR = px.colors.qualitative.Plotly[:2]

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
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Actual distribution'),
                    dbc.CardBody([
                        dist.Table(
                            id='Actual',
                            datatable={
                                'editable': True,
                                'style_as_list_view': True,
                                'row_deletable': True
                            },
                            row_addable=True,
                            smoother=True
                        )
                    ])
                ]),
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Counterfactal forecast'),
                    dbc.CardBody([
                        dist.Table(
                            id='Forecast',
                            datatable={
                                'editable': True,
                                'style_as_list_view': True,
                                'row_deletable': True
                            },
                            row_addable=True,
                            smoother=True
                        )
                    ])
                ]),
            ])
        ]),
        html.Div(id='graphs'),
        html.Br()
    ], className='container')

    dist.Table.register_callbacks(app)

    @app.callback(
        Output('graphs', 'children'),
        [
            Input(
                {'dist-cls': 'table', 'dist-id': 'Actual', 'type': 'state'},
                'children'
            ),
            Input(
                {'dist-cls': 'table', 'dist-id': 'Forecast', 'type': 'state'},
                'children'
            )
        ]
    )
    def update_graphs(actual_state, fcast_state):
        actual_dist = dist.Table.load(actual_state)
        fcast_dist = dist.Table.load(fcast_state)

        pdf = go.Figure([
            actual_dist.pdf_plot(line={'color': ACTUAL_COLOR}),
            fcast_dist.pdf_plot(line={'color': FCAST_COLOR}),
            actual_dist.bar_plot(marker_color=ACTUAL_COLOR, opacity=.4),
            fcast_dist.bar_plot(marker_color=FCAST_COLOR, opacity=.4)
        ])
        pdf.update_layout(
            transition_duration=500, 
            title={
                'text': 'Probability density', 
                'x': .5, 
                'xanchor': 'center'
            },
            legend={'orientation': 'h'},
            barmode='overlay',
            yaxis={'rangemode': 'tozero'}
        )

        cdf = go.Figure([
            actual_dist.cdf_plot(line={'color': ACTUAL_COLOR}), 
            fcast_dist.cdf_plot(line={'color': FCAST_COLOR})
        ])
        cdf.update_layout(
            transition_duration=500,
            title={
                'text': 'Cumulative distribution',
                'x': .5,
                'xanchor': 'center'
            },
            legend={'orientation': 'h'},
        )

        return dbc.Row([
            dbc.Col([dcc.Graph(figure=pdf)]),
            dbc.Col([dcc.Graph(figure=cdf)])
        ])

    return app

app = create_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)