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
</style># Moments distribution

This elicitation method asks forecasters to input the 'bounds and moments' of
the distribution. (Specifically, the moments are the mean and standard
deviation). It then fits a distribution based on these inputs:

1. Lower bound and upper bound => uniform
2. Lower bound and mean or standard deviation => exponential
3. Upper bound and mean or standard deviation => 'reflected' exponential
4. Mean and standard deviation => Gaussian
5. Otherwise => non-parametric maximum entropy distribution. See
<https://dsbowen.github.io/smoother/>.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>

####Examples

In `app.py`:

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

Run the app with:

```bash
$ python app.py
```

Open your browser and navigate to <http://localhost:8050/>.

##dash_fcast.distributions.**Moments**

<p class="func-header">
    <i>class</i> dash_fcast.distributions.<b>Moments</b>(<i>id, lb=0, ub=1, mean=None, std=None, *args, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L88">[source]</a>
</p>

Distribution generated from moments elicitation.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>id : <i>str</i></b>
<p class="attr">
    Distribution identifier.
</p>
<b>lb : <i>scalar or None, default=0</i></b>
<p class="attr">
    Lower bound of the distribution. <em>F(x)=0</em> for all <em>x&lt;lb</em>. If <code>None</code>, the distribution has no lower bound.
</p>
<b>ub : <i>scalar or None, default=1</i></b>
<p class="attr">
    Upper bound of the distribution. <em>F(x)=1</em> for all <em>x&gt;ub</em>. If <code>None</code>, the distribution has no upper bound.
</p>
<b>mean : <i>scalar or None, default=None</i></b>
<p class="attr">
    Mean of the distribution. If <code>None</code>, the mean is inferred as halfway between the lower and upper bound.
</p>
<b>std : <i>scalar or None, default=None</i></b>
<p class="attr">
    Standard deviation of the distribution. If <code>None</code>, the standard deviation is inferred as the standard deviation which maximizes entropy.
</p>
<b>*args, **kwargs : <i></i></b>
<p class="attr">
    Arguments and keyword arguments are passed to the smoother constructor.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Attributes:</b></td>
    <td class="field-body" width="100%"><b>id : <i>str</i></b>
<p class="attr">
    Set from the <code>id</code> parameter.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>get_id</b>(<i>id, type='state'</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L129">[source]</a>
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
    <i></i> <b>elicitation</b>(<i>self, lb=0, ub=1, mean=None, std=None</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L154">[source]</a>
</p>

Creates the layout for eliciting bounds and moments. Parameters for
this method are analogous to the constructor parameters.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>lb : <i>scalar, default=0</i></b>
<p class="attr">
    
</p>
<b>ub : <i>scalar, default=1</i></b>
<p class="attr">
    
</p>
<b>mean : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p>
<b>std : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p>
<b>decimals : <i>int, default=2</i></b>
<p class="attr">
    Number of decimals to which the recommended maximum standard deviation is rounded.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>layout : <i>list of dash elements.</i></b>
<p class="attr">
    Elicitation layout.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>register_callbacks</b>(<i>app, decimals=2</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L212">[source]</a>
</p>

Register dash callbacks for moments distributions.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>app : <i>dash.Dash</i></b>
<p class="attr">
    App with which to register callbacks.
</p>
<b>decimals : <i>int, default=2</i></b>
<p class="attr">
    Number of decimals to which to round the standard deviation placeholder.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>fit</b>(<i>self, lb=None, ub=None, mean=None, std=None</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L284">[source]</a>
</p>

Fit the smoother given bounds and moments constraints. Parameters are
analogous to those of the constructor.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>lb : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p>
<b>ub : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p>
<b>mean : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p>
<b>std : <i>scalar or None, default=None</i></b>
<p class="attr">
    
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>self : <i>dash_fcast.distributions.Moments</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>dump</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L371">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>state dictionary : <i>str (JSON)</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>load</b>(<i>cls, state_dict</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L389">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>state_dict : <i>str (JSON)</i></b>
<p class="attr">
    Moments distribution state dictionary (output of <code>Moments.dump</code>).
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>distribution : <i>dash_fcast.distributions.Moments</i></b>
<p class="attr">
    Moments distribution specified by the state dictionary.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>mean</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L414">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>std</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L417">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>pdf</b>(<i>self, x</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L420">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>cdf</b>(<i>self, x</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L423">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>ppf</b>(<i>self, q</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L426">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>pdf_plot</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L429">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments passed to <code>go.Scatter</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>scatter : <i>go.Scatter</i></b>
<p class="attr">
    Scatter plot of the probability density function.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>cdf_plot</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\moments.py#L452">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>** kwargs : <i></i></b>
<p class="attr">
    Keyword arguments passed to <code>go.Scatter</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>scatter : <i>go.Scatter</i></b>
<p class="attr">
    Scatter plot of the cumulative distribution function.
</p></td>
</tr>
    </tbody>
</table>

