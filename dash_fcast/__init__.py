from .series import Series
from .smoothers import MomentSmoother
from .tables import Bins, Quantiles

# from smoother import Smoother, DerivativeObjective, MassConstraint, MomentConstraint

# import dash
# import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_table
# import numpy as np
# import pandas as pd
# import plotly.express as px
# import plotly.figure_factory as ff
# import plotly.graph_objects as go
# from dash.dependencies import Input, Output, State

# BASE_COLOR, FCAST_COLOR = px.colors.qualitative.D3[0:2]
# N_BINS = 4

# base = pd.read_csv('base_data.csv')['Base'].sort_values().to_numpy()
# base_cdf = np.cumsum(np.ones(base.shape) / base.shape)
# base_lb, base_ub = round(base[0], 2), round(base[-1], 2)
# base_mean = round(base.mean(), 2)
# base_std = round(base.std(), 2)

# def gen_header(app):
#     return [
#         html.H1('Intuitive statistician', style={'text-align': 'center'}),
#         html.Div(id='smoother_state', style={'display': 'none'}),
#     ]

# def gen_moments_elicitation(app, smoother_init):
#     @app.callback(
#         Output('max-std', 'children'),
#         [Input('lb', 'value'), Input('ub', 'value'), Input('mean', 'value')],
#         [State('max-std', 'children')]
#     )
#     def update_max_std(lb, ub, mean, children):
#         try:
#             smoother = gen_moments_smoother(lb, ub, mean)
#             return 'Suggested maximum: {}'.format(round(smoother.std(), 2))
#         except:
#             return children

#     @app.callback(
#         Output('smoother_state', 'children'),
#         [Input('update', 'n_clicks')],
#         [
#             State('lb', 'value'),
#             State('ub', 'value'),
#             State('mean', 'value'),
#             State('std', 'value')
#         ]
#     )
#     def update_forecast(n_clicks, lb, ub, mean, std):
#         smoother = (
#             smoother_init if n_clicks == 0 
#             else gen_moments_smoother(lb, ub, mean, std)
#         )
#         return smoother.dump()

#     return [
#         dbc.FormGroup([
#             dbc.Label('Lower bound', html_for='lb'),
#             dbc.Input(id='lb', value=base_lb, type='number')
#         ]),
#         dbc.FormGroup([
#             dbc.Label('Upper bound', html_for='ub'),
#             dbc.Input(id='ub', value=base_ub, type='number')
#         ]),
#         dbc.FormGroup([
#             dbc.Label('Mean', html_for='mean'),
#             dbc.Input(id='mean', value=base_mean, type='number')
#         ]),
#         dbc.FormGroup([
#             dbc.Label('Standard deviation', html_for='std'),
#             dbc.Input(id='std', value=base_std, type='number'),
#             dbc.FormText(id='max-std')
#         ]),
#         dbc.Button('Update distribution', id='update', color='primary'),
#         html.Br()
#     ]

# def gen_moments_smoother(lb, ub, mean, std=None):
#     mean_const = MomentConstraint(mean, degree=1)
#     if std is None:
#         return Smoother().fit(lb, ub, [mean_const])
#     std_const = MomentConstraint(std, degree=2, type_='central', norm=True)
#     return Smoother().fit(lb, ub, [mean_const, std_const])

# def gen_masses_smoother(lb, ub, quantiles, values):
#     masses = np.diff(quantiles)
#     constraints = [
#         MassConstraint(lower, upper, mass) 
#         for lower, upper, mass in zip(values[:-1], values[1:], masses)
#     ]
#     return Smoother().fit(
#         lb, ub, constraints, objective=DerivativeObjective(1)
#     )

# def data_table(app, gen_table_data, columns):
#     @app.callback(
#         Output('table', 'data'),
#         [Input('smoother_state', 'children')]
#     )
#     def update_table(state_dict):
#         return gen_table_data(Smoother.load(state_dict))

#     return dash_table.DataTable(
#         id='table', columns=[{'id': col, 'name': col} for col in columns]
#     )


# class QuantilesTable():
#     columns = ['Percentile', 'Base', 'Forecast']

#     def __init__(self, n_bins=N_BINS, base=base):
#         self.quantiles = np.linspace(0, 1, n_bins+1)
#         self.base_values = [
#             round(np.quantile(base, q), 2) for q in self.quantiles
#         ]

#     def gen_table(self, smoother):
#         data = []
#         for q, base_val in zip(self.quantiles, self.base_values):
#             data.append({
#                 'Percentile': 100*q,
#                 'Base': base_val,
#                 'Forecast': round(smoother.ppf(q), 2)
#             })
#         return data

#     def gen_bar(self, data, key):
#         x, y, width = [], [], []
#         for i in range(1, len(data)):
#             x.append((data[i][key]+data[i-1][key])/2)
#             width.append(data[i][key]-data[i-1][key])
#             y.append(
#                 (data[i]['Percentile']-data[i-1]['Percentile'])/width[-1]/100.
#             )
#         return x, y, width

# def gen_bins_table(smoother, n_bins=N_BINS, base=base):
#     data = []
#     values = np.linspace(smoother.x[0], smoother.x[-1]+.001, n_bins+1)
#     for min_, max_ in zip(values[:-1], values[1:]):
#         data.append({
#             'Bin min': round(min_, 2),
#             'Bin max': round(max_, 2),
#             'Actual': round(((min_ < base) & (base < max_)).mean(), 2),
#             'Counterfactual': round(smoother.cdf(max_)-smoother.cdf(min_), 2)
#         })
#     return data

# def get_bins_bar(data, key):
#     x, y, width = [], [], []
#     for record in data:
#         x.append((record['Bin min'] + record['Bin max'])/2)
#         y.append(record[key])
#         width.append(record['Bin max'] - record['Bin min'])
#     return x, y, width

# def gen_pdf(smoother):
#     pdf = ff.create_distplot(
#         [base], 
#         colors=[BASE_COLOR],
#         group_labels=['Base'], 
#         show_hist=False, 
#         show_rug=False
#     )
#     pdf.add_trace(go.Scatter(
#         x=smoother.x, 
#         y=smoother.f_x, 
#         name='Counterfactual', 
#         line={'color': FCAST_COLOR}
#     ))
#     pdf.update_layout(
#         transition_duration=500, 
#         title={'text': 'Probability density', 'x': .5, 'xanchor': 'center'},
#         legend={'orientation': 'h'},
#     )
#     return pdf