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


class Quantiles():
    def __init__(self, name, quantiles, data=[], decimals=2):
        self.name = name
        self.quantiles = quantiles
        self.data = data if isinstance(data, list) else [data]
        self.series = [d for d in self.data if isinstance(d, Series)]
        self.decimals = decimals
        self.cell_template = '{{:.{}f}}'.format(decimals)
        self.columns = ['Percentile'] + [d.name for d in self.data]

    def dash_table(self, app):
        layout = [
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

        @app.callback(
            Output(self.name, 'data'),
            [
                Input(d.name, 'children') 
                for d in self.data if isinstance(d, Smoother)
            ]
        )
        def update_table(*state_dicts):
            records = []
            smoothers = [Smoother.load(state) for state in state_dicts]
            data = smoothers + self.series
            for q in self.quantiles:
                record = {
                    d.name: self.cell_template.format(d.quantile(q)) 
                    for d in data
                }
                record['Percentile'] = 100*q
                records.append(record)
            return records

        return layout

    def bar_plot(records, col, *args, **kwargs):
        x, y, width = [], [], []
        for i in range(1, len(records)):
            x_i, x_j = float(records[i-1][col]), float(records[i][col])
            q_i = float(records[i-1]['Percentile'])
            q_j = float(records[i]['Percentile'])
            x.append((x_i + x_j)/2)
            width.append(x_j - x_i)
            y.append((q_j - q_i) / (100*width[-1]))
        return go.Bar(x=x, y=y, width=width, name=col, *args, **kwargs)