"""Synthesised sound effects (no third-party samples, no rights issues)."""
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, attack=0.005, release=None, curve=4.0):
    t = np.arange(n) / SR
    d = n / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    r = np.exp(-curve * t / d) if release is None else np.clip((d - t) / release, 0, 1)
    return a * r


def _lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha[i] * (v - acc) if np.ndim(alpha) else alpha * (v - acc)
        y[i] = acc
    return y


def _norm(x, peak):
    return x / (np.abs(x).max() + 1e-9) * peak


def whoosh(d=0.45, peak=0.5, rising=True):
    n = int(SR * d)
    noise = rng.standard_normal(n)
    sweep = np.linspace(0.02, 0.35, n) if rising else np.linspace(0.35, 0.02, n)
    x = _lowpass(noise, sweep)
    x = x - _lowpass(x, 0.01)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** (0.6 if rising else 1.6)) ** 2
    return _norm(x * env, peak)


def pop(f0=900, f1=300, d=0.09, peak=0.45):
    t = _t(d)
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return _norm(x * _env(len(t), 0.002, curve=7), peak)


def tick(peak=0.18):
    return pop(2400, 1500, 0.03, peak)


def impact(peak=0.9):
    t = _t(0.7)
    f = 45 + 110 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    n = rng.standard_normal(len(t))
    crack = _lowpass(n, 0.25) * np.exp(-t * 35)
    return _norm(sub + 0.5 * crack, peak)


def ding(peak=0.45, base=1318.5):
    t = _t(1.4)
    x = sum(a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * (3 + 2 * m))
            for m, a in ((1, 1), (2.01, 0.5), (3.02, 0.25), (1.5, 0.35)))
    return _norm(x * _env(len(t), 0.002, curve=1), peak)


def sparkle(peak=0.3):
    out = np.zeros(int(SR * 0.6))
    for i, f in enumerate((1568, 2093, 2637, 3136)):
        s = int(i * 0.06 * SR)
        t = _t(0.3)
        tone = np.sin(2 * np.pi * f * t) * np.exp(-t * 14)
        out[s:s + len(t)] += tone[: len(out) - s]
    return _norm(out, peak)


def fail(peak=0.45):
    """Descending 'wah wah' trombone-ish buzz."""
    out = []
    for f, d in ((392, 0.22), (370, 0.22), (349, 0.22), (330, 0.55)):
        t = _t(d)
        vib = 1 + 0.015 * np.sin(2 * np.pi * 6 * t) * (t > 0.2)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x = np.sign(np.sin(ph)) * 0.4 + np.sin(ph) + 0.5 * np.sin(2 * ph)
        x = _lowpass(x, 0.12)
        out.append(x * _env(len(t), 0.01, release=0.06))
    return _norm(np.concatenate(out), peak)


def riser(d=0.6, peak=0.25):
    t = _t(d)
    f = 200 * (8 ** (t / d))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * rng.standard_normal(len(t))
    return _norm(x * (t / d) ** 2, peak)


def bonk(peak=0.5):
    t = _t(0.25)
    f = 600 * np.exp(-t * 9) + 140
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return _norm(x * np.exp(-t * 16), peak)


def scratch(peak=0.35):
    t = _t(0.35)
    rate = np.sin(2 * np.pi * 5.5 * t)
    n = _lowpass(rng.standard_normal(len(t)), 0.08 + 0.3 * np.abs(rate))
    return _norm(n * np.abs(rate) * _env(len(t), 0.005, curve=3), peak)
