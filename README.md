Dash-Forecast allows you to easily build forecasting dashboards.

## Why Dash-Forecast

Judgment and decision making research shows that <a href="http://journal.sjdm.org/13/131029/jdm131029.pdf" target="_blank">visual tools are an easy and effective way to boost forecasting accuracy</a>. Dash-Forecast is a high-level API for creating beautiful forecasting visualizations and statistical summaries.

## Installation

```
$ pip install dash-fcast
```

## Quickstart

In just a few lines of code, we'll create an app that gives you:

1. An intuitive 'bounds and moments' forecast elicitation
2. An editable data table representation of the forecast
3. Probability density function and cumulative distribution function line plots of the forecast
4. A bar plot of the data table

Create a file `app.py`:

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
    html.Br(),
    dist.Moments(id='Forecast'),
    html.Br(),
    fcast.Table(
        id='Table', 
        datatable={'editable': True, 'row_deletable': True},
        row_addable=True
    ),
    html.Div(id='graphs')
], className='container')

dist.Moments.register_callbacks(app)
fcast.Table.register_callbacks(app)

@app.callback(
    Output('graphs', 'children'),
    [
        Input(dist.Moments.get_id('Forecast'), 'children'),
        Input(fcast.Table.get_id('Table'), 'children')
    ]
)
def update_graphs(dist_state, table_state):
    distribution = dist.Moments.load(dist_state)
    table = fcast.Table.load(table_state)
    pdf = go.Figure([distribution.pdf_plot(), table.bar_plot('Forecast')])
    pdf.update_layout(transition_duration=500, title='PDF')
    cdf = go.Figure([distribution.cdf_plot()])
    cdf.update_layout(transition_duration=500, title='CDF')
    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
    app.run_server(debug=True)
```

Run your application with:

```bash
$ python app.py
```

Open your browser and navigate to <http://localhost:8050/>.

## Citation

```
@software{bowen2020dash-fcast,
  author = {Dillon Bowen},
  title = {Dash-Forecast},
  url = {https://dsbowen.github.io/dash-fcast/},
  date = {2020-09-11},
}
```

## License

Users must cite this package in any publications which use it.

It is licensed with the MIT [License](https://github.com/dsbowen/dash-fcast/blob/master/LICENSE).

## Acknowledgements

The following collaborators deserve special acknowledgement:

- David Melgin, for the bounds and moments elicitation
- Ezra Karger, whose non-parametric elicitation methods helped inspire my 'tabular elicitation'
- Sarah Reed, for feedback on the front-end design

I would also like to thank the Tetlock Lab, whose weekly presentations inspired various aspects of this package, including Zachary Jacobs' and Ian Lustick's 'first approximation algorithm', Scott Page's multi-model thinking, and Annie Duke's presentation on intuitively eliciting predictions.