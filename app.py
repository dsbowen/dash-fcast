import dash_fcast as fcast

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

# TODO: bins table, mass smoother with quantiles elicitaiton, mass smoother with bins elicitaiton

DATA_COLOR, FCAST_COLOR = px.colors.qualitative.D3[0:2]

series = fcast.Series('Data', pd.read_csv('base_data.csv')['x'])
series_pdf = series.pdf_plot(line={'color': DATA_COLOR})
series_cdf = series.cdf_plot(line={'color': DATA_COLOR})
# smoother = fcast.MomentSmoother('Forecast', series)
smoother = fcast.MomentSmoother('Forecast')
# table = fcast.Quantiles(
#     'Table', (0, .25, .5, .75, 1), data=[smoother] # data=[series, smoother]
# )
table = fcast.Bins(
    'Table', 
    [(-3, -1), (-1, 0), (0, 1), (1, 3)],
    data=[smoother]
)

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
            dbc.Col(smoother.elicitation(app)),
            dbc.Col(table.dash_table(app))
        ]),
        html.Div(id='graphs')
    ], className='container')

    @app.callback(
        Output('graphs', 'children'),
        [Input('Forecast', 'children'), Input('Table', 'data')],
    )
    def update_graphs(state_dict, data):
        smoother = fcast.MomentSmoother.load(state_dict)
        pdf = go.Figure([
            # series_pdf, 
            smoother.pdf_plot(line={'color': FCAST_COLOR}),
            # fcast.Quantiles.bar_plot(
            #     data, 'Data', marker_color=DATA_COLOR, opacity=.4
            # ),
            # fcast.Quantiles.bar_plot(
            #     data, 'Forecast', marker_color=FCAST_COLOR, opacity=.4
            # )
            fcast.Bins.bar_plot(
                data, 'Forecast', marker_color=FCAST_COLOR, opacity=.4
            )
        ])
        pdf.update_layout(
            transition_duration=500, 
            title={
                'text': 'Probability density', 
                'x': .5, 
                'xanchor': 'center'
            }
        )
        cdf = go.Figure([
            # series_cdf,
            smoother.cdf_plot(line={'color': FCAST_COLOR})
        ])
        cdf.update_layout(
            transition_duration=500, 
            title={
                'text': 'Cumulative distribution', 
                'x': .5, 
                'xanchor': 'center'
            }
        )
        return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

    return app

app = create_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)