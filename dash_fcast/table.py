from .smoother import Smoother
from .utils import get_changed_cells, get_trigger_ids, get_smoother_trigger_ids, update_records, records_to_dict

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

def register_table_callbacks(app):
    @app.callback(
        Output({'type': 'table-state', 'table-id': MATCH}, 'children'),
        [
            Input({'type': 'table', 'table-id': MATCH}, 'data_timestamp'),
            Input({'type': 'row-add', 'table-id': MATCH}, 'n_clicks'),
            Input({'type': 'smoother-state', 'smoother-id': ALL}, 'children')
        ],
        [
            State({'type': 'table-state', 'table-id': MATCH}, 'children'),
            State({'type': 'table', 'table-id': MATCH}, 'data')
        ]
    )
    def update_table_state(_, add_row, smoother_states, table_state, data):
        table = Table.load(table_state)
        table._handle_data_updates(smoother_states, data)
        table._handle_add_row_updates(add_row)
        table._handle_smoother_updates(smoother_states)
        # indicate the table has experienced a callback
        table._first_callback = False
        return table.dump()

    @app.callback(
        [
            Output({'type': 'table', 'table-id': MATCH}, 'columns'),
            Output({'type': 'table', 'table-id': MATCH}, 'data')
        ],
        [Input({'type': 'table-state', 'table-id': MATCH}, 'children')]
    )
    def update_table(table_state):
        table = Table.load(table_state)
        return table.get_columns(), table._data


class Table():
    def __init__(self, id=None, bins=[], datatable={}, row_addable=False):
        self.id = id
        self.bins = bins
        self.datatable = datatable
        self.row_addable = row_addable
        # ids of smoothers displayed in the table
        self._smoother_ids = []
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
                        id={'type': 'table-state', 'table-id': self.id}, 
                        style={'display': 'none'}
                    ),
                    self.get_table(),
                    html.Br(),
                    dbc.Button(
                        'Add row',
                        id={'type': 'row-add', 'table-id': self.id},
                        color='primary',
                        style={} if self.row_addable else {'display': 'none'}
                    )
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
            id={'type': 'table', 'table-id': self.id},
            columns=self.get_columns(),
            data=self._data,
            style_as_list_view=True,
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
            for id in self._smoother_ids
        ]
        return columns

    def get_data(self, smoothers=[], bins=None):
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
            for smoother in smoothers:
                bin_start = -np.inf if bin[0] is None else bin[0]
                bin_end = np.inf if bin[1] is None else bin[1]
                cdf = 100*smoother.cdf(bin_end)
                record.update({
                    smoother.id+'pdf': cdf - 100*smoother.cdf(bin_start),
                    smoother.id+'cdf': cdf
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
            key: self.__dict__[key] for key in (
                'id', 
                'bins',  
                'datatable',
                '_smoother_ids', 
                '_data',
                '_first_callback'
            )
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
        state_dict = json.loads(state_dict)
        table = cls(
            **{key: state_dict[key] for key in ('id', 'bins', 'datatable')}
        )
        table._smoother_ids = state_dict['_smoother_ids']
        table._data = state_dict['_data']
        table._first_callback = state_dict['_first_callback']
        return table

    def _handle_data_updates(self, smoother_states, data):
        def update_bins():
            self.bins = [
                (record['bin-start'], record['bin-end']) for record in data
            ]

        def update_row(i):
            bins = [(data[i]['bin-start'], data[i]['bin-end'])]
            self._data[i].update(self.get_data(smoothers, bins)[0])

        trigger_ids = get_trigger_ids(dash.callback_context)
        if {'type': 'table', 'table-id': self.id} not in trigger_ids:
            # no data update
            return

        update_bins()
        if len(data) < len(self._data):
            # row was deleted
            self._data = data
            return

        changed_cells = get_changed_cells(self._data, data)
        changed_rows = [cell[0] for cell in changed_cells]
        smoothers = [Smoother.load(state) for state in smoother_states]
        [update_row(i) for i in changed_rows]
        return self

    def _handle_add_row_updates(self, add_row):
        trigger_ids = get_trigger_ids(dash.callback_context)
        if not (
            add_row 
            and {'type': 'row-add', 'table-id': self.id} in trigger_ids
        ):
            return

        self.bins.append((None, None))
        self._data.append({})

    def _handle_smoother_updates(self, smoother_states):
        """
        Handles an update to the table state triggered by a change to a 
        smoother state. If this is the first callback updating the table 
        state, update the data for the entire table. Otherwise, find the 
        smoother which triggered the callback and update only those records.
        """
        self._smoother_ids = [
            json.loads(state)['id'] for state in smoother_states
        ]
        smoother_trigger_ids = (
            self._smoother_ids if self._first_callback
            else get_smoother_trigger_ids(dash.callback_context)
        )
        smoother_states = [
            state for state in smoother_states 
            if json.loads(state)['id'] in smoother_trigger_ids
        ]
        smoothers = [Smoother.load(state) for state in smoother_states]
        update_records(self._data, self.get_data(smoothers))
        return self

    def bar_plot(self, col, **kwargs):
        x, y, width = [], [], []
        for record in self._data:
            bin_start, bin_end = record['bin-start'], record['bin-end']
            if not (bin_start is None or bin_end is None):
                x.append((bin_start + bin_end)/2.)
                width.append(bin_end - bin_start)
                y.append(record[col+'pdf'] / (100*width[-1])) 
        name = kwargs.get('name', col)
        return go.Bar(x=x, y=y, width=width, name=name, **kwargs)
    

# class Table():
#     def __init__(self, name, iv=[0, .25, .5, .75, 1], objects=[]):
#         self.name = name
#         self.iv = iv
#         self.objects = objects
#         self._data = {
#             obj.name: [obj.quantile(q) for q in iv] for obj in objects
#         }

#     def get_table_data(self):
#         return [
#             {
#                 'Percentile': 100*q, 
#                 **{key: val[i] for key, val in self._data.items()}
#             }
#             for i, q in enumerate(self.iv)
#         ]

#     def render(self, app, iv_editable=True):
#         layout = [
#             dash_table.DataTable(
#                 id=self.name+'-table',
#                 columns=self._get_columns(iv_editable),
#                 data=self.get_table_data(),
#                 style_as_list_view=True,
#             ),
#             html.Div(self.dump(), id=self.name, style={'display': 'none'})
#         ]
#         self._register_table_state_callback(app)

#         @app.callback(
#             Output(self.name+'-table', 'data'),
#             [Input(self.name, 'children')]
#         )
#         def update_table_data(table_state):
#             table = Table.load(table_state)
#             return table.get_table_data()

#         return layout

#     def _get_columns(self, iv_editable):
#         iv_col = {
#             'id': 'Percentile', 
#             'name': 'Percentile', 
#             'type': 'numeric',
#             'editable': iv_editable
#         }
#         columns = [
#             {
#                 'id': obj.name, 
#                 'name': obj.name, 
#                 'type': 'numeric',
#                 'editable': True,
#                 'format': Format(scheme=Scheme.fixed, precision=2)
#             } 
#             for obj in self.objects
#         ]
#         return [iv_col] + columns

#     def _register_table_state_callback(self, app):
#         inputs, states = self._get_inputs_states()

#         @app.callback(Output(self.name, 'children'), inputs, states)
#         def update_table_state(*inputs_states):
#             params = partition_inputs_states(list(inputs_states))
#             table = Table.load(params['table_state'])
#             ctx = dash.callback_context
#             triggers = [t['prop_id'].split('.')[0] for t in ctx.triggered]
#             if self.name+'-table' in triggers:
#                 register_table_data_change(table, params)
#             register_smoother_state_changes(table, params, triggers)
#             return table.dump()

#         def partition_inputs_states(inputs_states):
#             return {
#                 'smoother_inputs': inputs_states[1:len(inputs)],
#                 'table_data': inputs_states[len(inputs)],
#                 'table_data_previous': inputs_states[len(inputs)+1],
#                 'table_state': inputs_states[len(inputs)+2],
#                 'smoother_states': inputs_states[len(inputs)+3:]
#             }

#         def register_table_data_change(table, params):
#             changed_cells = get_changed_cells(
#                 params['table_data'], params['table_data_previous']
#             )
#             changed_cols = [cell[1] for cell in changed_cells]
#             if 'Percentile' in changed_cols:
#                 table.iv = [
#                     row['Percentile']/100. for row in params['table_data']
#                 ]
#                 update_table_data(
#                     table, 
#                     params['smoother_inputs'] + params['smoother_states']
#                 )
#             register_smoother_data_changes(table, params, changed_cols)

#         def register_smoother_data_changes(table, params, changed_cols):
#             data = list_orient(params['table_data'])
#             for state in params['smoother_states']:
#                 if json.loads(state)['name'] in changed_cols:
#                     smoother = Smoother.load(state)
#                     table._data[smoother.id] = data[smoother.id]

#         def register_smoother_state_changes(table, params, triggers):
#             update_table_data(
#                 table, 
#                 [
#                     state for state in params['smoother_inputs'] 
#                     if json.loads(state)['name'] in triggers
#                 ]
#             )

#         def update_table_data(table, smoother_states):
#             for state in smoother_states:
#                 smoother = Smoother.load(state)
#                 table._data[smoother.id] = [
#                     smoother.ppf(q) for q in table.iv
#                 ]

#     def _get_inputs_states(self):
#         inputs = [Input(self.name+'-table', 'data_timestamp')]
#         states = [
#             State(self.name+'-table', 'data'),
#             State(self.name+'-table', 'data_previous'), 
#             State(self.name, 'children')
#         ]
#         for obj in self.objects:
#             if isinstance(obj, MomentSmoother):
#                 inputs.append(Input(obj.name, 'children'))
#             elif isinstance(obj, MassSmoother):
#                 states.append(State(obj.name, 'children'))
#         return inputs, states

#     def dump(self):
#         return json.dumps(
#             {'name': self.name, 'iv': self.iv, '_data': self._data}
#         )

#     def load(state_dict):
#         state_dict = json.loads(state_dict)
#         table = Table(state_dict['name'], state_dict['iv'])
#         table._data = state_dict['_data']
#         return table

#     def bar_plot(self, col, **kwargs):
#         data = np.array(self._data[col])
#         x = (data[:-1] + data[1:]) / 2
#         width = np.diff(data)
#         y = np.diff(self.iv) / width
#         name = kwargs.get('name', col)
#         return go.Bar(x=x, y=y, width=width, name=name, **kwargs)