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


class Smoother(SmootherBase):
    """
    Base for smoother classes. Inherits from `smoother.Smoother`.

    Parameters
    ----------
    name : str
        The smoother's name is the `id` of its hidden state `div`, the 
        default label for plots it generates, and the default column name for 
        tables to which it belongs.

    \*args, \*\*kwargs : 
        Arguments and keyword arguments are passed to the smoother 
        constructor.
    """
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def dump(self):
        """
        Returns
        -------
        state dictionary : str (JSON)
        """
        return json.dumps({
            'name': self.name,
            'x': list(self.x),
            '_f_x': list(self._f_x)
        })

    def load(state_dict):
        """
        Parameters
        ----------
        state_dict : str (JSON)
            Smoother state dictionary (output of `Smoother.dump`).

        Returns
        -------
        smoother : dash_fcast.Smoother
            Smoother specified by the state dictionary.
        """
        state_dict = json.loads(state_dict)
        smoother = Smoother(state_dict['name'], state_dict['decimals'])
        smoother.x = np.array(state_dict['x'])
        smoother._f_x = np.array(state_dict['_f_x'])
        return smoother

    def pdf_plot(self, **kwargs):
        """
        Parameters
        ----------
        \*\*kwargs : 
            Keyword arguments passed to `go.Scatter`.

        Returns
        -------
        scatter : go.Scatter
            Scatter plot of the probability density function.
        """
        name = kwargs.get('name', self.name)
        return go.Scatter(x=self.x, y=self.f_x, name=name, **kwargs)

    def cdf_plot(self, **kwargs):
        """
        Parameters
        ----------
        \*\* kwargs :
            Keyword arguments passed to `go.Scatter`.

        Returns
        -------
        scatter : go.Scatter
            Scatter plot of the cumulative distribution function.
        """
        name = kwargs.get('name', self.name)
        return go.Scatter(x=self.x, y=self.F_x, name=name, **kwargs)


class MassSmoother(Smoother):
    pass
#     """
#     with series
#     editable quantiles and bins tables?
#     """
#     def __init__(self, name, data=None, decimals=2):
#         super().__init__(name, decimals)

#     def fit(self, data):
#         lb, ub, constraints = None, None, []
#         for d in data:
#             if lb is None or d[0] < lb:
#                 lb = d[0]
#             if ub is None or d[1] > ub:
#                 ub = d[1]
#             constraints.append(MassConstraint(d[0], d[1], d[2]/100.))
#         return super().fit(lb, ub, constraints, DerivativeObjective(2))

#     def elicitation(self, app, bins=None):
#         bins = bins or DEFAULT_BINS

#         layout = [
#             html.Div(id=self.name, style={'display': 'none'}),
#             dash_table.DataTable(
#                 id=self.name+'-table',
#                 columns=[
#                     {'id': 'Bin min', 'name': 'Bin min'},
#                     {'id': 'Bin max', 'name': 'Bin max'},
#                     {'id': self.name, 'name': self.name}
#                 ],
#                 data=[
#                     {'Bin min': bin[0], 'Bin max': bin[1], self.name: bin[2]}
#                     for bin in bins
#                 ],
#                 style_as_list_view=True,
#                 style_header={
#                     'backgroundColor': 'white',
#                     'fontWeight': 'bold'
#                 },
#                 editable=True
#             ),
#             dbc.FormText(id=self.name+'-total')
#         ]

#         @app.callback(
#             Output(self.name+'-total', 'children'),
#             [Input(self.name+'-table', 'data')]
#         )
#         def update_total_fcast(records):
#             total = sum([float(r[self.name]) for r in records])
#             return 'Total: {}'.format(total)

#         @app.callback(
#             Output(self.name, 'children'),
#             [Input(self.name+'-table', 'data_timestamp')],
#             [State(self.name+'-table', 'data')]
#         )
#         def update_forecast(_, records):
#             data = [
#                 (
#                     float(r['Bin min']), 
#                     float(r['Bin max']), 
#                     float(r[self.name])
#                 )
#                 for r in records
#             ]
#             return BinSmoother(self.name).fit(data).dump()

#         return layout


class MomentSmoother(Smoother):
    """
    Smoother with bounds and moments constraints. The moments constraints are 
    mean and standard deviation.
    """
    def fit(self, lb, ub, mean, std=None):
        """
        Fit the smoother given bounds and moments constraints.

        Parameters
        ----------
        lb : float
            Lower bound of the distribution.

        ub : float
            Upper bound of the distribution.

        mean : float
            Mean of the distribution.

        std : float or None, default=None
            Standard deviation of the distribution. If `None`, the standard 
            deviation constraint is omitted.

        Returns
        -------
        self : dash_fcast.MomentSmoother
        """
        constraints = [MomentConstraint(mean, degree=1)]
        if std is not None:
            constraints.append(
                MomentConstraint(std, degree=2, type_='central', norm=True)
            )
        return super().fit(lb, ub, constraints)

    def elicitation(self, app, lb=-3, ub=3, mean=0, std=1, decimals=2):
        """
        Creates the layout for eliciting bounds and moments.

        Parameters
        ----------
        app : dash.Dash
            Application with which the elicitation is associated.

        lb : float, default=-3
            Default lower bound.

        ub : float, default=3
            Default upper bound.

        mean : float, default=0
            Default mean.

        std : float, default=1
            Default standard deviation.

        decimals : int, default=2
            Number of decimals to which the recommended maximum standard 
            deviation is rounded.

        Returns
        -------
        layout : list of dash elements.
            Elicitation layout.
        """
        layout = [
            html.Div(id=self.name, style={'display': 'none'}),
            dbc.FormGroup([
                dbc.Label('Lower bound', html_for=self.name+'-lb'),
                dbc.Input(id=self.name+'-lb', value=lb, type='number')
            ]),
            dbc.FormGroup([
                dbc.Label('Upper bound', html_for=self.name+'-ub'),
                dbc.Input(id=self.name+'-ub', value=ub, type='number')
            ]),
            dbc.FormGroup([
                dbc.Label('Mean', html_for=self.name+'-mean'),
                dbc.Input(id=self.name+'-mean', value=mean, type='number')
            ]),
            dbc.FormGroup([
                dbc.Label('Standard deviation', html_for=self.name+'-std'),
                dbc.Input(id=self.name+'-std', value=std, type='number'),
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
                    round(smoother.std(), decimals)
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
        def update_forecast(_, lb, ub, mean, std):
            return MomentSmoother(self.name).fit(lb, ub, mean, std).dump()

        return layout