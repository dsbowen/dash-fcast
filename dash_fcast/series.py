import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV


class Series(np.ndarray):
    def __new__(cls, name, array):
        return np.sort(np.asarray(array).view(cls))

    def __init__(self, name, array):
        self.name = name
        self.F_x = np.cumsum(np.ones(self.shape) / self.shape[0])

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)

    def __round__(self, *args, **kwargs):
        return round(float(self), *args, **kwargs)

    def quantile(self, q):
        return np.quantile(self, q)

    def pdf_plot(self, lb=None, ub=None, num=100, *args, **kwargs):
        lb = self[0] if lb is None else lb
        ub = self[-1] if ub is None else ub
        x = np.linspace(lb, ub, num)
        params = {'bandwidth': np.logspace(-1, 1, 20)}
        grid = GridSearchCV(KernelDensity(), params)
        grid.fit(self.reshape(-1, 1))
        f_x = np.exp(grid.best_estimator_.score_samples(x.reshape(-1, 1)))
        return go.Scatter(x=x, y=f_x, name=self.name, *args, **kwargs)

    def cdf_plot(self, *args, **kwargs):
        return go.Scatter(x=self, y=self.F_x, name=self.name, *args, **kwargs)