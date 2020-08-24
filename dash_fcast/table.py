from .distributions import dist_classes 
from .utils import get_changed_cell, get_trigger_ids, get_dist_trigger_ids, update_records

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash_table.Format import Format, Scheme

import json

def get_id(type_, id):
    return {'type': type_, 'table-id': id}


class Table():
    def __init__(self, id=None, bins=[], datatable={}, row_addable=False):
        self.id = id
        self.bins = bins
        self.datatable = datatable
        self.row_addable = row_addable
        # ids of smoothers displayed in the table
        self._dist_ids = []
        # table data in records format
        self._data = self.get_data()
        # indicates that this is the first callback updating this table
        self._first_callback = True

    def to_plotly_json(self):
        return {
            'props': {
                'children': [
                    # hidden div holding the table state
                    html.Div(
                        self.dump(), 
                        id=get_id('state', self.id), 
                        style={'display': 'none'}
                    ),
                    self.get_table(),
                    html.Div([
                        html.Br(),
                        dbc.Button(
                            'Add row',
                            id=get_id('row-add', self.id),
                            color='primary',
                        )
                    ], style={} if self.row_addable else {'display': 'none'})
                ]
            },
            'type': 'Div',
            'namespace': 'dash_html_components'
        }

    def get_table(self):
        """
        Returns
        -------
        layout : list of dash_table.Datatable
        """
        return dash_table.DataTable(
            id=get_id('table', self.id),
            columns=self.get_columns(),
            data=self._data,
            **self.datatable
        )

    def get_columns(self):
        """
        Returns
        -------
        columns : list of dicts
            List of column dictionaries in dash_table columns format.
        """
        def get_smoother_columns(id):
            return [
                {
                    'id': id+'pdf', 
                    'name': id,
                    'editable': False,
                    'type': 'numeric',
                    'format': Format(scheme=Scheme.fixed, precision=2)
                },
                {
                    'id': id+'cdf', 
                    'name': id + ' (cdf)',
                    'editable': False,
                    'type': 'numeric',
                    'format': Format(scheme=Scheme.fixed, precision=2)
                }
            ]

        columns = [
            {
                'id': 'bin-start', 
                'name': 'Bin start', 
                'type': 'numeric'
            },
            {
                'id': 'bin-end', 
                'name': 'Bin end', 
                'type': 'numeric'
            }
        ]
        [
            columns.extend(get_smoother_columns(id)) 
            for id in self._dist_ids
        ]
        return columns

    def get_data(self, distributions=[], bins=None):
        """
        Parameters
        ----------
        smoothers : list of dash_fcast.Smoother, default=[]
            Smoothers whose data should will be stored.

        bins : list or None, default=None
            List of (bin start, bin end) lists or tuples. If `None` this 
            method uses `self.bins`.

        Returns
        -------
        records : list
            List of records (dictionaries) mapping column ids to data entry.
        """
        def get_record(bin):
            record = {'bin-start': bin[0], 'bin-end': bin[1]}
            for dist in distributions:
                bin_start = -np.inf if bin[0] is None else bin[0]
                bin_end = np.inf if bin[1] is None else bin[1]
                cdf = 100*dist.cdf(bin_end)
                record.update({
                    dist.id+'pdf': cdf - 100*dist.cdf(bin_start),
                    dist.id+'cdf': cdf
                })
            return record

        bins = self.bins if bins is None else bins
        return [get_record(bin) for bin in bins]

    def dump(self):
        """
        Returns
        -------
        state_dict : dict
            Dictionary representing the table state.
        """
        return json.dumps({
            'id': self.id,
            'bins': self.bins,
            'datatable': self.datatable,
            'row_addable': self.row_addable,
            '_dist_ids': self._dist_ids,
            '_data': self._data,
            '_first_callback': self._first_callback
        })

    @classmethod
    def load(cls, state_dict):
        """
        Parameters
        ----------
        state_dict : dict
            Table state dictionary; output from `dash_fcast.Table.dump`.

        Returns
        -------
        table : dash_fcast.Table
            Table specified by the table state.
        """
        state = json.loads(state_dict)
        table = cls(
            state['id'], 
            state['bins'], 
            state['datatable'], 
            state['row_addable']
        )
        table._dist_ids = state['_dist_ids']
        table._data = state['_data']
        table._first_callback = state['_first_callback']
        return table

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(get_id('state', MATCH), 'children'),
            [
                Input(get_id('table', MATCH), 'data_timestamp'),
                Input(get_id('row-add', MATCH), 'n_clicks'),
                Input(
                    {'type': 'state', 'dist-cls': ALL, 'dist-id': ALL}, 'children'
                )
            ],
            [
                State(get_id('state', MATCH), 'children'),
                State(get_id('table', MATCH), 'data')
            ]
        )
        def update_table_state(_, add_row, dist_states, table_state, data):
            trigger_ids = get_trigger_ids(dash.callback_context)
            table = Table.load(table_state)
            table._handle_data_updates(dist_states, data, trigger_ids)
            table._handle_add_row_updates(add_row, trigger_ids)
            table._handle_dist_updates(dist_states)
            # indicate the table has experienced a callback
            table._first_callback = False
            return table.dump()

        @app.callback(
            [
                Output(get_id('table', MATCH), 'columns'),
                Output(get_id('table', MATCH), 'data')
            ],
            [Input(get_id('state', MATCH), 'children')]
        )
        def update_table(table_state):
            table = Table.load(table_state)
            return table.get_columns(), table._data

    def _handle_data_updates(self, dist_states, data, trigger_ids):
        def update_bins():
            self.bins = [(d['bin-start'], d['bin-end']) for d in data]

        def update_row(i):
            bins = [(data[i]['bin-start'], data[i]['bin-end'])]
            self._data[i].update(self.get_data(distributions, bins)[0])

        if get_id('table', self.id) not in trigger_ids:
            # no data update
            return

        update_bins()
        if len(data) < len(self._data):
            # row was deleted
            self._data = data
            return

        changed_row, _ = get_changed_cell(self._data, data)
        distributions = []
        # smoothers = [Smoother.load(state) for state in dist_states]
        update_row(changed_row)
        return self

    def _handle_add_row_updates(self, add_row, trigger_ids):
        if add_row and get_id('row-add', self.id) in trigger_ids:
            self.bins.append((None, None))
            self._data.append({})

    def _handle_dist_updates(self, dist_states):
        """
        Handles an update to the table state triggered by a change to a 
        smoother state. If this is the first callback updating the table 
        state, update the data for the entire table. Otherwise, find the 
        smoother which triggered the callback and update only those records.
        """
        self._dist_ids = [
            json.loads(state)['id'] for state in dist_states
        ]
        dist_trigger_ids = (
            self._dist_ids if self._first_callback
            else get_dist_trigger_ids(dash.callback_context)
        )
        dist_states = [
            state for state in dist_states 
            if json.loads(state)['id'] in dist_trigger_ids
        ]
        # smoothers = [Smoother.load(state) for state in dist_states]
        # update_records(self._data, self.get_data(smoothers))
        return self

    def bar_plot(self, col, **kwargs):
        x, y, width = [], [], []
        for record in self._data:
            bin_start, bin_end = record['bin-start'], record['bin-end']
            if not (bin_start is None or bin_end is None):
                x.append((bin_start + bin_end)/2.)
                width.append(bin_end - bin_start)
                y.append(record[col+'pdf'] / (100*width[-1])) 
        name = kwargs.pop('name', col)
        return go.Bar(x=x, y=y, width=width, name=name, **kwargs)