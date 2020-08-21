"""# Distribution from tabular elicitation"""

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import numpy as np
from dash.dependencies import MATCH, Input, Output, State

def get_id(type_, dist_id):
    return {'type': type_, 'dist-cls': 'table', 'dist-id': dist_id}


class Table():
    def __init__(
            self, 
            id=None, 
            bins=[(0, .25), (.25, .5), (.5, .75), (.75, 1)], 
            pdf=[.25, .25, .25, .25], 
            datatable={}, 
            row_addable=False,
            *args, **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.id = id
        self.bins = bins
        self.pdf = pdf
        self.datatable = datatable
        self.row_addable = row_addable

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
        return [
            html.Div(
                self.dump(),
                id=get_id('state', self.id),
                style={'display': 'none'}
            ),
            dash_table.DataTable(
                id=get_id('table', self.id),
                columns=self.get_columns(),
                data=self.get_data(),
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
        return [
            {'id': 'bin-start', 'name': 'Bin start'},
            {'id': 'bin-end', 'name': 'Bin end'},
            {'id': 'pdf', 'name': 'Probability'},
            {'id': 'cdf', 'name': 'Probability (cum)'}
        ]

    def get_data(self, bins=None, pdf=None):
        bins = self.bins if bins is None else bins
        pdf = self.pdf if pdf is None else pdf
        assert len(bins) == len(pdf), (
            'bins and pdf must be lists of the same length'
        )

        def get_record(bin, pdf_i, cdf_i):
            return {
                'bin-start': bin[0],
                'bin-end': bin[1],
                'pdf': 100*pdf_i,
                'cdf': 100*cdf_i
            }

        cdf = np.cumsum(np.array(pdf))
        return [
            get_record(bin, pdf_i, cdf_i) 
            for bin, pdf_i, cdf_i in zip(bins, pdf, cdf)
        ]

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(get_id('state', MATCH), 'children'),
            [Input(get_id('table', MATCH), 'data_timestamp')],
            [State(get_id('table', MATCH), 'data')]
        )
        def update_table_state(_, data):
            pass

        @app.callback(
            Output(get_id('table', MATCH), 'data'),
            [Input(get_id('state', MATCH), 'children')]
        )
        def update_table(table_state):
            pass

    def dump(self):
        pass

    @classmethod
    def load(cls, state_dict):
        pass

    def pdf_plot(self):
        pass

    def bar_plot(self):
        pass

    def cdf_plot(self):
        pass