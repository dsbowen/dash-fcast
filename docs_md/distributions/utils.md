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
</style># Distributions

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##dash_fcast.distributions.**load_distributions**

<p class="func-header">
    <i>def</i> dash_fcast.distributions.<b>load_distributions</b>(<i>dist_states</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\__init__.py#L15">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>dist_states : <i>list of JSON dictionaries</i></b>
<p class="attr">
    List of distribution state dictionaries.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>distributions : <i>list of distributions</i></b>
<p class="attr">
    List of distributions recovered from the state dictionaries.
</p></td>
</tr>
    </tbody>
</table>



##dash_fcast.distributions.**load_distribution**

<p class="func-header">
    <i>def</i> dash_fcast.distributions.<b>load_distribution</b>(<i>dist_state</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/distributions\__init__.py#L29">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>dist_state : <i>JSON dictionary</i></b>
<p class="attr">
    Distribution state dictionary.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>distribution : <i></i></b>
<p class="attr">
    Distribution recovered from the state dictionary.
</p></td>
</tr>
    </tbody>
</table>

