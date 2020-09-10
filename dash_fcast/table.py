"""# Table display"""

from .distributions import load_distributions
from .utils import get_changed_cell, get_deleted_row, get_trigger_ids, get_dist_trigger_ids, match_record, update_records

"""# Table """

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


class Table():
    """
    Parameters and attributes
    -------------------------
    id : str
        Table identifier.

    bins : list, default=[0, .25, .5, .75, 1]
        List of bin 'breakpoints'. Bins are contiguous. The first bin starts 
        at `bins[0]`. The last bin ends at `bins[-1]`.

    datatable : dict, default={}
        Keyword arguments passed to the datatable in which table data are 
        displayed.

    row_addable : bool, default=False
        Indicates that users can add rows to the table.
    """
    def __init__(
            self, id, bins=[0, .25, .5, .75, 1], datatable={}, 
            row_addable=False
        ):
        self.id = id
        self.bins = bins
        self.datatable = datatable
        self.row_addable = row_addable
        # ids of distributions displayed in the table
        self._dist_ids = []
        # table data in records format
        self._data = self.get_data()
        # indicates that this is the first callback updating this table
        self._first_callback = True

    @staticmethod
    def get_id(id, type='state'):
        """
        Parameters
        ----------
        id : str
        
        type : str, default='state'
            Type of object associated with the table.

        Returns
        -------
        id dictionary : dict
            Dictionary identifier.
        """
        return {'table-id': id, 'type': type}

    def to_plotly_json(self):
        return {
            'props': {
                'children': [
                    html.Div(
                        self.dump(), 
                        id=Table.get_id(self.id, 'state'), 
                        style={'display': 'none'}
                    ),
                    dash_table.DataTable(
                        id=Table.get_id(self.id, 'table'),
                        columns=self.get_columns(),
                        data=self._data,
                        **self.datatable
                    ),
                    html.Div([
                        html.Br(),
                        dbc.Button(
                            'Add row',
                            id=Table.get_id(self.id, 'row-add'),
                            color='primary',
                        )
                    ], style={} if self.row_addable else {'display': 'none'})
                ]
            },
            'type': 'Div',
            'namespace': 'dash_html_components'
        }

    def get_columns(self):
        """
        Returns
        -------
        columns : list of dicts
            List of column dictionaries in dash_table columns format.
        """
        format = Format(scheme=Scheme.fixed, precision=2)
        def get_dist_columns(id):
            return [
                {
                    'id': id+'pdf', 
                    'name': id,
                    'editable': False,
                    'type': 'numeric',
                    'format': format
                },
                {
                    'id': id+'cdf', 
                    'name': id + ' (cdf)',
                    'editable': False,
                    'type': 'numeric',
                    'format': format
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
            columns.extend(get_dist_columns(id)) 
            for id in self._dist_ids
        ]
        return columns

    def get_data(self, bins=None, distributions=[], data=[]):
        """
        Parameters
        ----------
        bins : list of scalars or None, default=None
            If `None` this method uses `self.bins`.

        distributions : list, default=[]
            List of distributions like those specified in 
            `dash_fcast.distributions`.

        data : list of dicts
            Existing data in records format. If a bin matches existing data,
            that record is returned without updating the distribution pdfs.

        Returns
        -------
        records : list
            List of records (dictionaries) mapping column ids to data entry.
        """
        def get_record(bin_start, bin_end):
            record = {'bin-start': bin_start, 'bin-end': bin_end}
            match = match_record(record, data)
            if match:
                return match
            bin_start = -np.inf if bin_start == '' else bin_start
            bin_end = np.inf if bin_end == '' else bin_end
            for dist in distributions:
                cdf_end = 100*dist.cdf(bin_end)
                record.update({
                    dist.id+'pdf': cdf_end - 100*dist.cdf(bin_start),
                    dist.id+'cdf': cdf_end
                })
            return record

        bins = self.bins if bins is None else bins
        return [get_record(*bin) for bin in zip(bins[:-1], bins[1:])]

    @staticmethod
    def register_callbacks(app):
        """
        Register dash callbacks for table objects.

        Parameters
        ----------
        app : dash.Dash
            App with which to register the callbacks.
        """
        @app.callback(
            Output(Table.get_id(MATCH, 'state'), 'children'),
            [
                Input(Table.get_id(MATCH, 'table'), 'data_timestamp'),
                Input(Table.get_id(MATCH, 'row-add'), 'n_clicks'),
                Input(
                    {'type': 'state', 'dist-cls': ALL, 'dist-id': ALL}, 
                    'children'
                )
            ],
            [
                State(Table.get_id(MATCH, 'state'), 'children'),
                State(Table.get_id(MATCH, 'table'), 'data')
            ]
        )
        def update_table_state(_, add_row, dist_states, table_state, data):
            trigger_ids = get_trigger_ids(dash.callback_context)
            table = Table.load(table_state)
            if table._first_callback:
                table._handle_first_callback(dist_states)
            else:
                table._handle_data_updates(dist_states, data, trigger_ids)
                table._handle_row_add(add_row, dist_states, trigger_ids)
                table._handle_dist_updates(dist_states)
            return table.dump()

        @app.callback(
            [
                Output(Table.get_id(MATCH, 'table'), 'columns'),
                Output(Table.get_id(MATCH, 'table'), 'data')
            ],
            [Input(Table.get_id(MATCH, 'state'), 'children')]
        )
        def update_table(table_state):
            table = Table.load(table_state)
            return table.get_columns(), table._data

    def dump(self):
        """
        Returns
        -------
        state_dict : JSON dict
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
        state_dict : JSON dict
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

    def _handle_first_callback(self, dist_states):
        distributions = load_distributions(dist_states)
        self._dist_ids = [dist.id for dist in distributions]
        self._data = self.get_data(distributions=distributions)
        self._first_callback = False
        return self

    def _handle_data_updates(self, dist_states, data, trigger_ids):
        def handle_bin_update(end_updated=True):
            bin_start = [d['bin-start'] for d in data]
            bin_end = [d['bin-end'] for d in data]
            self.bins = (
                bin_start[:1] + bin_end if end_updated
                else bin_start + bin_end[-1:]
            )
            self._data = self.get_data(
                distributions=load_distributions(dist_states),
                data=self._data
            )

        if Table.get_id(self.id, 'table') not in trigger_ids:
            # no bins were updates
            return
        if len(data) < len(self._data):
            # row was deleted
            handle_bin_update()
        else:
            # bin changed
            _, changed_col = get_changed_cell(data, self._data)
            handle_bin_update(end_updated=changed_col=='bin-end')
        return self

    def _handle_row_add(self, add_row, dist_states, trigger_ids):
        if add_row and Table.get_id(self.id, 'row-add') in trigger_ids:
            self.bins.append(self.bins[-1])
            self._data = self.get_data(
                distributions=load_distributions(dist_states),
                data=self._data
            )

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
        dist_trigger_ids = get_dist_trigger_ids(dash.callback_context)
        distributions = load_distributions([
            state for state in dist_states 
            if json.loads(state)['id'] in dist_trigger_ids
        ])
        update_records(self._data, self.get_data(distributions=distributions))
        return self

    def bar_plot(self, col, **kwargs):
        """
        Parameters
        ----------
        col : str
            ID of the column (distribution) to plot.

        \*\*kwargs :
            Keyword arguments passed to `go.Bar`.

        Returns
        -------
        bar plot : go.Bar
        """
        x, y, width = [], [], []
        for record in self._data:
            bin_start, bin_end = record['bin-start'], record['bin-end']
            if '' not in (bin_start, bin_end) and bin_start < bin_end:
                x.append((bin_start + bin_end)/2.)
                width.append(bin_end - bin_start)
                y.append(record[col+'pdf'] / (100*width[-1])) 
        name = kwargs.pop('name', col)
        return go.Bar(x=x, y=y, width=width, name=name, **kwargs)