"""# Moments distribution

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

import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import MATCH, Input, Output, State
from smoother import Smoother, MomentConstraint

import json


class Moments(Smoother):
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
        self._elicitation_args = lb, ub, mean, std

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
                'props': {'children': self.elicitation(
                    *self._elicitation_args
                )
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
        lb : float, default=0

        ub : float, default=1

        mean : float or None, default=None

        std : float or None, default=None

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
                for type in ('lb', 'ub')
            ],
            [State(Moments.get_id(MATCH, 'mean'), 'placeholder')]
        )
        def update_mean_placeholder(lb, ub, curr_mean):
            # mean placeholder is midway between lower and upper bound
            try:
                return round((lb + ub)/2., decimals)
            except:
                return curr_mean

        @app.callback(
            Output(Moments.get_id(MATCH, 'std'), 'placeholder'),
            [
                Input(Moments.get_id(MATCH, type), 'value') 
                for type in ('lb', 'ub', 'mean')
            ],
            [State(Moments.get_id(MATCH, 'std'), 'placeholder')]
        )
        def update_std_placeholder(lb, ub, mean, curr_placeholder):
            # std placeholder maximizes entropy
            try:
                return round(Moments('tmp').fit(lb, ub, mean).std(), decimals)
            except:
                return curr_placeholder

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

    def fit(self, lb=0, ub=1, mean=None, std=None):
        """
        Fit the smoother given bounds and moments constraints. Parameters are
        analogous to those of the constructor.

        Parameters
        ----------
        lb : scalar, default=0

        ub : scalar, default=1

        mean : float or None, default=None

        std : float or None, default=None

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

    def dump(self):
        """
        Returns
        -------
        state dictionary : str (JSON)
        """
        return json.dumps({
            'cls': 'moments',
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
        dist = cls(id=state_dict['id'])
        dist.x = np.array(state_dict['x'])
        dist._f_x = np.array(state_dict['_f_x'])
        return dist

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
        name = kwargs.pop('name', self.id)
        return go.Scatter(x=self.x, y=self.F_x, name=name, **kwargs)