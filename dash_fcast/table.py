from .series import Series
from .smoothers import Smoother, MassSmoother, MomentSmoother
from .utils import get_changed_cells, list_orient

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from dash_table.Format import Format, Scheme

import json


class Table():
    def __init__(self, name, iv=[0, .25, .5, .75, 1], objects=[]):
        self.name = name
        self.iv = iv
        self.objects = objects
        self._data = {
            obj.name: [obj.quantile(q) for q in iv] for obj in objects
        }

    def get_table_data(self):
        return [
            {
                'Percentile': 100*q, 
                **{key: val[i] for key, val in self._data.items()}
            }
            for i, q in enumerate(self.iv)
        ]

    def render(self, app, iv_editable=True):
        layout = [
            dash_table.DataTable(
                id=self.name+'-table',
                columns=self._get_columns(iv_editable),
                data=self.get_table_data(),
                style_as_list_view=True,
            ),
            html.Div(self.dump(), id=self.name, style={'display': 'none'})
        ]
        self._register_table_state_callback(app)

        @app.callback(
            Output(self.name+'-table', 'data'),
            [Input(self.name, 'children')]
        )
        def update_table_data(table_state):
            table = Table.load(table_state)
            return table.get_table_data()

        return layout

    def _get_columns(self, iv_editable):
        iv_col = {
            'id': 'Percentile', 
            'name': 'Percentile', 
            'type': 'numeric',
            'editable': iv_editable
        }
        columns = [
            {
                'id': obj.name, 
                'name': obj.name, 
                'type': 'numeric',
                'editable': True,
                'format': Format(scheme=Scheme.fixed, precision=2)
            } 
            for obj in self.objects
        ]
        return [iv_col] + columns

    def _register_table_state_callback(self, app):
        inputs, states = self._get_inputs_states()

        @app.callback(Output(self.name, 'children'), inputs, states)
        def update_table_state(*inputs_states):
            params = partition_inputs_states(list(inputs_states))
            table = Table.load(params['table_state'])
            ctx = dash.callback_context
            triggers = [t['prop_id'].split('.')[0] for t in ctx.triggered]
            if self.name+'-table' in triggers:
                register_table_data_change(table, params)
            register_smoother_state_changes(table, params, triggers)
            return table.dump()

        def partition_inputs_states(inputs_states):
            return {
                'smoother_inputs': inputs_states[1:len(inputs)],
                'table_data': inputs_states[len(inputs)],
                'table_data_previous': inputs_states[len(inputs)+1],
                'table_state': inputs_states[len(inputs)+2],
                'smoother_states': inputs_states[len(inputs)+3:]
            }

        def register_table_data_change(table, params):
            changed_cells = get_changed_cells(
                params['table_data'], params['table_data_previous']
            )
            changed_cols = [cell[1] for cell in changed_cells]
            if 'Percentile' in changed_cols:
                table.iv = [
                    row['Percentile']/100. for row in params['table_data']
                ]
                update_table_data(
                    table, 
                    params['smoother_inputs'] + params['smoother_states']
                )
            register_smoother_data_changes(table, params, changed_cols)

        def register_smoother_data_changes(table, params, changed_cols):
            data = list_orient(params['table_data'])
            for state in params['smoother_states']:
                if json.loads(state)['name'] in changed_cols:
                    smoother = Smoother.load(state)
                    table._data[smoother.name] = data[smoother.name]

        def register_smoother_state_changes(table, params, triggers):
            update_table_data(
                table, 
                [
                    state for state in params['smoother_inputs'] 
                    if json.loads(state)['name'] in triggers
                ]
            )

        def update_table_data(table, smoother_states):
            for state in smoother_states:
                smoother = Smoother.load(state)
                table._data[smoother.name] = [
                    smoother.ppf(q) for q in table.iv
                ]

    def _get_inputs_states(self):
        inputs = [Input(self.name+'-table', 'data_timestamp')]
        states = [
            State(self.name+'-table', 'data'),
            State(self.name+'-table', 'data_previous'), 
            State(self.name, 'children')
        ]
        for obj in self.objects:
            if isinstance(obj, MomentSmoother):
                inputs.append(Input(obj.name, 'children'))
            elif isinstance(obj, MassSmoother):
                states.append(State(obj.name, 'children'))
        return inputs, states

    def dump(self):
        return json.dumps(
            {'name': self.name, 'iv': self.iv, '_data': self._data}
        )

    def load(state_dict):
        state_dict = json.loads(state_dict)
        table = Table(state_dict['name'], state_dict['iv'])
        table._data = state_dict['_data']
        return table

    def bar_plot(self, col, **kwargs):
        data = np.array(self._data[col])
        x = (data[:-1] + data[1:]) / 2
        width = np.diff(data)
        y = np.diff(self.iv) / width
        name = kwargs.get('name', col)
        return go.Bar(x=x, y=y, width=width, name=name, **kwargs)


class Bins(Table):
    def __init__(self, name, bins, data=[], decimals=2):
        super().__init__(name, data, decimals)
        self.bins = bins
        self.columns = ['Bin min', 'Bin max'] + [d.name for d in self.data]

    def dash_table(self, app):
        def get_records(data):
            return [get_record(data, bin) for bin in self.bins]

        def get_record(data, bin):
            template = self.cell_template
            record = {
                d.name: template.format(d.cdf(bin[1]) - d.cdf(bin[0]))
                for d in data
            }
            record.update({'Bin min': bin[0], 'Bin max': bin[1]})
            return record

        self.register_table_callback(app, get_records)
        return self.get_layout()


class Quantiles(Table):
    def __init__(self, name, quantiles, data=[], decimals=2):
        super().__init__(name, data, decimals)
        self.quantiles = quantiles
        self.columns = ['Percentile'] + [d.name for d in self.data]

    def dash_table(self, app):
        def get_records(data):
            return [get_record(data, q) for q in self.quantiles]

        def get_record(data, q):
            record = {
                d.name: self.cell_template.format(d.quantile(q)) 
                for d in data
            }
            record['Percentile'] = 100*q
            return record

        self.register_table_callback(app, get_records)
        return self.get_layout()