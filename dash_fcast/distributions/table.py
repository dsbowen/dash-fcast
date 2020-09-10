"""# Distribution from tabular elicitation"""

from ..utils import get_changed_cell, get_deleted_row, get_trigger_ids

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import MATCH, Input, Output, State
from dash_table.Format import Format, Scheme
from smoother import Smoother, DerivativeObjective, MassConstraint

import json

def get_id(type_, dist_id):
    """
    Parameters
    ----------
    type_ : str
        Type of table element (e.g. 'state', 'data').

    dist_id : str
        id of the table distribution, usually the table id or MATCH.

    Returns
    -------
    element id : dict
    """
    return {'type': type_, 'dist-cls': 'table', 'dist-id': dist_id}


class Table(Smoother):
    """
    Tabular distribution elicitation. Subclasses `smoother.Smoother`.
    <https://dsbowen.github.io/smoother/>.

    Parameters and attributes
    -------------------------
    id : str or None, default=None
        Unique id of the table distribution.

    bins : list of float, default=[0, .25, .5, .75, 1]
        List of 'break points' for the bins. The first bin starts at 
        `bins[0]`. The last bin ends at `bins[-1]`.

    pdf : list of float, default=[.25, .25, .25, .25]
        Probability density function. This is the amount of probability mass
        in each bin. Must sum to 1 and `len(pdf)` should be `len(bins)-1`.

    datatable : dict, default={}
        Keyword arguments for the datatable associated with the table
        distribution. See <https://dash.plotly.com/datatable>.

    row_addable : bool, default=False
        Indicates whether the forecaster can add rows.

    smoother : bool, default=False
        Indicates whether to use a smoother for interpolation..

    \*args, \*\*kwargs : 
        Arguments and keyword arguments passed to `super().__init__`.
    """
    def __init__(
            self, 
            id=None, 
            bins=[0, .25, .5, .75, 1], 
            pdf=[.25, .25, .25, .25], 
            datatable={}, 
            row_addable=False,
            smoother=False,
            *args, **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.id = id
        self.bins = bins
        self.pdf = pdf
        self.datatable = datatable
        self.row_addable = row_addable
        self.smoother = smoother

    def to_plotly_json(self):
        return {
            'props': {
                'children': self.elicitation(
                    self.bins, self.pdf, self.datatable, self.row_addable
                )
            },
            'type': 'Div',
            'namespace': 'dash_html_components'
        }

    def elicitation(self, bins, pdf, datatable={}, row_addable=False):
        """
        Parameters
        ----------
        bins : list of float or numpy.array

        pdf : list of float or numpy.array

        datatable : dict, default={}

        row_addable : bool, default=False

        Returns
        -------
        elicitation elements : list of dash elements
            Dash elements used to elicit the distribution.
        """
        return [
            html.Div(
                self.dump(),
                id=get_id('state', self.id),
                style={'display': 'none'}
            ),
            dash_table.DataTable(
                id=get_id('table', self.id),
                columns=self.get_columns(),
                data=self.get_data(bins, pdf),
                **datatable
            ),
            html.Div([
                html.Br(),
                dbc.Button(
                    'Add row',
                    id=get_id('row-add', self.id),
                    color='primary',
                )
            ], style={} if self.row_addable else {'display': 'none'})
        ]

    def get_columns(self):
        """
        Returns
        -------
        columns : list of dict
            List of dictionaries specifying the datatable columns. See
            <https://dash.plotly.com/datatable>,
        """
        format = Format(scheme=Scheme.fixed, precision=2)
        return [
            {
                'id': 'bin-start', 
                'name': 'Bin start', 
                'type': 'numeric'
            },
            {
                'id': 'bin-end', 
                'name': 'Bin end', 
                'type': 'numeric'
            },
            {
                'id': 'pdf', 
                'name': 'Probability', 
                'type': 'numeric',
                'format': format
            },
            {
                'id': 'cdf', 
                'name': 'Probability (cum)', 
                'type': 'numeric',
                'format': format
            }
        ]

    def get_data(self, bins=None, pdf=None):
        """
        Parameters
        ----------
        bins : list of float or numpy.array or None, default=None
            If `None`, use `self.bins`.

        pdf : list of float or numpy.array or None, default=None
            If `None`, use `self.pdf`.

        Returns
        -------
        records : list of dict
            Datatable data in records format.
        """
        def get_record(bin_start, bin_end, pdf_i, cdf_i):
            return {
                'bin-start': bin_start, 
                'bin-end': bin_end, 
                'pdf': 100*pdf_i,
                'cdf': 100*cdf_i
            }

        bins = self.bins if bins is None else bins
        pdf = self.pdf if pdf is None else pdf
        cdf = np.cumsum(pdf)
        assert len(bins)-1 == len(pdf)
        return [
            get_record(*args) for args in zip(bins[:-1], bins[1:], pdf, cdf)
        ]

    def fit(self, bins=None, pdf=None, derivative=2):
        """
        Fit the smoother given masses constraints.

        Parameters
        ----------
        bins : list of float or numpy.array
            Ordered list of bin break points.

        pdf : list of float or numpy.array
            Probability density function. This is the amount of probability mass
            in each bin. Must sum to 1 and `len(pdf)` should be `len(bins)-1`.

        derivative : int, default=2
            Deriviate of the derivative smoothing function to maximize. e.g. 
            `2` means the smoother will minimize the mean squaure second 
            derivative.

        Returns
        -------
        self
        """
        bins = self.bins if bins is None else bins
        pdf = self.pdf if pdf is None else pdf
        params = zip(bins[:-1], bins[1:], pdf)
        return super().fit(
            bins[0], 
            bins[-1],
            [MassConstraint(lb, ub, mass) for lb, ub, mass in params],
            DerivativeObjective(derivative)
        )

    @staticmethod
    def register_callbacks(app):
        """
        Register callbacks for the table distribution. Only register callbacks
        for the table distribution once per app.
        """
        @app.callback(
            Output(get_id('state', MATCH), 'children'),
            [
                Input(get_id('table', MATCH), 'data_timestamp'),
                Input(get_id('row-add', MATCH), 'n_clicks')
            ],
            [
                State(get_id('state', MATCH), 'children'),
                State(get_id('table', MATCH), 'data')
            ]
        )
        def update_table_state(_, add_row, table_state, data):
            trigger_ids = get_trigger_ids(dash.callback_context)
            table = Table.load(table_state)
            table._handle_data_updates(data, trigger_ids)
            table._handle_row_add(add_row, trigger_ids)
            return table.dump()

        @app.callback(
            Output(get_id('table', MATCH), 'data'),
            [Input(get_id('state', MATCH), 'children')]
        )
        def update_table(table_state):
            return Table.load(table_state).get_data()

    def dump(self):
        """
        Dump the table distribution state dictionary in JSON format.

        Returns
        -------
        state : dict, JSON
        """
        return json.dumps({
            'cls': 'table',
            'id': self.id,
            'bins': self.bins,
            'pdf': self.pdf,
            'datatable': self.datatable,
            'row_addable': self.row_addable,
            'smoother': self.smoother,
            'x': list(self.x),
            '_f_x': list(self._f_x)
        })

    @classmethod
    def load(cls, state_dict):
        """
        Load a table distribution from its state dictionary.

        Parameters
        ----------
        state_dict : dict
            Output of `Table.dump`.

        Returns
        -------
        table : `Table`
        """
        state = json.loads(state_dict)
        table = cls(
            state['id'],
            state['bins'],
            state['pdf'],
            state['datatable'],
            state['row_addable'],
            state['smoother']
        )
        table.x = np.array(state['x'])
        table._f_x = np.array(state['_f_x'])
        return table

    def _handle_data_updates(self, data, trigger_ids):
        """
        Helper method for callback updating table state which handles updates
        to the data in the data table.
        """
        def handle_row_delete():
            """
            Handle a row being deleted.
            """
            i = get_deleted_row(data, prev_data)
            pdf_i = self.pdf.pop(i)
            if i < len(self.pdf):
                self.pdf[i] += pdf_i
            handle_bin_update()

        def handle_data_update():
            """
            Handle data updates.
            """
            # Strictly speaking, it should be sufficient to handle updates for
            # only the changed column. But it's often useful to check that the
            # columns are consistent because of asynchronous updating.
            _, changed_col = get_changed_cell(data, prev_data)
            handle_bin_update(end_updated=changed_col=='bin-end')
            if changed_col == 'pdf':
                self.pdf = [d['pdf']/100. for d in data]
            else:
                cdf = np.insert([d['cdf'] for d in data], 0, 0)
                self.pdf = list(np.diff(cdf)/100.)

        def handle_bin_update(end_updated=True):
            """
            Handle bin updates.
            """
            bin_start = [d['bin-start'] for d in data]
            bin_end = [d['bin-end'] for d in data]
            self.bins = (
                bin_start[:1] + bin_end if end_updated 
                else bin_start + bin_end[-1:]
            )

        if get_id('table', self.id) not in trigger_ids:
            return
        prev_data = self.get_data()
        if len(data) < len(prev_data):
            handle_row_delete()
        else:
            handle_data_update()
        if self.smoother:
            try:
                self.fit()
            except:
                pass
        return self

    def _handle_row_add(self, add_row, trigger_ids):
        """
        Helper method for callback updating table state which handles adding
        rows.
        """
        if add_row and get_id('row-add', self.id) in trigger_ids:
            self.bins.append(self.bins[-1])
            self.pdf.append(0)

    def pdf_plot(self, **kwargs):
        """
        Parameters
        ----------
        \*\*kwargs :
            Keyword arguments for `go.Scatter`.

        Returns
        -------
        scatter : go.Scatter.
            Scatter plot of the pdf.
        """
        name = kwargs.pop('name', self.id)
        if self.smoother:
            return go.Scatter(x=self.x, y=self.f_x, name=name, **kwargs)
        heights = np.array(self.pdf) / np.diff(self.bins)
        x, y = [self.bins[0]], [heights[0]]
        values = zip(self.bins[1:], heights[:-1], heights[1:])
        for x_i, height_prev, height_curr in values:
            x += [x_i, x_i]
            y += [height_prev, height_curr]
        x.append(self.bins[-1])
        y.append(heights[-1])
        return go.Scatter(x=x, y=y, name=name, **kwargs)

    def cdf_plot(self, **kwargs):
        """
        Parameters
        ----------
        \*\*kwargs :
            Keyword arguments for `go.Scatter`.

        Returns
        -------
        scatter : go.Scatter
            Scatter plot of the cdf.
        """
        name = kwargs.pop('name', self.id)
        if self.smoother:
            return go.Scatter(x=self.x, y=self.F_x, name=name, **kwargs)
        F_x = np.insert(np.cumsum(self.pdf), 0, 0)
        return go.Scatter(x=self.bins, y=F_x, name=name, **kwargs)

    def bar_plot(self, **kwargs):
        """
        Parameters
        ----------
        \*\*kwargs :
            Keyword arguments for `go.Bar`.

        Returns
        -------
        bar plot : go.Bar
            Bar plot of the pdf in the datatable.
        """
        name = kwargs.pop('name', self.id)
        return go.Bar(
            x=(np.array(self.bins[1:]) + np.array(self.bins[:-1])) / 2.,
            y=np.array(self.pdf) / np.diff(self.bins),
            width=np.diff(self.bins),
            name=name,
            **kwargs
        )