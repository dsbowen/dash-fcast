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
</style># Table display

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##dash_fcast.**Table**

<p class="func-header">
    <i>class</i> dash_fcast.<b>Table</b>(<i>id, bins=[0, 0.25, 0.5, 0.75, 1], datatable={}, row_addable=False</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L21">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters and attributes:</b></td>
    <td class="field-body" width="100%"><b>id : <i>str</i></b>
<p class="attr">
    Table identifier.
</p>
<b>bins : <i>list, default=[0, .25, .5, .75, 1]</i></b>
<p class="attr">
    List of bin 'breakpoints'. Bins are contiguous. The first bin starts at <code>bins[0]</code>. The last bin ends at <code>bins[-1]</code>.
</p>
<b>datatable : <i>dict, default={}</i></b>
<p class="attr">
    Keyword arguments passed to the datatable in which table data are displayed.
</p>
<b>row_addable : <i>bool, default=False</i></b>
<p class="attr">
    Indicates that users can add rows to the table.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>get_id</b>(<i>id, type='state'</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L54">[source]</a>
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
    Type of object associated with the table.
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
    <i></i> <b>get_table</b>(<i>self, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L95">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments for <code>dash_table.DataTable</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>data table : <i>dash_table.DataTable</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>get_columns</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L113">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>columns : <i>list of dicts</i></b>
<p class="attr">
    List of column dictionaries in dash_table columns format.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>get_data</b>(<i>self, bins=None, distributions=[], data=[]</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L157">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>bins : <i>list of scalars or None, default=None</i></b>
<p class="attr">
    If <code>None</code> this method uses <code>self.bins</code>.
</p>
<b>distributions : <i>list, default=[]</i></b>
<p class="attr">
    List of distributions like those specified in <code>dash_fcast.distributions</code>.
</p>
<b>data : <i>list of dicts, default=[]</i></b>
<p class="attr">
    Existing data in records format. If a bin matches existing data, that record is returned without updating the distribution pdfs.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>records : <i>list</i></b>
<p class="attr">
    List of records (dictionaries) mapping column ids to data entry.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>register_callbacks</b>(<i>app</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L195">[source]</a>
</p>

Register dash callbacks for table display.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>app : <i>dash.Dash</i></b>
<p class="attr">
    App with which to register the callbacks.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>dump</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L242">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>state_dict : <i>JSON dict</i></b>
<p class="attr">
    Dictionary representing the table state.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>load</b>(<i>cls, state_dict</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L259">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>state_dict : <i>JSON dict</i></b>
<p class="attr">
    Table state dictionary; output from <code>dash_fcast.Table.dump</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>table : <i>dash_fcast.Table</i></b>
<p class="attr">
    Table specified by the table state.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>bar_plot</b>(<i>self, col, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/dash-fcast/blob/master/dash_fcast/table.py#L350">[source]</a>
</p>



<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>col : <i>str</i></b>
<p class="attr">
    ID of the column (distribution) to plot.
</p>
<b>**kwargs : <i></i></b>
<p class="attr">
    Keyword arguments passed to <code>go.Bar</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>bar plot : <i>go.Bar</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>

