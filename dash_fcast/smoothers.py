"""# Smoothers"""

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from smoother import Smoother as SmootherBase, DerivativeObjective, MassConstraint, MomentConstraint

import json

DEFAULT_BINS = [
    (-3, -1.5, 6), 
    (-1.5, 0, 44), 
    (0, 1.5, 44), 
    (1.5, 3, 6)
]
DEFAULT_MOMENTS = {'lb': -3, 'ub': 3, 'mean': 0, 'std': 1}


class Smoother(SmootherBase):
    def __init__(self, name, decimals=2):
        super().__init__()
        self.name = name
        self.decimals = decimals

    def dump(self):
        return json.dumps({
            'name': self.name,
            'x': list(self.x),
            '_f_x': list(self._f_x)
        })

    def load(state_dict):
        state_dict = json.loads(state_dict)
        smoother = Smoother(state_dict['name'])
        smoother.x = np.array(state_dict['x'])
        smoother._f_x = np.array(state_dict['_f_x'])
        return smoother

    def quantile(self, q):
        return self.ppf(q)

    def pdf_plot(self, *args, **kwargs):
        return go.Scatter(
            x=self.x, y=self.f_x, name=self.name, *args, **kwargs
        )

    def cdf_plot(self, *args, **kwargs):
        return go.Scatter(
            x=self.x, y=self.F_x, name=self.name, *args, **kwargs
        )


class BinSmoother(Smoother):
    """
    with series
    editable quantiles and bins tables?
    """
    def __init__(self, name, data=None, decimals=2):
        super().__init__(name, decimals)

    def fit(self, data):
        lb, ub, constraints = None, None, []
        for d in data:
            if lb is None or d[0] < lb:
                lb = d[0]
            if ub is None or d[1] > ub:
                ub = d[1]
            constraints.append(MassConstraint(d[0], d[1], d[2]/100.))
        return super().fit(lb, ub, constraints, DerivativeObjective(2))

    def elicitation(self, app, bins=None):
        bins = bins or DEFAULT_BINS

        layout = [
            html.Div(id=self.name, style={'display': 'none'}),
            dash_table.DataTable(
                id=self.name+'-table',
                columns=[
                    {'id': 'Bin min', 'name': 'Bin min'},
                    {'id': 'Bin max', 'name': 'Bin max'},
                    {'id': self.name, 'name': self.name}
                ],
                data=[
                    {'Bin min': bin[0], 'Bin max': bin[1], self.name: bin[2]}
                    for bin in bins
                ],
                style_as_list_view=True,
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                editable=True
            ),
            dbc.FormText(id=self.name+'-total')
        ]

        @app.callback(
            Output(self.name+'-total', 'children'),
            [Input(self.name+'-table', 'data')]
        )
        def update_total_fcast(records):
            total = sum([float(r[self.name]) for r in records])
            return 'Total: {}'.format(total)

        @app.callback(
            Output(self.name, 'children'),
            [Input(self.name+'-table', 'data_timestamp')],
            [State(self.name+'-table', 'data')]
        )
        def update_forecast(_, records):
            data = [
                (
                    float(r['Bin min']), 
                    float(r['Bin max']), 
                    float(r[self.name])
                )
                for r in records
            ]
            return BinSmoother(self.name).fit(data).dump()

        return layout


class MomentSmoother(Smoother):
    def __init__(self, name, decimals=2):
        super().__init__(name, decimals)

    def fit(self, lb, ub, mean, std=None):
        constraints = [MomentConstraint(mean, degree=1)]
        if std is not None:
            constraints.append(
                MomentConstraint(std, degree=2, type_='central', norm=True)
            )
        return super().fit(lb, ub, constraints)

    def elicitation(self, app, series=None):
        params = DEFAULT_MOMENTS if series is None else self.get_params(series)

        layout = [
            html.Div(id=self.name, style={'display': 'none'}),
            dbc.FormGroup([
                dbc.Label('Lower bound', html_for=self.name+'-lb'),
                dbc.Input(
                    id=self.name+'-lb', value=params['lb'], type='number'
                )
            ]),
            dbc.FormGroup([
                dbc.Label('Upper bound', html_for=self.name+'-ub'),
                dbc.Input(
                    id=self.name+'-ub', value=params['ub'], type='number'
                )
            ]),
            dbc.FormGroup([
                dbc.Label('Mean', html_for=self.name+'-mean'),
                dbc.Input(
                    id=self.name+'-mean', 
                    value=round(params['mean'], self.decimals), 
                    type='number'
                )
            ]),
            dbc.FormGroup([
                dbc.Label('Standard deviation', html_for=self.name+'-std'),
                dbc.Input(
                    id=self.name+'-std', 
                    value=round(params['std'], self.decimals), 
                    type='number'
                ),
                dbc.FormText(id=self.name+'-max-std')
            ]),
            dbc.Button(
                'Update distribution', id=self.name+'-update', color='primary'
            ),
            html.Br()
        ]

        @app.callback(
            Output(self.name+'-max-std', 'children'),
            [
                Input(self.name+'-lb', 'value'), 
                Input(self.name+'-ub', 'value'), 
                Input(self.name+'-mean', 'value')
            ],
            [State(self.name+'-max-std', 'children')]
        )
        def update_max_std(lb, ub, mean, children):
            try:
                smoother = MomentSmoother(self.name).fit(lb, ub, mean)
                return 'Suggested maximum: {}'.format(
                    round(smoother.std(), self.decimals)
                )
            except:
                return children

        @app.callback(
            Output(self.name, 'children'),
            [Input(self.name+'-update', 'n_clicks')],
            [
                State(self.name+'-lb', 'value'),
                State(self.name+'-ub', 'value'),
                State(self.name+'-mean', 'value'),
                State(self.name+'-std', 'value')
            ]
        )
        def update_forecast(n_clicks, lb, ub, mean, std):
            return MomentSmoother(self.name).fit(lb, ub, mean, std).dump()

        return layout

    def get_params(self, series=None):
        return {
            'lb': round(series.min(), self.decimals), 
            'ub': round(series.max(), self.decimals), 
            'mean': round(series.mean(), self.decimals), 
            'std': round(series.std(), self.decimals)
        }