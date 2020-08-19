"""# Smoothers"""

from .utils import get_changed_cells

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import MATCH, Input, Output, State
from smoother import Smoother as SmootherBase, DerivativeObjective, MassConstraint, MomentConstraint

import json

def register_smoother_callbacks(app, decimals=2):
    @app.callback(
        Output({'type': 'mean', 'index': MATCH}, 'placeholder'),
        [
            Input({'type': type_, 'index': MATCH}, 'value') 
            for type_ in ('lb', 'ub')
        ],
        [State({'type': 'mean', 'index': MATCH}, 'placeholder')]
    )
    def update_mean_placeholder(lb, ub, curr_mean):
        try:
            return round((lb + ub)/2., decimals)
        except:
            return curr_mean



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
    def __init__(self, app=None, id=None, callbacks={}, elicitation={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.elicitation_kwargs = elicitation
        if app is not None:
            self.register_moments_callbacks(app, **callbacks)

    def to_plotly_json(self):
        return {
            'props': {
                'children': self.elicit_moments(**self.elicitation_kwargs)
            },
            'type': 'Div',
            'namespace': 'dash_html_components'
        }

    def elicit_moments(self, lb=0, ub=1, mean=None, std=None):
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

        mean : float or None, default=None
            Default mean.

        std : float or None, default=None
            Default standard deviation.

        decimals : int, default=2
            Number of decimals to which the recommended maximum standard 
            deviation is rounded.

        Returns
        -------
        layout : list of dash elements.
            Elicitation layout.
        """
        def gen_formgroup(label, sfx, value):
            id = self.id + sfx
            formgroup = dbc.FormGroup([
                dbc.Label(label, html_for=id, width=6),
                dbc.Col([
                    dbc.Input(
                        id={'type': sfx, 'index': id}, 
                        value=value, 
                        type='number', 
                        style={'text-align': 'right'}
                    ),
                ], width=6)
            ], row=True)
            return formgroup

        return [
            html.Div(
                self.dump(), 
                id={'type': 'smoother', 'name': self.id}, 
                style={'display': 'none'}
            ),
            gen_formgroup('Lower bound', 'lb', lb),
            gen_formgroup('Upper bound', 'ub', ub),
            gen_formgroup('Mean', 'mean', mean),
            gen_formgroup('Standard deviation', 'std', std),
            dbc.Button('Update', id=self.id+'update', color='primary'),
            html.Br()
        ]

    def register_moments_callbacks(self, app, decimals=2):
        # @app.callback(
        #     Output(self.id+'mean', 'placeholder'),
        #     [Input(self.id+sfx, 'value') for sfx in ('lb', 'ub')],
        #     [State(self.id+'mean', 'placeholder')]
        # )
        # def update_mean_placeholder(lb, ub, curr_mean):
        #     try:
        #         return round((lb + ub)/2., decimals)
        #     except:
        #         return curr_mean

        @app.callback(
            Output(self.id+'std', 'placeholder'),
            [Input(self.id+sfx, 'value') for sfx in ('lb', 'ub', 'mean')],
            [State(self.id+'std', 'placeholder')]
        )
        def update_std_placeholder(lb, ub, mean, curr_placeholder):
            try:
                std = Smoother(id=self.id).fit_moments(lb, ub, mean).std()
                return round(std, decimals)
            except:
                return curr_placeholder

        @app.callback(
            Output({'type': 'smoother', 'name': self.id}, 'children'),
            [Input(self.id+'update', 'n_clicks')],
            [
                State(self.id+sfx, 'value') 
                for sfx in ('lb', 'ub', 'mean', 'std')
            ]
        )
        def update_forecast(_, lb, ub, mean, std):
            return Smoother(id=self.id).fit_moments(lb, ub, mean, std).dump()

        return self

    def fit_moments(self, lb, ub, mean=None, std=None):
        """
        Fit the smoother given bounds and moments constraints.

        Parameters
        ----------
        lb : float
            Lower bound of the distribution.

        ub : float
            Upper bound of the distribution.

        mean : float or None, default=None
            Mean of the distribution. If `None`, the mean constraint is 
            omitted.

        std : float or None, default=None
            Standard deviation of the distribution. If `None`, the standard 
            deviation constraint is omitted.

        Returns
        -------
        self : dash_fcast.MomentSmoother
        """
        mean = (lb + ub)/2. if mean is None else mean
        constraints = [MomentConstraint(mean, degree=1)]
        if std is not None:
            constraints.append(
                MomentConstraint(std, degree=2, type_='central', norm=True)
            )
        return super().fit(lb, ub, constraints)

    def fit_quantiles(self, quantiles, values, derivative=2):
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
            [MassConstraint(lb, ub, mass) for lb, ub, mass in params], 
            DerivativeObjective(derivative)
        )

    def dump(self):
        """
        Returns
        -------
        state dictionary : str (JSON)
        """
        return json.dumps({
            'id': self.id,
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
        smoother = cls(id=state_dict['id'])
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
        name = kwargs.get('name', self.id)
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
        name = kwargs.get('name', self.id)
        return go.Scatter(x=self.x, y=self.F_x, name=name, **kwargs)