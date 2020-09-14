"""# Moments distribution

This elicitation method asks forecasters to input the 'bounds and moments' of
the distribution. (Specifically, the moments are the mean and standard 
deviation). It then fits a distribution based on these inputs:

1. Lower bound and upper bound => uniform
2. Lower bound and mean or standard deviation => exponential
3. Upper bound and mean or standard deviation => 'reflected' exponential
4. Mean and standard deviation => Gaussian
5. Lower bound, mean, and standard deviation => gamma
6. Upper bound, mean, and standard deviation => 'reflected' gamma
7. Lower bound, upper bound, mean, and standard deviation => non-parametric 
maximum entropy distribution

Examples
--------
In `app.py`:

```python
import dash_fcast as fcast
import dash_fcast.distributions as dist

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
\    html.Br(),
\    dist.Moments(id='Forecast'),
\    html.Br(),
\    fcast.Table(
\        id='Table', 
\        datatable={'editable': True, 'row_deletable': True},
\        row_addable=True
\    ),
\    html.Div(id='graphs')
], className='container')

dist.Moments.register_callbacks(app)
fcast.Table.register_callbacks(app)

@app.callback(
\    Output('graphs', 'children'),
\    [
\        Input(dist.Moments.get_id('Forecast'), 'children'),
\        Input(fcast.Table.get_id('Table'), 'children')
\    ]
)
def update_graphs(dist_state, table_state):
\    distribution = dist.Moments.load(dist_state)
\    table = fcast.Table.load(table_state)
\    pdf = go.Figure([distribution.pdf_plot(), table.bar_plot('Forecast')])
\    pdf.update_layout(transition_duration=500, title='PDF')
\    cdf = go.Figure([distribution.cdf_plot()])
\    cdf.update_layout(transition_duration=500, title='CDF')
\    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
\    app.run_server(debug=True)
```

Run the app with:

```bash
$ python app.py
```

Open your browser and navigate to <http://localhost:8050/>.
"""

from .utils import rexpon, rgamma

import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import MATCH, Input, Output, State
from scipy.stats import expon, gamma, norm, uniform
from smoother import Smoother, MomentConstraint

import json


class Moments():
    """
    Distribution generated from moments elicitation. Inherits from 
    `smoother.Smoother`. See <https://dsbowen.github.io/smoother/>.

    Parameters
    ----------
    id : str
        Distribution identifier.

    lb : scalar, default=0
        Lower bound of the distribution. *F(x)=0* for all *x<lb*.

    ub : scalar, default=1
        Upper bound of the distribution. *F(x)=1* for all *x>ub*.

    mean : scalar or None, default=None
        Mean of the distribution. If `None`, the mean is inferred as halfway
        between the lower and upper bound.

    std : scalar or None, default=None
        Standard deviation of the distribution. If `None`, the standard 
        deviation is inferred as the standard deviation which maximizes
        entropy.

    \*args, \*\*kwargs : 
        Arguments and keyword arguments are passed to the smoother 
        constructor.

    Attributes
    ----------
    id : str
        Set from the `id` parameter.
    """
    def __init__(self, id, lb=0, ub=1, mean=None, std=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self._dist, self._dist_type = None, None
        self._fit_args = lb, ub, mean, std

    @staticmethod
    def get_id(id, type='state'):
        """
        Parameters
        ----------
        id : str

        type : str, default='state'
            Type of object associated with the moments distribution.

        Returns
        -------
        id dictionary : dict
            Dictionary identifier.
        """
        return {'dist-cls': 'moments', 'dist-id': id, 'type': type}

    def to_plotly_json(self):
        return {
                'props': {'children': self.elicitation(*self._fit_args)
            },
            'type': 'Div',
            'namespace': 'dash_html_components'
        }

    def elicitation(self, lb=0, ub=1, mean=None, std=None):
        """
        Creates the layout for eliciting bounds and moments. Parameters for 
        this method are analogous to the constructor parameters.

        Parameters
        ----------
        lb : scalar, default=0

        ub : scalar, default=1

        mean : scalar or None, default=None

        std : scalar or None, default=None

        decimals : int, default=2
            Number of decimals to which the recommended maximum standard 
            deviation is rounded.

        Returns
        -------
        layout : list of dash elements.
            Elicitation layout.
        """
        def gen_formgroup(label, type, value):
            id = Moments.get_id(self.id, type)
            formgroup = dbc.FormGroup([
                dbc.Label(label, html_for=id, width=6),
                dbc.Col([
                    dbc.Input(
                        id=id, 
                        value=value, 
                        type='number', 
                        style={'text-align': 'right'}
                    ),
                ], width=6)
            ], row=True)
            return formgroup

        return [
            # hidden state div
            html.Div(
                self.dump(), 
                id=Moments.get_id(self.id, 'state'), 
                style={'display': 'none'}
            ),
            gen_formgroup('Lower bound', 'lb', lb),
            gen_formgroup('Upper bound', 'ub', ub),
            gen_formgroup('Mean', 'mean', mean),
            gen_formgroup('Standard deviation', 'std', std),
            dbc.Button(
                'Update', 
                id=Moments.get_id(self.id, 'update'), 
                color='primary'
            )
        ]

    @staticmethod
    def register_callbacks(app, decimals=2):
        """
        Register dash callbacks for moments distributions.

        Parameters
        ----------
        app : dash.Dash
            App with which to register callbacks.

        decimals : int, default=2
            Number of decimals to which to round the standard deviation
            placeholder.
        """
        @app.callback(
            Output(Moments.get_id(MATCH, 'mean'), 'placeholder'),
            [
                Input(Moments.get_id(MATCH, type), 'value') 
                for type in ('lb', 'ub', 'std')
            ]
        )
        def update_mean_placeholder(lb, ub, std):
            dist_type = Moments._get_dist_type(lb, ub, std=std)
            if dist_type is None:
                return None
            if dist_type in ('uniform', 'max-entropy'):
                mean = (lb + ub)/2.
            elif dist_type == 'expon':
                mean = lb + std
            elif dist_type == 'rexpon':
                mean = ub - std
            return round(mean, decimals)

        @app.callback(
            Output(Moments.get_id(MATCH, 'std'), 'placeholder'),
            [
                Input(Moments.get_id(MATCH, type), 'value') 
                for type in ('lb', 'ub', 'mean')
            ]
        )
        def update_std_placeholder(lb, ub, mean):
            dist_type = Moments._get_dist_type(lb, ub, mean)
            if dist_type is None:
                return
            if dist_type == 'uniform':
                std = (1/12. * (ub-lb)**2)**.5
            elif dist_type == 'expon':
                std = mean - lb
            elif dist_type == 'rexpon':
                std = ub - mean
            elif dist_type == 'max-entropy':
                std = Moments('tmp').fit(lb, ub, mean).std()
            return round(std, decimals)

        @app.callback(
            Output(Moments.get_id(MATCH, 'state'), 'children'),
            [Input(Moments.get_id(MATCH, 'update'), 'n_clicks')],
            [
                State(Moments.get_id(MATCH, 'state'), 'id'),
                State(Moments.get_id(MATCH, 'state'), 'children'),
                State(Moments.get_id(MATCH, 'lb'), 'value'),
                State(Moments.get_id(MATCH, 'ub'), 'value'),
                State(Moments.get_id(MATCH, 'mean'), 'value'),
                State(Moments.get_id(MATCH, 'std'), 'value')
            ]
        )
        def update_forecast(_, id, children, lb, ub, mean, std):
            try:
                return Moments(id['dist-id']).fit(lb, ub, mean, std).dump()
            except:
                return children

    def fit(self, lb=None, ub=None, mean=None, std=None):
        """
        Fit the smoother given bounds and moments constraints. Parameters are
        analogous to those of the constructor.

        Parameters
        ----------
        lb : scalar or None, default=None

        ub : scalar or None, default=None

        mean : scalar or None, default=None

        std : scalar or None, default=None

        Returns
        -------
        self : dash_fcast.distributions.Moments
        """
        dist_type = self._get_dist_type(lb, ub, mean, std)
        self._dist_type = dist_type
        self._fit_args = lb, ub, mean, std
        if dist_type == 'uniform':
            self._dist = uniform(lb, ub)
        elif dist_type == 'expon':
            self._dist = expon(lb, mean-lb if std is None else std)
        elif dist_type == 'rexpon':
            self._dist = rexpon(ub, ub-mean if std is None else std)
        elif dist_type == 'norm':
            self._dist = norm(mean, std)
        # elif dist_type == 'gamma':
        #     self._dist = gamma(((mean-lb) / std)**2, lb, std**2)
        # elif dist_type == 'rgamma':
        #     self._dist = rgamma(((ub-mean) / std)**2, ub, std**2)
        elif dist_type == 'max-entropy':
            lb = mean - 3*std if lb is None else lb
            ub = mean + 3*std if ub is None else ub
            mean = (lb + ub)/2. if mean is None else mean
            constraints = [MomentConstraint(mean, degree=1)]
            if std is not None:
                constraints.append(MomentConstraint(
                    std, degree=2, type_='central', norm=True
                )) 
            self._dist = Smoother().fit(lb, ub, constraints=constraints)
        return self

    @staticmethod
    def _get_dist_type(lb=None, ub=None, mean=None, std=None):
        None_count = [lb, ub, mean, std].count(None)
        if None_count >= 3:
            return
        if None_count == 2:
            if mean is None and std is None:
                return 'uniform'
            if lb is not None and ub is None:
                # exponential
                return 'expon'
            if lb is None and ub is not None:
                # reflected exponential
                return 'rexpon'
            if lb is None and ub is None:
                # normal
                return 'norm'
        if None_count == 1:
            if ub is None:
                return 'max-entropy'
                # return 'gamma'
            if lb is None:
                return 'max-entropy'
                # return 'rgamma'
        # non-parametric maximum entropy distribution
        # approximated by smoother
        return 'max-entropy'

    def dump(self):
        """
        Returns
        -------
        state dictionary : str (JSON)
        """
        state = {
            'cls': 'moments',
            'id': self.id,
            '_dist_type': self._dist_type,
            '_fit_args': self._fit_args
        }
        if self._dist_type == 'max-entropy':
            state.update({
                'x': list(self._dist.x), '_f_x': list(self._dist._f_x)
            })
        return json.dumps(state)

    @classmethod
    def load(cls, state_dict):
        """
        Parameters
        ----------
        state_dict : str (JSON)
            Moments distribution state dictionary (output of `Moments.dump`).

        Returns
        -------
        distribution : dash_fcast.distributions.Moments
            Moments distribution specified by the state dictionary.
        """
        state_dict = json.loads(state_dict)
        dist = cls(id=state_dict['id'])
        dist._dist_type = state_dict['_dist_type']
        if dist._dist_type == 'max-entropy':
            dist._fit_args = state_dict['_fit_args']
            dist._dist = Smoother()
            dist._dist.x = np.array(state_dict['x'])
            dist._dist._f_x = np.array(state_dict['_f_x'])
        else:
            dist.fit(*state_dict['_fit_args'])
        return dist

    def mean(self):
        return self._dist.mean()

    def std(self):
        return self._dist.std()

    def pdf(self, x):
        return self._dist.pdf(x)

    def cdf(self, x):
        return self._dist.cdf(x)

    def ppf(self, q):
        return self._dist.ppf(q)

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
        name = kwargs.pop('name', self.id)
        if self._dist_type != 'max-entropy':
            lb, ub = self._dist.ppf(0), self._dist.ppf(1)
            lb = self._dist.ppf(.01) if lb == -np.inf else lb
            ub = self._dist.ppf(.99) if ub == np.inf else ub
            x = np.linspace(lb, ub)
            y = self._dist.pdf(x)
        elif self._dist_type == 'max-entropy':
            x, y = self._dist.x, self._dist.f_x
        return go.Scatter(x=x, y=y, name=name, **kwargs)

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
        name = kwargs.pop('name', self.id)
        if self._dist_type != 'max-entropy':
            lb, ub = self._dist.ppf(0), self._dist.ppf(1)
            lb = self._dist.ppf(.01) if lb == -np.inf else lb
            ub = self._dist.ppf(.99) if ub == np.inf else ub
            x = np.linspace(lb, ub)
            y = self._dist.cdf(x)
        else:
            x, y = self._dist.x, self._dist.F_x
        return go.Scatter(x=x, y=y, name=name, **kwargs)