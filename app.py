# TODO

# WED

# table bar graph

# THU

# editable number of rows

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
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Actual distribution'),
                    dbc.CardBody(fcast.Smoother(app, id='Actual'))
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Counterfactual forecast'),
                    dbc.CardBody(fcast.Smoother(app, id='Forecast'))
                ])
            ])
        ]),
        html.Br(),
        html.Div(id='graphs'),
        dbc.Card([
            dbc.CardHeader('Table', style={'text-align': 'center'}),
            dbc.CardBody(
                # fcast.Table(
                #     app, 
                #     id='Table', 
                #     bins=[(-3, -1.5), (-1.5, 0), (0, 1.5), (1.5, 3)],
                #     datatable={'row_deletable': True, 'editable': True},
                #     # row_addable=True
                # )
            )
        ]),
        html.Br()
    ], className='container')

    fcast.smoother.register_smoother_callbacks(app)

    @app.callback(
        Output('graphs', 'children'),
        [Input({'type': 'smoother', 'name': ALL}, 'children')]
    )
    def update_graphs(smoother_states):
        smoothers = [fcast.Smoother.load(state) for state in smoother_states]
        # table = fcast.Table.load(table_state)

        pdf = go.Figure(
            [smoother.pdf_plot() for smoother in smoothers]
            # + [table.bar_plot()]
        )
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

        cdf = go.Figure([smoother.cdf_plot() for smoother in smoothers])
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