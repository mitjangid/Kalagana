"""Generic root finding on angle-valued functions of time.

The panchang limbs are defined by the instants at which a continuously
increasing angle (e.g. the Moon-Sun elongation) reaches a multiple of some
step (12 deg for tithis, 13 deg 20' for nakshatras).  This module turns that
into a reusable "find when this angle crosses this target" primitive.

Units
-----
* ``func`` must return an angle in *degrees*.
* All time arguments and the returned instant are *Julian Days* (TT).
* Tolerances are expressed in *seconds of time*.
"""

from __future__ import annotations

from typing import Callable

__all__ = [
    "SECONDS_PER_DAY",
    "solve_angle",
    "next_crossing",
    "find_crossing",
    "bisect",
]

SECONDS_PER_DAY = 86400.0


def _wrap_180(x: float) -> float:
    """Wrap an angle into (-180, 180]."""
    return (x + 180.0) % 360.0 - 180.0


def bisect(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1.0 / SECONDS_PER_DAY,
    max_iter: int = 100,
) -> float:
    """Classic bisection on a scalar function ``f`` known to bracket a root.

    ``f(a)`` and ``f(b)`` must have opposite signs.  ``tol`` is the width of
    the accepted bracket in the argument's units (days here).
    """
    fa = f(a)
    fb = f(b)
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        raise ValueError("bisect: interval does not bracket a root")
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = f(m)
        if fm == 0.0 or (b - a) < tol:
            return m
        if fa * fm < 0.0:
            b = m
            fb = fm
        else:
            a = m
            fa = fm
    return 0.5 * (a + b)


def solve_angle(
    func: Callable[[float], float],
    target: float,
    jd_start: float,
    jd_end: float,
    tol_seconds: float = 1.0,
    scan_step: float = 0.25,
) -> "float | None":
    """Find the instant in ``[jd_start, jd_end]`` where ``func`` crosses ``target``.

    Handles the 360 -> 0 degree wraparound.  ``func`` is assumed to be
    increasing (which is the case for all elongations used here); the first
    upward crossing inside the window is returned, or ``None`` if there is
    none.

    ``scan_step`` is the coarse sampling interval in *days*; it must be smaller
    than the time the angle needs to advance 360 deg (0.25 day is safe for the
    Moon-Sun elongation, which moves ~12 deg/day).
    """
    tol = tol_seconds / SECONDS_PER_DAY
    target = target % 360.0

    def g(jd: float) -> float:
        return _wrap_180(func(jd) - target)

    a = jd_start
    ga = g(a)
    # If we are essentially on the crossing at the window start.
    if abs(ga) < 1e-9:
        return a

    x_prev = a
    g_prev = ga
    jd = a + scan_step
    while jd <= jd_end + 1e-12:
        gp = g(jd)
        # An upward crossing of the target shows a sign change from - to +.
        # We ignore the downward wrap (which happens near the anti-target,
        # where g jumps from ~+180 to ~-180), by requiring the bracket to be
        # small enough to be a genuine crossing.
        if abs(g_prev) < 90.0 and abs(gp) < 90.0 and g_prev <= 0.0 < gp:
            return bisect(g, jd - scan_step, jd, tol=max(tol, 1e-9))
        x_prev, g_prev = jd, gp
        jd += scan_step

    # Final check at the window end.
    if g(jd_end) == 0.0:
        return jd_end
    _ = x_prev
    return None


def find_crossing(
    func: Callable[[float], float],
    jd_start: float,
    jd_end: float,
    step: float = 1.0 / 48.0,
    ascending: bool = True,
    tol_seconds: float = 1.0,
) -> "float | None":
    """Find a sign-changing zero of a plain (non-angle) function of time.

    Used for altitude crossings such as sunrise (``ascending=True``) and
    sunset (``ascending=False``).  Returns the first matching instant, or
    ``None`` if the function does not cross zero in the window.
    """
    tol = tol_seconds / SECONDS_PER_DAY
    x0 = jd_start
    f0 = func(x0)
    if f0 == 0.0:
        return x0
    x = jd_start + step
    while x <= jd_end + 1e-12:
        f1 = func(x)
        if f0 == 0.0:
            return x0
        if f0 * f1 < 0.0:
            is_ascending = f1 > f0
            if is_ascending == ascending:
                return bisect(func, x0, x, tol=max(tol, 1e-10))
        x0, f0 = x, f1
        x += step
    return None


def next_crossing(
    func: Callable[[float], float],
    target: float,
    jd_start: float,
    max_days: float = 400.0,
    tol_seconds: float = 1.0,
) -> "float | None":
    """Return the first upward crossing of ``target`` at or after ``jd_start``.

    Searches up to ``max_days`` ahead.  Useful for "next full moon", "next
    Sankranti", etc.
    """
    jd_end = jd_start + max_days
    # A small look-back lets us catch a crossing that lands exactly on start.
    res = solve_angle(func, target, jd_start, jd_end, tol_seconds=tol_seconds)
    if res is None:
        return None
    return res
