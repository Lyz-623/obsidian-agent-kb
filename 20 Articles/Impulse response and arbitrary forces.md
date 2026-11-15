---
type: article
series: "[[1 Damped and driven oscillations]]"
series_no: 1
seq: 3
summary: 'How a damped oscillator answers any force, not just a sinusoid: the response to a single kick, the superposition integral built from it, its link to the steady-state amplitude, and why short pulses ring while slow pushes do not'
sections: ["The response to a kick", "Any force as a sum of kicks"]
kinds: [Definition, Explanation, Proposition, Derivation, Caution, Conclusion]
terms: ["[[Impulse response]]", "[[Response function]]", "[[Steady-state response]]", "[[Natural frequency]]", "[[Damping rate]]", "[[Quality factor]]"]
sources: ["[[French1971]]", "[[Landau1976]]"]
figures: 1
equations: 4
words: 1411
cssclasses: [card-note, article-note]
---
Real forces are rarely pure sinusoids: a hammer strikes a bell, a gust hits a bridge, a laser pulse kicks a molecule. Because the oscillator equation is linear, one response is enough to predict all the others, namely the motion after a single, infinitely short kick. This article asks what that response is, how any force is assembled from kicks, and how the result connects to the steady-state amplitude found for a periodic drive ([[French1971|French 1971]]; [[Landau1976|Landau and Lifshitz 1976]]).

## The response to a kick

### An impulsive force

A force that acts for a time much shorter than the period changes the velocity before the spring has had time to move the mass. What matters is then only its time integral, the impulse $p=\int F\,\mathrm{d}t$.

> [!definition] Definition — Impulse response
> For the oscillator of [[Driven oscillations and resonance#^def-drv-eom|“Driven oscillations and resonance” Eq. (1)]] driven by a general force, $\ddot x+2\gamma\dot x+\omega_0^2x=F(t)/m$, the **[[Impulse response]]** $G(t)$ is the motion after a unit kick $F=m\,\delta(t)$ applied to the mass at rest. For light damping, $\gamma<\omega_0$,
>
> $$
> G(t)=\begin{cases}0, & t<0,\\[2pt] \mathrm{e}^{-\gamma t}\,\dfrac{\sin\omega_d t}{\omega_d}, & t\ge 0,\end{cases}\qquad \omega_d=\sqrt{\omega_0^2-\gamma^2}. \tag{1}
> $$
>
> A kick of impulse $p$ produces $x(t)=(p/m)\,G(t)$.

^def-imp-green

Equation (1) is free motion with one particular pair of initial conditions. Why these, and why does the response vanish before the kick?

> [!derivation] Derivation — From the kick to the initial conditions
> **Step 1: integrate across the kick.** Integrate the equation of motion from $t=-\epsilon$ to $t=+\epsilon$. The displacement stays finite, so the $\gamma$ and $\omega_0^2$ terms contribute terms of order $\epsilon$, while $\int\ddot x\,\mathrm{d}t=\dot x(+\epsilon)-\dot x(-\epsilon)$:
>
> $$
> \dot x(0^+)-\dot x(0^-)=\frac{1}{m}\int_{-\epsilon}^{\epsilon}m\,\delta(t)\,\mathrm{d}t=1,\qquad x(0^+)=x(0^-)=0 .
> $$
>
> **Step 2: free motion afterwards.** For $t>0$ the force is zero, so $x$ is the underdamped solution of [[Free damped oscillations#^pro-free-under|“Free damped oscillations” Eq. (3)]]. The conditions $x(0^+)=0$, $\dot x(0^+)=1$ select $\mathrm{e}^{-\gamma t}\sin(\omega_d t)/\omega_d$.
>
> **Step 3: causality.** Before the kick the mass was at rest and nothing acted on it, so $G=0$ for $t<0$.

^der-imp-green

### What the impulse response contains

The kick response looks like nothing more than a special case of free motion. Why should one special case be enough to describe the oscillator under every possible force?

> [!explain] Explanation — Two numbers again
> - The oscillation inside $G$ runs at the damped frequency $\omega_d$ and the envelope decays at the **[[Damping rate|damping rate]]** $\gamma$, exactly as in free motion: a kick is just a way to start the oscillator.
> - The first maximum, a quarter period after the kick, lies just below $p/(m\omega_0)$; the ringing lasts a few times $1/\gamma=2Q/\omega_0$, so a high-$Q$ bell rings for about $Q$ cycles.
> - ***$G$ depends only on $\omega_0$ and $\gamma$, not on the force.*** Whatever the force, the oscillator itself enters only through $G$.

^exp-imp-meaning

That last point becomes a formula once a force is seen as a train of kicks, each launching its own copy of $G$.

## Any force as a sum of kicks

### The superposition integral

Any force history can be cut into thin slices, each of which acts as a small kick $F(t')\,\mathrm{d}t'$ at time $t'$. Linearity lets the responses to all slices simply add.

> [!proposition] Proposition — Response to an arbitrary force
> Starting from rest in the distant past, the oscillator driven by any force $F(t)$ moves as
>
> $$
> x(t)=\frac{1}{m}\int_{-\infty}^{t}G(t-t')\,F(t')\,\mathrm{d}t' . \tag{2}
> $$
>
> **The displacement now is a weighted memory of the force in the past, with weights that ring at $\omega_d$ and fade at the rate $\gamma$.**

^pro-imp-superpose

The upper limit $t$ in Eq. (2) is causality written into the formula: forces that have not yet acted have no effect. For a sinusoidal drive the integral must reproduce the known steady state; checking this exposes how the time and frequency descriptions are related.

> [!proposition] Proposition — The response function is the transform of $G$
> For $F(t)=F_0\,\mathrm{e}^{\mathrm{i}\omega t}$, Eq. (2) gives $x(t)=(F_0/m)\,\chi(\omega)\,\mathrm{e}^{\mathrm{i}\omega t}$ with the **[[Response function]]**
>
> $$
> \chi(\omega)=\int_0^{\infty}G(\tau)\,\mathrm{e}^{-\mathrm{i}\omega\tau}\,\mathrm{d}\tau=\frac{1}{\omega_0^2-\omega^2+2\mathrm{i}\gamma\omega} . \tag{3}
> $$
>
> ==The complex amplitude of the steady state is the Fourier transform of the impulse response==, so $A(\omega)=(F_0/m)\,\chi(\omega)$ reproduces [[Driven oscillations and resonance#^pro-drv-amp|“Driven oscillations and resonance” Eq. (2)]].

^pro-imp-chi

> [!derivation] Derivation — Transforming the decaying sine
> **Step 1: change variable.** With $\tau=t-t'$, Eq. (2) becomes $x=(F_0/m)\,\mathrm{e}^{\mathrm{i}\omega t}\int_0^\infty G(\tau)\,\mathrm{e}^{-\mathrm{i}\omega\tau}\,\mathrm{d}\tau$, which defines $\chi(\omega)$.
>
> **Step 2: integrate.** Put $s=\gamma+\mathrm{i}\omega$; since $\int_0^\infty \mathrm{e}^{-s\tau}\sin(\omega_d\tau)\,\mathrm{d}\tau=\omega_d/(s^2+\omega_d^2)$ for $\operatorname{Re}s>0$,
>
> $$
> \chi(\omega)=\frac{1}{(\gamma+\mathrm{i}\omega)^2+\omega_0^2-\gamma^2}=\frac{1}{\omega_0^2-\omega^2+2\mathrm{i}\gamma\omega} .
> $$
>
> **Step 3: read off.** This is the complex amplitude per unit $F_0/m$ found for the **[[Steady-state response]]**; the damping $\gamma>0$ makes the integral converge, which is why only the steady state survives.

^der-imp-chi

### Short pulses and slow pushes

When does a pulse of finite length still act as a kick? Equation (2) answers it: the mass rings after the pulse only to the extent that the force contains the frequency $\omega_d$.

> [!proposition] Proposition — Ringing after a pulse
> After a force pulse has ended, a lightly damped oscillator rings at $\omega_d$ with amplitude
>
> $$
> x_{\text{ring}}\approx\frac{|\tilde F(\omega_d)|}{m\,\omega_d},\qquad \tilde F(\omega)=\int F(t)\,\mathrm{e}^{-\mathrm{i}\omega t}\,\mathrm{d}t, \tag{4}
> $$
>
> valid when the pulse is much shorter than $1/\gamma$. **A pulse much shorter than $T_0$ has $\tilde F(\omega_d)\approx p$ and acts as a kick; a push much slower than $T_0$ has almost no component at $\omega_d$ and leaves no ringing behind.**

^pro-imp-ring

> [!figure] **Fig. 1** Response of a damped oscillator with $Q=5$ to impulsive forces. (a) Impulse response $G$ of Eq. (1) in units of $1/\omega_0$, with the envelope $\pm\mathrm{e}^{-\gamma t}\,\omega_0/\omega_d$ dotted; (b) displacement computed from Eq. (2) for Gaussian force pulses of equal impulse $p$, centred at $t=2T_0$, with rms widths $\sigma=0.02\,T_0$ (blue), $0.2\,T_0$ (orange) and $0.5\,T_0$ (green).
> ![[impulse-response.png|720]]

^fig-imp-pulses

Fig. 1(a) is the response to an ideal kick: the mass starts moving at once with velocity $p/m$, so $G$ rises from zero with finite slope, then rings at $\omega_d$ inside the dotted envelope, exactly the free motion of Eq. (1). Fig. 1(b) shows what a finite pulse duration changes: the shortest pulse is still effectively a kick and reproduces the curve of Fig. 1(a) delayed to $t=2T_0$; the $0.2\,T_0$ pulse leaves ringing reduced to $\mathrm{e}^{-\omega_d^2\sigma^2/2}\approx0.46$ of it, as Eq. (4) predicts for a Gaussian; the $0.5\,T_0$ pulse is slower than one oscillation, so it only pushes the mass aside and lets it return, with almost no ringing left. A pulse excites the oscillator only if it contains frequency components near $\omega_d$, which is the time-domain face of the resonance curve.

> [!warning] Caution — Linear only
> Equations (2) to (4) rest on superposition. They fail once the amplitude is large enough for the restoring force or the drag to stop being linear, for example a pendulum swinging through large angles; then the response to two kicks is not the sum of the responses.

^warn-imp-linear

> [!conclusion] Conclusion — One function for every force
> The impulse response $G$, fixed by $\omega_0$ and $\gamma$ alone, predicts the motion under any force through Eq. (2), and its Fourier transform $\chi(\omega)$ is the steady-state amplitude of a periodic drive. ==Time-domain ringing and frequency-domain resonance are the same information==: a sharp resonance of width $\omega_0/Q$ means a long ringing of about $Q$ cycles.

^con-imp-summary

> [!series] Damped and driven oscillations
> [[Driven oscillations and resonance]]
>
> [[Home]]
>
> [[1 Damped and driven oscillations|Series map]]
