import numpy as np
import plotly.graph_objects as go

def bins_bar_plot(records, col, *args, **kwargs):
    x, y, width = [], [], []
    for record in records:
        min_, max_ = float(record['Bin min']), float(record['Bin max'])
        x.append((min_ + max_)/2)
        width.append(max_ - min_)
        y.append(float(record[col])/width[-1])
    y = _normalize(y, width)
    return go.Bar(x=x, y=y, width=width, name=col, *args, **kwargs)

def quantiles_bar_plot(records, col, *args, **kwargs):
    x, y, width = [], [], []
    for i in range(len(records)-1):
        x_i, x_j = float(records[i][col]), float(records[i+1][col])
        q_i = float(records[i]['Percentile'])
        q_j = float(records[i+1]['Percentile'])
        x.append((x_i + x_j)/2)
        width.append(x_j - x_i)
        y.append((q_j - q_i) / width[-1])
    y = _normalize(y, width)
    return go.Bar(x=x, y=y, width=width, name=col, *args, **kwargs)

def _normalize(y, width):
    y, width = np.array(y), np.array(width)
    return y / (width.T @ y)