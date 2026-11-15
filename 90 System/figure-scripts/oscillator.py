"""Figures for the sample series "Damped and driven oscillations".

    python "90 System/figure-scripts/oscillator.py"

writes four PNGs to Assets/oscillator/:
- damping-regimes.png   free motion in the three damping regimes + energy decay (article 1, Fig. 1)
- resonance.png         steady-state amplitude and phase vs drive frequency (article 2, Fig. 1)
- transient.png         start-up from rest: transient + steady state (article 2, Fig. 2)
- impulse-response.png  impulse response + response to force pulses of three widths (article 3, Fig. 1)

Model (time in units of 1/omega0, so omega0 = 1):
    x'' + 2 gamma x' + omega0^2 x = (F0/m) cos(omega t),   Q = omega0 / (2 gamma).
"""
import numpy as np
import matplotlib.pyplot as plt

import figstyle

figstyle.use()
P = figstyle.PALETTE
W0 = 1.0                       # natural angular frequency
T0 = 2 * np.pi / W0            # natural period


def free(t, g):
    """x(t) for x(0) = 1, x'(0) = 0 and damping rate g (omega0 = 1)."""
    if g < W0:
        wd = np.sqrt(W0**2 - g**2)
        return np.exp(-g * t) * (np.cos(wd * t) + g / wd * np.sin(wd * t))
    if g == W0:
        return (1 + g * t) * np.exp(-g * t)
    b = np.sqrt(g**2 - W0**2)
    sp, sm = -g + b, -g - b
    return (sp * np.exp(sm * t) - sm * np.exp(sp * t)) / (sp - sm)


def steady(w, g):
    """Complex amplitude A = 1 / (omega0^2 - omega^2 + 2 i gamma omega) for F0/m = 1."""
    return 1.0 / (W0**2 - w**2 + 2j * g * w)


def fig_damping():
    fig, (a, b) = figstyle.figure(1, 2, height_mm=58)
    t = np.linspace(0, 4 * T0, 2000)
    for g, name, col in [(0.1, r"underdamped, $\gamma=0.1\,\omega_0$", P["blue"]),
                         (1.0, r"critical, $\gamma=\omega_0$", P["orange"]),
                         (2.5, r"overdamped, $\gamma=2.5\,\omega_0$", P["teal"])]:
        a.plot(t / T0, free(t, g), color=col, label=name)
    g = 0.1
    a.plot(t / T0, np.exp(-g * t), color=P["blue"], lw=0.8, ls=":")
    a.plot(t / T0, -np.exp(-g * t), color=P["blue"], lw=0.8, ls=":")
    a.axhline(0, color="0.6", lw=0.5)
    a.set_xlim(0, 4)
    a.set_ylim(-1.05, 2.15)
    a.set_xlabel(r"time $t/T_0$")
    a.set_ylabel(r"displacement $x/x_0$")
    a.legend(loc="upper right", fontsize=8.5)
    figstyle.panel_label(a, "(a)")

    # energy of the underdamped oscillator for two Q values, with the e^{-2 gamma t} law
    t = np.linspace(0, 6 * T0, 3000)
    for g, col in [(0.1, P["blue"]), (0.025, P["violet"])]:
        wd = np.sqrt(W0**2 - g**2)
        x = free(t, g)
        v = np.exp(-g * t) * (-(g**2 / wd + wd) * np.sin(wd * t))
        e = 0.5 * (v**2 + W0**2 * x**2) / 0.5
        q = W0 / (2 * g)
        b.semilogy(t / T0, e, color=col, label=rf"$Q={q:g}$")
        b.semilogy(t / T0, np.exp(-2 * g * t), color=col, lw=0.8, ls="--")
    b.set_xlim(0, 6)
    b.set_ylim(5e-4, 3)
    b.set_xlabel(r"time $t/T_0$")
    b.set_ylabel(r"energy $E/E_0$")
    b.plot([], [], color="0.35", lw=0.8, ls="--", label=r"$\mathrm{e}^{-2\gamma t}$")
    b.legend(loc="lower left")
    figstyle.panel_label(b, "(b)")
    figstyle.save(fig, "oscillator", "damping-regimes")


def fig_resonance():
    fig, (a, b) = figstyle.figure(1, 2, height_mm=58)
    w = np.linspace(0.001, 2.0, 4000)
    for q, col in [(0.5, P["grey"]), (1, P["teal"]), (2, P["orange"]), (5, P["blue"]), (10, P["violet"])]:
        g = W0 / (2 * q)
        A = steady(w, g)
        a.plot(w / W0, np.abs(A) * W0**2, color=col, label=rf"$Q={q:g}$")
        b.plot(w / W0, np.angle(A, deg=False) * -1 / np.pi, color=col)
    a.set_xlim(0, 2)
    a.set_ylim(0, 11.5)
    a.set_xlabel(r"drive frequency $\omega/\omega_0$")
    a.set_ylabel(r"amplitude $|A|\,m\omega_0^2/F_0$")
    a.legend(loc="upper right")
    figstyle.panel_label(a, "(a)")
    b.axhline(0.5, color="0.6", lw=0.5, ls=":")
    b.axvline(1.0, color="0.6", lw=0.5, ls=":")
    b.set_xlim(0, 2)
    b.set_ylim(-0.03, 1.03)
    b.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    b.set_yticklabels(["0", r"$\pi/4$", r"$\pi/2$", r"$3\pi/4$", r"$\pi$"])
    b.set_xlabel(r"drive frequency $\omega/\omega_0$")
    b.set_ylabel(r"phase lag $\delta$")
    figstyle.panel_label(b, "(b)")
    figstyle.save(fig, "oscillator", "resonance")


def fig_transient():
    fig, ax = figstyle.figure(1, 1, height_mm=55)
    q, w = 10.0, 0.85 * W0
    g = W0 / (2 * q)
    wd = np.sqrt(W0**2 - g**2)
    A = steady(np.array(w), g)
    amp, delta = np.abs(A), -np.angle(A)           # x_ss = amp cos(w t - delta)
    t = np.linspace(0, 16 * T0, 6000)
    xss = amp * np.cos(w * t - delta)
    a0 = -amp * np.cos(delta)                       # x(0) = 0
    b0 = (-amp * w * np.sin(delta) + g * a0) / wd   # x'(0) = 0
    xtr = np.exp(-g * t) * (a0 * np.cos(wd * t) + b0 * np.sin(wd * t))
    ax.plot(t / T0, (xss + xtr) / amp, color=P["blue"], label="full solution from rest")
    ax.plot(t / T0, xss / amp, color=P["orange"], lw=0.9, ls="--", label="steady state")
    ax.plot(t / T0, xtr / amp, color=P["teal"], lw=0.9, label="transient")
    ax.axhline(0, color="0.6", lw=0.5)
    ax.set_xlim(0, 16)
    ax.set_ylim(-2.1, 2.9)
    ax.set_xlabel(r"time $t/T_0$")
    ax.set_ylabel(r"$x/|A|$")
    ax.legend(loc="upper right", ncols=3)
    figstyle.save(fig, "oscillator", "transient")


def impulse(t, g):
    """Impulse response G(t) = e^{-g t} sin(wd t) / wd for t >= 0, zero before (omega0 = 1)."""
    wd = np.sqrt(W0**2 - g**2)
    tp = np.clip(t, 0, None)
    return np.where(t >= 0, np.exp(-g * tp) * np.sin(wd * tp) / wd, 0.0)


def fig_impulse():
    fig, (a, b) = figstyle.figure(1, 2, height_mm=58)
    q = 5.0
    g = W0 / (2 * q)
    wd = np.sqrt(W0**2 - g**2)
    t = np.linspace(-0.5 * T0, 6 * T0, 3000)
    a.plot(t / T0, impulse(t, g) * W0, color=P["blue"], label=rf"$G\,\omega_0$, $Q={q:g}$")
    tp = t[t >= 0]
    env = np.exp(-g * tp) * W0 / wd
    a.plot(tp / T0, env, color=P["blue"], lw=0.8, ls=":", label=r"$\pm\mathrm{e}^{-\gamma t}\,\omega_0/\omega_d$")
    a.plot(tp / T0, -env, color=P["blue"], lw=0.8, ls=":")
    a.axhline(0, color="0.6", lw=0.5)
    a.set_xlim(-0.5, 6)
    a.set_ylim(-1.15, 1.6)
    a.set_xlabel(r"time $t/T_0$")
    a.set_ylabel(r"impulse response $G\,\omega_0$")
    a.legend(loc="upper right")
    figstyle.panel_label(a, "(a)")

    # Gaussian force pulses of equal impulse p (= 1), centred at tc, rms width s T0; x = (1/m) G * F (m = 1).
    dt = T0 / 400
    t = np.arange(0, 8 * T0, dt)
    tc = 2 * T0
    kern = impulse(t, g)
    for s, col in [(0.02, P["blue"]), (0.2, P["orange"]), (0.5, P["teal"])]:
        sig = s * T0
        f = np.exp(-0.5 * ((t - tc) / sig) ** 2) / (np.sqrt(2 * np.pi) * sig)
        x = np.convolve(f, kern)[: len(t)] * dt
        b.plot(t / T0, x * W0, color=col, label=rf"$\sigma={s:g}\,T_0$")
    b.axhline(0, color="0.6", lw=0.5)
    b.set_xlim(0, 8)
    b.set_ylim(-1.15, 1.6)
    b.set_xlabel(r"time $t/T_0$")
    b.set_ylabel(r"displacement $x\,m\omega_0/p$")
    b.legend(loc="upper right")
    figstyle.panel_label(b, "(b)")
    figstyle.save(fig, "oscillator", "impulse-response")


if __name__ == "__main__":
    fig_damping()
    fig_resonance()
    fig_transient()
    fig_impulse()
