# TODO

# THU

# clean and comment
# make app

# FRI

# table with IV as percentiles not bins

# SAT-SUN

# tabular elicitation

import dash_fcast as fcast

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
                        fcast.Smoother(id='Actual'),
                        html.Br()
                    ])
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Counterfactual forecast'),
                    dbc.CardBody([
                        fcast.Smoother(id='Forecast'),
                        html.Br()
                    ])
                ])
            ])
        ]),
        html.Br(),
        html.Div(id='graphs'),
        dbc.Card([
            dbc.CardHeader('Adjust the bin start and end as specified by the CFP'),
            dbc.CardBody(
                fcast.Table(
                    id='Table', 
                    bins=[(0, .25), (.25, .5), (.5, .75), (.75, 1)],
                    datatable={'row_deletable': True, 'editable': True},
                    row_addable=True
                )
            )
        ]),
        html.Br()
    ], className='container')

    fcast.smoother.register_smoother_callbacks(app)
    fcast.table.register_table_callbacks(app)

    @app.callback(
        Output('graphs', 'children'),
        [
            Input(
                {'type': 'smoother-state', 'smoother-id': 'Actual'}, 
                'children'
            ),
            Input(
                {'type': 'smoother-state', 'smoother-id': 'Forecast'},
                'children'
            ),
            Input(
                {'type': 'table-state', 'table-id': 'Table'}, 
                'children'
            )
        ]
    )
    def update_graphs(actual_state, fcast_state, table_state):
        actual_smoother = fcast.Smoother.load(actual_state)
        fcast_smoother = fcast.Smoother.load(fcast_state)
        table = fcast.Table.load(table_state)

        pdf = go.Figure([
            actual_smoother.pdf_plot(line={'color': ACTUAL_COLOR}),
            fcast_smoother.pdf_plot(line={'color': FCAST_COLOR}),
            table.bar_plot('Actual', opacity=.4, marker_color=ACTUAL_COLOR),
            table.bar_plot('Forecast', opacity=.4, marker_color=FCAST_COLOR)
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
            actual_smoother.cdf_plot(line={'color': ACTUAL_COLOR}),
            fcast_smoother.cdf_plot(line={'color': FCAST_COLOR})
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
        return dbc.Row([
            dbc.Col([dcc.Graph(figure=pdf)]), 
            dbc.Col([dcc.Graph(figure=cdf)])
        ])

    return app

app = create_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)