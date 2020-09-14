from scipy.stats._continuous_distns import expon_gen, gamma_gen


class reflect():
    def pdf(self, x, *args, **kwargs):
        return super().pdf(-x, *args, **kwargs)

    def logpdf(self, x, *args, **kwargs):
        return super().logpdf(-x, *args, **kwargs)

    def cdf(self, x, *args, **kwargs):
        return 1 - super().cdf(-x, *args, **kwargs)

    # def logcdf(self, x, *args, **kwargs):
    #     return super().logcdf(-x, *args, **kwargs)

    def sf(self, x, *args, **kwargs):
        return 1 - super().sf(-x, *args, **kwargs)

    # def logsf(self, x, *args, **kwargs):
    #     return super().logsf(-x, *args, **kwargs)

    def ppf(self, q, *args, **kwargs):
        return -super().ppf(1-q, *args, **kwargs)

    def isf(self, q, *args, **kwargs):
        return -super().isf(1-q, *args, **kwargs)

    def moment(self, n, *args, **kwargs):
        return -super().moment(n, *args, **kwargs)

    def mean(self, *args, **kwargs):
        return -super().mean(*args, **kwargs)

    def median(self, *args, **kwargs):
        return -super().median(*args, **kwargs)

    # TODO
    # stats
    # entropy
    # expect
    # interval
    # fit
    # fit_loc_scale
    # nnlf
    # support


class rexpon_gen(reflect, expon_gen):
    def __call__(self, loc=0, *args, **kwargs):
        return super().__call__(-loc, *args, **kwargs)

rexpon = rexpon_gen(a=0., name='rexpon')


class rgamma_gen(reflect, gamma_gen):
    def __call__(self, a=1, loc=0, *args, **kwargs):
        return super().__call__(a, -loc, *args, **kwargs)


rgamma = rgamma_gen(a=0, name='rgamma')