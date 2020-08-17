# TODO column layouts

import dash_fcast as fcast

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

ACTUAL_COLOR, FCAST_COLOR = px.colors.qualitative.D3[0:2]

# series = fcast.Series('Data', pd.read_csv('base_data.csv')['x'])
# series_pdf = series.pdf_plot(line={'color': DATA_COLOR})
# series_cdf = series.cdf_plot(line={'color': DATA_COLOR})

smoother_actual = fcast.MomentSmoother('Actual')
smoother_cf = fcast.MomentSmoother('Forecast')
table = fcast.Table('Table', objects=[smoother_actual, smoother_cf])

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
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Actual distribution'),
                    dbc.CardBody(smoother_actual.elicitation(app))
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Counterfactual forecast'),
                    dbc.CardBody(smoother_cf.elicitation(app))
                ])
            ])
        ]),
        # smoother_actual.state_div(app, table),
        # smoother_cf.state_div(app, table),
        html.Br(),
        html.Div(id='graphs'),
        *table.render(app),
        html.Br()
    ], className='container')

    @app.callback(
        Output('graphs', 'children'),
        [
            Input('Actual', 'children'),
            Input('Forecast', 'children'), 
            Input('Table', 'children')
        ]
    )
    def update_graphs(smoother_actual_state, smoother_cf_state, table_state):
        smoother_actual = fcast.Smoother.load(smoother_actual_state)
        smoother_cf = fcast.Smoother.load(smoother_cf_state)
        table = fcast.Table.load(table_state)

        pdf = go.Figure([
            smoother_actual.pdf_plot(line={'color': ACTUAL_COLOR}),
            smoother_cf.pdf_plot(line={'color': FCAST_COLOR}),
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
            barmode='overlay'
        )

        cdf = go.Figure([
            smoother_actual.cdf_plot(line={'color': ACTUAL_COLOR}),
            smoother_cf.cdf_plot(line={'color': FCAST_COLOR})
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