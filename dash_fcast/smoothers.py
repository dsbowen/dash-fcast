"""# Smoothers"""

from .utils import get_changed_cells

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
    
    def quantile(self, q):
        return self.ppf(q)

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

    @classmethod
    def load(cls, state_dict):
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
        smoother = cls(state_dict['name'])
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
    """
    Smoother with masses constraints.
    """
    def fit(self, quantiles, values, derivative=2):
        """
        Fit the smoother given masses constraints.

        Parameters
        ----------
        quantiles : list of float or numpy.array
            Ordered list of quantiles.

        values : list of float or numpy.array
            Ordered list of values corresponding to `quantiles`.

        derivative : int, default=2
            Deriviate of the derivative smoothing function to maximize. e.g. 
            `2` means the smoother will minimize the mean squaure second 
            derivitive.
        """
        params = zip(values[:-1], values[1:], np.diff(quantiles))
        return super().fit(
            values[0], 
            values[-1],
            [MassConstraint(lb, ub, mass) for lb, ub, mass in params], DerivativeObjective(derivative)
        )

    def state_div(self, app, table):
        layout = html.Div(
            self.dump(), id=self.name, style={'display': 'none'}
        )

        @app.callback(
            Output(self.name, 'children'),
            [Input(table.name, 'children')],
            [
                State(table.name+'-table', 'data'), 
                State(table.name+'-table', 'data_previous'),
                State(self.name, 'children')
            ]
        )
        def update_smoother_state(
            table_state, data, data_previous, smoother_state
        ):
            if not smoother_state or not data_previous:
                return self.dump()
            changed_cells = get_changed_cells(data, data_previous)
            changed_cols = [cell[1] for cell in changed_cells]
            if self.name not in changed_cols:
                return smoother_state
            smoother = MassSmoother.load(smoother_state)
            table_state = json.loads(table_state)
            try:
                smoother.fit(
                    table_state['iv'], table_state['_data'][self.name]
                )
            except:
                pass
            return smoother.dump()

        return layout


class MomentSmoother(Smoother):
    """
    Smoother with bounds and moments constraints. The moments constraints are 
    mean and standard deviation.
    """
    def __init__(self, name, lb=0, ub=1, mean=.5, std=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.fit(lb, ub, mean, std)

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

    def elicitation(self, app, lb=0, ub=1, mean=.5, std=None, decimals=2):
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
            html.Div(self.dump(), id=self.name, style={'display': 'none'}),
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
                'Update', id=self.name+'-update', color='primary'
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