"""# Moments distribution

This elicitation method asks forecasters to input the 'bounds and moments' of
the distribution. (Specifically, the moments are the mean and standard 
deviation). It then fits a distribution based on these inputs:

1. Lower bound and upper bound => uniform
2. Lower bound and mean or standard deviation => exponential
3. Upper bound and mean or standard deviation => 'reflected' exponential
4. Mean and standard deviation => Gaussian
5. Otherwise => non-parametric maximum entropy distribution. See
<https://dsbowen.github.io/smoother/>.

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

from .base import Base
from .utils import rexpon, rgamma

import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import MATCH, Input, Output, State
from scipy.stats import expon, gamma, norm, uniform
from smoother import MaxEntropy

import json


class Moments(Base):
    """
    Distribution generated from moments elicitation.

    Parameters
    ----------
    id : str
        Distribution identifier.

    lb : scalar or None, default=0
        Lower bound of the distribution. *F(x)=0* for all *x<lb*. If `None`,
        the distribution has no lower bound.

    ub : scalar or None, default=1
        Upper bound of the distribution. *F(x)=1* for all *x>ub*. If `None`,
        the distribution has no upper bound.

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
        super().__init__(id, *args, **kwargs)
        self._dist, self._dist_type = None, None
        self._fit_args = lb, ub, mean, std

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
        def gen_formgroup(label, type, value, placeholder=None):
            id = self.get_id(self.id, type)
            return dbc.FormGroup([
                dbc.Label(label, html_for=id, width=6),
                dbc.Col([
                    dbc.Input(
                        id=id, 
                        value=value,
                        placeholder=placeholder,
                        type='number', 
                        style={'text-align': 'right'}
                    )
                ], width=6)
            ], row=True)

        return [
            # hidden state div
            html.Div(
                self.dump(), 
                id=self.get_id(self.id, 'state'), 
                style={'display': 'none'}
            ),
            gen_formgroup('Lower bound', 'lb', lb, '-∞'),
            gen_formgroup('Upper bound', 'ub', ub, '∞'),
            gen_formgroup('Mean', 'mean', mean),
            gen_formgroup('Standard deviation', 'std', std),
            dbc.Button(
                'Update', 
                id=self.get_id(self.id, 'update'), 
                color='primary'
            )
        ]

    @classmethod
    def register_callbacks(cls, app, decimals=2):
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
            Output(cls.get_id(MATCH, 'mean'), 'placeholder'),
            [
                Input(cls.get_id(MATCH, type), 'value') 
                for type in ('lb', 'ub', 'std')
            ]
        )
        def update_mean_placeholder(lb, ub, std):
            dist_type = cls._get_dist_type(lb, ub, std=std)
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
            Output(cls.get_id(MATCH, 'std'), 'placeholder'),
            [
                Input(cls.get_id(MATCH, type), 'value') 
                for type in ('lb', 'ub', 'mean')
            ]
        )
        def update_std_placeholder(lb, ub, mean):
            dist_type = cls._get_dist_type(lb, ub, mean)
            if dist_type is None:
                return
            if dist_type == 'uniform':
                std = (1/12. * (ub-lb)**2)**.5
            elif dist_type == 'expon':
                std = mean - lb
            elif dist_type == 'rexpon':
                std = ub - mean
            elif dist_type == 'max-entropy':
                std = cls(id='tmp').fit(lb, ub, mean).std()
            return round(std, decimals)

        @app.callback(
            Output(cls.get_id(MATCH, 'state'), 'children'),
            [Input(cls.get_id(MATCH, 'update'), 'n_clicks')],
            [
                State(cls.get_id(MATCH, 'state'), 'id'),
                State(cls.get_id(MATCH, 'state'), 'children'),
                State(cls.get_id(MATCH, 'lb'), 'value'),
                State(cls.get_id(MATCH, 'ub'), 'value'),
                State(cls.get_id(MATCH, 'mean'), 'value'),
                State(cls.get_id(MATCH, 'std'), 'value')
            ]
        )
        def update_forecast(_, id, children, lb, ub, mean, std):
            try:
                return cls(id['dist-id']).fit(lb, ub, mean, std).dump()
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
        def fit_max_entropy(lb, ub, mean, std):
            # 2.58 standard deviations = 99.5th percentile in normal
            lb = mean - 2.58*std if lb is None else lb
            ub = mean + 2.58*std if ub is None else ub
            moment_funcs, values = [], []
            if mean is not None:
                moment_funcs.append(lambda x: x)
                values.append(mean)
            mean = (lb + ub)/2. if mean is None else mean
            if std is not None:
                moment_funcs.append(lambda x: (x-mean)**2)
                values.append(std**2)
            self._dist = MaxEntropy().fit(lb, ub, moment_funcs, values)

        dist_type = self._get_dist_type(lb, ub, mean, std)
        self._dist_type = dist_type
        self._fit_args = lb, ub, mean, std
        if dist_type == 'uniform':
            self._dist = uniform(lb, ub-lb)
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
            fit_max_entropy(lb, ub, mean, std)
        return self

    @staticmethod
    def _get_dist_type(lb=None, ub=None, mean=None, std=None):
        """
        Get the type of distribution based on available values.
        """
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
            'cls': self.__class__.__name__,
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
            dist._dist = MaxEntropy()
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