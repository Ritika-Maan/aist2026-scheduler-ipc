"""Small statistics helpers (no SciPy dependency): Student-t quantile and a t-interval."""
import math


def _betacf(a, b, x, max_iter=300, eps=3e-14):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * _betainc(df / 2.0, 0.5, x)
    return 1.0 - p if t > 0 else p


def t_crit(df, conf=0.95):
    """Two-sided critical value: P(|T| <= t_crit) = conf for T ~ t(df)."""
    if df < 1:
        return float("nan")
    target = 0.5 + conf / 2.0
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < target:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def t_interval(values, conf=0.95):
    """(n, mean, sd, ci_lo, ci_hi). sd uses ddof=1. n < 2 -> sd/ci are NaN."""
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        nan = float("nan")
        return 0, nan, nan, nan, nan
    mean = sum(vals) / n
    if n < 2:
        return n, mean, float("nan"), float("nan"), float("nan")
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    half = t_crit(n - 1, conf) * sd / math.sqrt(n)
    return n, mean, sd, mean - half, mean + half
