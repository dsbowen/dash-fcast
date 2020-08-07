"""# Smoothers"""

import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from smoother import Smoother as SmootherBase, MomentConstraint

import json


class Smoother(SmootherBase):
    def dump(self):
        return json.dumps({
            'name': self.name,
            'x': list(self.x),
            '_f_x': list(self._f_x)
        })

    def load(state_dict):
        state_dict = json.loads(state_dict)
        smoother = Smoother()
        smoother.name = state_dict['name']
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


class MomentSmoother(Smoother):
    def __init__(self, name, data=None, decimals=2):
        super().__init__()
        self.name = name
        self.decimals = decimals
        if data is None:
            self.fit(-3, 3, 0, 1)
        else:
            self.fit(
                round(data.min(), decimals), 
                round(data.max(), decimals),
                round(data.mean(), decimals), 
                round(data.std(), decimals)
            )

    def fit(self, lb, ub, mean, std=None):
        constraints = [MomentConstraint(mean, degree=1)]
        if std is not None:
            constraints.append(
                MomentConstraint(std, degree=2, type_='central', norm=True)
            )
        return super().fit(lb, ub, constraints)

    def elicitation(self, app):
        layout = [
            html.Div(id=self.name, style={'display': 'none'}),
            dbc.FormGroup([
                dbc.Label('Lower bound', html_for='lb'),
                dbc.Input(id=self.name+'-lb', value=self.x[0], type='number')
            ]),
            dbc.FormGroup([
                dbc.Label('Upper bound', html_for='ub'),
                dbc.Input(id=self.name+'-ub', value=self.x[-1], type='number')
            ]),
            dbc.FormGroup([
                dbc.Label('Mean', html_for='mean'),
                dbc.Input(
                    id=self.name+'-mean', 
                    value=round(self.mean(), self.decimals), 
                    type='number'
                )
            ]),
            dbc.FormGroup([
                dbc.Label('Standard deviation', html_for='std'),
                dbc.Input(
                    id=self.name+'-std', 
                    value=round(self.std(), self.decimals), 
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
            smoother = (
                self if n_clicks == 0 
                else MomentSmoother(self.name).fit(lb, ub, mean, std)
            )
            return smoother.dump()

        return layout


class MassSmoother(Smoother):
    def __init__(self, data=None):
        pass