from .series import Series
from .smoothers import Smoother

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State


class Table():
    def __init__(self, name, data, decimals):
        self.name = name
        self.data = data if isinstance(data, list) else [data]
        self.series = [d for d in self.data if isinstance(d, Series)]
        self.cell_template = '{{:.{}f}}'.format(decimals)

    def get_layout(self):
        return [
            dash_table.DataTable(
                id=self.name, 
                columns=[{'id': col, 'name': col} for col in self.columns],
                style_as_list_view=True,
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                }
            )
        ]

    def register_table_callback(self, app, get_records):
        @app.callback(
            Output(self.name, 'data'),
            [
                Input(d.name, 'children')
                for d in self.data if isinstance(d, Smoother)
            ]
        )
        def update_table(*state_dicts):
            smoothers = [Smoother.load(state) for state in state_dicts]
            return get_records(smoothers + self.series)


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

    def bar_plot(records, col, *args, **kwargs):
        x, y, width = [], [], []
        for record in records:
            min_, max_ = record['Bin min'], record['Bin max']
            x.append((min_ + max_)/2)
            y.append(float(record[col]))
            width.append(max_ - min_)
        return go.Bar(x=x, y=y, width=width, name=col, *args, **kwargs)


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

    def bar_plot(records, col, *args, **kwargs):
        x, y, width = [], [], []
        for i in range(len(records)-1):
            x_i, x_j = float(records[i][col]), float(records[i+1][col])
            q_i = float(records[i]['Percentile'])
            q_j = float(records[i+1]['Percentile'])
            x.append((x_i + x_j)/2)
            width.append(x_j - x_i)
            y.append((q_j - q_i) / (100*width[-1]))
        return go.Bar(x=x, y=y, width=width, name=col, *args, **kwargs)