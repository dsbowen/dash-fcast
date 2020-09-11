<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

<link rel="stylesheet" href="https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css" type="text/css" />

<style>
    a.src-href {
        float: right;
    }
    p.attr {
        margin-top: 0.5em;
        margin-left: 1em;
    }
    p.func-header {
        background-color: gainsboro;
        border-radius: 0.1em;
        padding: 0.5em;
        padding-left: 1em;
    }
    table.field-table {
        border-radius: 0.1em
    }
</style># Tabular distribution

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>

####Examples

In `app.py`:

```python
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
    dist.Table(
        id='Forecast',
        datatable={'editable': True, 'row_deletable': True},
        row_addable=True,
        smoother=True
    ),
    html.Div(id='graphs')
], className='container')

dist.Table.register_callbacks(app)

@app.callback(
    Output('graphs', 'children'),
    [Input(dist.Table.get_id('Forecast'), 'children')]
)
def update_graphs(dist_state):
    distribution = dist.Table.load(dist_state)
    pdf = go.Figure([distribution.pdf_plot(), distribution.bar_plot()])
    pdf.update_layout(transition_duration=500, title='PDF')
    cdf = go.Figure([distribution.cdf_plot()])
    cdf.update_layout(transition_duration=500, title='CDF')
    return [dcc.Graph(figure=pdf), dcc.Graph(figure=cdf)]

if __name__ == '__main__':
    app.run_server(debug=True)
```

Run the app with:

```bash
$ python app.py
```

Open your browser and navigate to <http://localhost:8050/>.

##dash_fcast.distributions.**Table**

<p class="func-header">
    <i>class</i> dash_fcast.distributions.<b>Table</b>(<i>id, bins=[0, 0.25, 0.5, 0.75, 1], pdf=[0.25, 0.25, 0.25, 0.25], datatable={}, row_addable=False, smoother=False, *args, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L72">[source]</a>
</p>

Tabular distribution elicitation. Subclasses `smoother.Smoother`.
<https://dsbowen.github.io/smoother/>.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters and attributes:</b></td>
    <td class="field-body" width="100%"><b>id : <i>str, default</i></b>
<p class="attr">
    Distribution identifier.
</p>
<b>bins : <i>list of scalars, default=[0, .25, .5, .75, 1]</i></b>
<p class="attr">
    List of 'break points' for the bins. The first bin starts at <code>bins[0]</code>. The last bin ends at <code>bins[-1]</code>.
</p>
<b>pdf : <i>list of float, default=[.25, .25, .25, .25]</i></b>
<p class="attr">
    Probability density function. This is the amount of probability mass in each bin. Must sum to 1 and <code>len(pdf)</code> must be <code>len(bins)-1</code>.
</p>
<b>datatable : <i>dict, default={}</i></b>
<p class="attr">
    Keyword arguments for the datatable associated with the table distribution. See <a href="https://dash.plotly.com/datatable">https://dash.plotly.com/datatable</a>.
</p>
<b>row_addable : <i>bool, default=False</i></b>
<p class="attr">
    Indicates whether the forecaster can add rows.
</p>
<b>smoother : <i>bool, default=False</i></b>
<p class="attr">
    Indicates whether to use a smoother for interpolation.
</p>
<b>*args, **kwargs : <i></i></b>
<p class="attr">
    Arguments and keyword arguments passed to <code>super().__init__</code>.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>get_id</b>(<i>id, type='state'</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L115">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>id : <i>str</i></b>
<p class="attr">
    
</p>
<b>type : <i>str, default='state'</i></b>
<p class="attr">
    Type of object associated with the moments distribution.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>id dictionary : <i>dict</i></b>
<p class="attr">
    Dictionary identifier.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>elicitation</b>(<i>self, bins=[0, 0.25, 0.5, 0.75, 1], pdf=[0.25, 0.25, 0.25, 0.25], datatable={}, row_addable=False</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L143">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>bins : <i>list of scalars or numpy.array, default=[0, .25, .5, .75, 1]</i></b>
<p class="attr">
    
</p>
<b>pdf : <i>list of scalars or numpy.array, default=[.25, .25, .25, .25]</i></b>
<p class="attr">
    
</p>
<b>datatable : <i>dict, default={}</i></b>
<p class="attr">
    
</p>
<b>row_addable : <i>bool, default=False</i></b>
<p class="attr">
    
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>elicitation elements : <i>list of dash elements</i></b>
<p class="attr">
    Dash elements used to elicit the distribution.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>get_columns</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L186">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>columns : <i>list of dict</i></b>
<p class="attr">
    List of dictionaries specifying the datatable columns. See <a href="https://dash.plotly.com/datatable">https://dash.plotly.com/datatable</a>,
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>get_data</b>(<i>self, bins=None, pdf=None</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L220">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>bins : <i>list of float or numpy.array or None, default=None</i></b>
<p class="attr">
    If <code>None</code>, use <code>self.bins</code>.
</p>
<b>pdf : <i>list of float or numpy.array or None, default=None</i></b>
<p class="attr">
    If <code>None</code>, use <code>self.pdf</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>records : <i>list of dict</i></b>
<p class="attr">
    Datatable data in records format.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>register_callbacks</b>(<i>app</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L251">[source]</a>
</p>

Register dash callbacks for table distributions.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>app : <i>dash.Dash</i></b>
<p class="attr">
    App with which to register callbacks.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>fit</b>(<i>self, bins=None, pdf=None, derivative=2</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L286">[source]</a>
</p>

Fit the smoother given masses constraints.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>bins : <i>list of float or numpy.array</i></b>
<p class="attr">
    Ordered list of bin break points. If <code>None</code>, use <code>self.bins</code>.
</p>
<b>pdf : <i>list of float or numpy.array</i></b>
<p class="attr">
    Probability density function. This is the amount of probability mass in each bin. Must sum to 1 and <code>len(pdf)</code> should be <code>len(bins)-1</code>. If <code>None</code>, use <code>self.pdf</code>.
</p>
<b>derivative : <i>int, default=2</i></b>
<p class="attr">
    Deriviate of the derivative smoothing function to maximize. e.g. <code>2</code> means the smoother will minimize the mean squaure second derivative.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>self : <i></i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>dump</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L319">[source]</a>
</p>

Dump the table distribution state dictionary in JSON format.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>state : <i>dict, JSON</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>load</b>(<i>cls, state_dict</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L339">[source]</a>
</p>

Load a table distribution from its state dictionary.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>state_dict : <i>dict</i></b>
<p class="attr">
    Output of <code>Table.dump</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>table : <i><code>Table</code></i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>pdf_plot</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L430">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments for <code>go.Scatter</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>scatter : <i>go.Scatter.</i></b>
<p class="attr">
    Scatter plot of the pdf.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>cdf_plot</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L455">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments for <code>go.Scatter</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>scatter : <i>go.Scatter</i></b>
<p class="attr">
    Scatter plot of the cdf.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>bar_plot</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\table.py#L473">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments for <code>go.Bar</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>bar plot : <i>go.Bar</i></b>
<p class="attr">
    Bar plot of the pdf in the datatable.
</p></td>
</tr>
    </tbody>
</table>

