from dash_fcast.distributions import Moments

dist = Moments('tmp')
dist.fit(-2, mean=0, std=.5)
print('type', dist._dist_type)
print('dist', dist._dist)
print('mean', dist._dist.mean())
print('std', dist._dist.std())

# from scipy.stats import gamma

# def test(mean, std):
#     dist = gamma((mean/std)**2, 0, std**2)
#     if mean != dist.mean() or std != dist.std():
#         print()
#         print('input mean is', mean)
#         print('input std is', std)
#         print('dist mean is', dist.mean())
#         print('dist std is', dist.std())

# for i in range(3):
#     mean = 2**i
#     for j in range(3):
#         std = 2**-j
#         test(mean, std)

# from smoother import Smoother, MomentConstraint

# def test(mean, std):
#     mean_const = MomentConstraint(mean, degree=1)
#     std_const = MomentConstraint(std, degree=2, type_='central', norm=True)
#     ub = mean + 3*std
#     dist.fit(lb, ub, [mean_const, std_const])
#     print()
#     print('input mean', mean)
#     print('input std', std)
#     print('dist mean', dist.mean())
#     print('dsit std', dist.std())

# dist = Smoother()

# lb = 0

# for i in range(3):
#     mean = 2**i
#     for j in range(3):
#         std = 2**-j
#         test(mean, std)