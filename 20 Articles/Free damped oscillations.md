---
type: article
series: "[[1 Damped and driven oscillations]]"
series_no: 1
seq: 1
summary: 'How a mass on a spring with linear drag moves on its own: the characteristic roots, the three damping regimes, and the quality factor that measures how slowly the energy leaks away'
sections: ["The equation of motion", "Three regimes of damping", "Energy decay and the quality factor"]
kinds: [Definition, Explanation, Proposition, Derivation, Caution, Conclusion]
terms: ["[[Natural frequency]]", "[[Damping rate]]", "[[Critical damping]]", "[[Quality factor]]"]
sources: ["[[French1971]]", "[[Landau1976]]"]
figures: 1
equations: 4
words: 1476
cssclasses: [card-note, article-note]
---
A pendulum, a tuning fork, an LC circuit and a molecule's bond all share one behaviour: pushed away from equilibrium, they swing back, overshoot and slowly settle. Almost all of it is captured by a single linear equation with two parameters, a restoring rate and a damping rate. This article asks how the motion follows from those two numbers, when the oscillation disappears altogether, and how to measure "how good" an oscillator is ([[French1971|French 1971]]; [[Landau1976|Landau and Lifshitz 1976]]).

## The equation of motion

### Restoring force and drag

Take a mass $m$ on a spring of stiffness $k$, moving through a medium that resists the motion with a force proportional to the velocity. Newton's second law gives one second-order equation for the displacement $x(t)$.

> [!definition] Definition — Damped harmonic oscillator
> With a restoring force $-kx$ and a linear drag force $-b\dot x$, Newton's law $m\ddot x=-kx-b\dot x$ becomes, after dividing by $m$,
>
> $$
> \ddot x+2\gamma\,\dot x+\omega_0^2\,x=0,\qquad \omega_0^2=\frac{k}{m},\quad 2\gamma=\frac{b}{m}. \tag{1}
> $$
>
> **[[Natural frequency]]** $\omega_0$ is the angular frequency the mass would oscillate at without drag; **[[Damping rate]]** $\gamma$ is the rate at which the drag removes amplitude.

^def-free-eom

Equation (1) contains only two rates, so the shape of the motion can depend only on their ratio. What do the two rates mean on their own?

> [!explain] Explanation — Two time scales
> - $1/\omega_0$ sets how fast the spring pulls the mass back; one free period is $T_0=2\pi/\omega_0$.
> - $1/\gamma$ sets how long the drag takes to remove the motion; the factor 2 in $2\gamma$ is chosen so that, as shown below, the amplitude decays exactly as $\mathrm{e}^{-\gamma t}$.
> - ***The ratio $\gamma/\omega_0$ alone decides whether the mass oscillates.*** Everything else is a choice of units for time and length.

^exp-free-rates

### Exponential trial solutions

Because Eq. (1) is linear with constant coefficients, an exponential keeps its form under differentiation; substituting one turns the differential equation into an algebraic one.

> [!proposition] Proposition — Characteristic roots
> Solutions of Eq. (1) of the form $x=\mathrm{e}^{st}$ exist for exactly two values of $s$,
>
> $$
> s_\pm=-\gamma\pm\sqrt{\gamma^2-\omega_0^2}, \tag{2}
> $$
>
> and every solution is a combination $x(t)=C_+\mathrm{e}^{s_+t}+C_-\mathrm{e}^{s_-t}$ fixed by $x(0)$ and $\dot x(0)$. **Both roots have a negative real part, so every motion dies out; whether it oscillates depends on the sign under the square root.**

^pro-free-roots

> [!derivation] Derivation — From the equation to the roots
> **Step 1: substitute.** With $x=\mathrm{e}^{st}$, $\dot x=s\,\mathrm{e}^{st}$ and $\ddot x=s^2\mathrm{e}^{st}$, so Eq. (1) reads $(s^2+2\gamma s+\omega_0^2)\,\mathrm{e}^{st}=0$.
>
> **Step 2: solve the quadratic.** The exponential never vanishes, hence $s^2+2\gamma s+\omega_0^2=0$, whose roots are Eq. (2).
>
> **Step 3: superpose.** The equation is linear, so any combination of the two solutions is again a solution; two constants match the two initial conditions of a second-order equation.

^der-free-roots

## Three regimes of damping

### Underdamped motion

When the drag is weak, $\gamma<\omega_0$, the square root in Eq. (2) is imaginary and the two roots are complex conjugates. What does a complex exponent mean for a real displacement?

> [!proposition] Proposition — Underdamped solution
> For $\gamma<\omega_0$ every real solution of Eq. (1) is a cosine inside a decaying envelope,
>
> $$
> x(t)=A\,\mathrm{e}^{-\gamma t}\cos(\omega_d t+\varphi),\qquad \omega_d=\sqrt{\omega_0^2-\gamma^2}, \tag{3}
> $$
>
> with amplitude $A$ and phase $\varphi$ set by the initial conditions. **The oscillation runs at the damped frequency $\omega_d$, slightly below $\omega_0$, while the envelope decays at the rate $\gamma$.**

^pro-free-under

> [!derivation] Derivation — Real form of the conjugate roots
> **Step 1.** For $\gamma<\omega_0$, Eq. (2) gives $s_\pm=-\gamma\pm\mathrm{i}\omega_d$.
>
> **Step 2.** A real $x$ needs $C_-=C_+^{*}$. Writing $C_+=\tfrac12 A\,\mathrm{e}^{\mathrm{i}\varphi}$,
>
> $$
> x=\tfrac12 A\,\mathrm{e}^{-\gamma t}\left(\mathrm{e}^{\mathrm{i}(\omega_d t+\varphi)}+\mathrm{e}^{-\mathrm{i}(\omega_d t+\varphi)}\right)=A\,\mathrm{e}^{-\gamma t}\cos(\omega_d t+\varphi).
> $$

^der-free-under

> [!figure] **Fig. 1** Free motion of a damped oscillator released from rest at $x_0$. (a) Displacement versus time in units of the free period $T_0$ for $\gamma=0.1\,\omega_0$ (blue), $\gamma=\omega_0$ (orange) and $\gamma=2.5\,\omega_0$ (green), with the envelope $\pm\mathrm{e}^{-\gamma t}$ of the underdamped case dotted; (b) energy on a logarithmic scale for $Q=5$ and $Q=20$, with the law $\mathrm{e}^{-2\gamma t}$ dashed.
> ![[damping-regimes.png|720]]

^fig-free-regimes

Fig. 1(a) compares the three regimes of Eq. (2): the underdamped mass oscillates at $\omega_d$ and crosses zero once every half period, while its peaks follow the envelope $\mathrm{e}^{-\gamma t}$ of Eq. (3); the critically and overdamped masses never cross zero, and of these two the critically damped one returns first, because a larger $\gamma$ only slows the creep back. Fig. 1(b) looks at the same decay through energy: on a logarithmic scale the energy falls along a straight line, with a slope proportional to $1/Q$, so the $Q=20$ oscillator keeps its energy four times longer than the $Q=5$ one. Why the slope is $2\gamma$ and not $\gamma$ is derived in the next section.

### Critical and overdamped motion

What happens when the square root in Eq. (2) becomes real? The two roots are then real and negative, and the motion is a sum of two plain decays.

> [!definition] Definition — Critical damping and overdamping
> **[[Critical damping]]** is the boundary $\gamma=\omega_0$, where the two roots of Eq. (2) merge into $s=-\omega_0$ and the general solution becomes $x(t)=(C_1+C_2t)\,\mathrm{e}^{-\omega_0 t}$. For $\gamma>\omega_0$ (overdamping) both roots are real; the slower one,
>
> $$
> |s_+|=\gamma-\sqrt{\gamma^2-\omega_0^2}\approx\frac{\omega_0^2}{2\gamma}\quad(\gamma\gg\omega_0),
> $$
>
> controls the late motion, so ==strong drag makes the return slower, not faster==.

^def-free-critical

This is why door closers, galvanometers and car suspensions are tuned close to critical damping: it gives the quickest return without ringing (orange curve in Fig. 1(a)).

> [!warning] Caution — "No overshoot" depends on the start
> A critically damped mass released from rest never crosses $x=0$. Given a large enough initial velocity toward equilibrium, $\dot x(0)<-\omega_0x(0)$, it crosses once and then creeps back from the other side. Overdamped motion can likewise cross zero at most once.

^warn-free-overshoot

## Energy decay and the quality factor

### Energy loss per cycle

Damping is easier to compare between very different oscillators through energy than through amplitude. How fast does the stored energy $E=\tfrac12m\dot x^2+\tfrac12kx^2$ disappear?

> [!derivation] Derivation — Energy decays at twice the amplitude rate
> **Step 1: power lost to drag.** Differentiating $E$ and using Eq. (1),
>
> $$
> \frac{\mathrm{d}E}{\mathrm{d}t}=\dot x\,(m\ddot x+kx)=-b\,\dot x^2=-2m\gamma\,\dot x^2 .
> $$
>
> **Step 2: average over one cycle.** For light damping, $\gamma\ll\omega_0$, the motion over one period is nearly $A\cos(\omega_0t)$, whose kinetic energy averages to half of $E$: $\langle\tfrac12 m\dot x^2\rangle=\tfrac12E$. Hence $\langle\mathrm{d}E/\mathrm{d}t\rangle=-2\gamma E$.
>
> **Step 3: integrate.** $E(t)=E_0\,\mathrm{e}^{-2\gamma t}$, the square of the amplitude envelope in Eq. (3). Over one period $T_0$ the fraction lost is $1-\mathrm{e}^{-2\gamma T_0}\approx2\gamma T_0=4\pi\gamma/\omega_0$.

^der-free-energy

Figure 1(b) confirms the result: the energy follows $\mathrm{e}^{-2\gamma t}$ on average, with small steps because the drag removes energy fastest when the mass moves fastest.

### The quality factor

The fraction lost per cycle, $4\pi\gamma/\omega_0$, is a dimensionless measure of damping. Its inverse, up to a factor $2\pi$, is the standard figure of merit.

> [!definition] Definition — Quality factor
> The **[[Quality factor]]** of a damped oscillator is
>
> $$
> Q\equiv\frac{\omega_0}{2\gamma}=2\pi\,\frac{\text{energy stored}}{\text{energy lost per cycle}}\quad(\gamma\ll\omega_0). \tag{4}
> $$
>
> The amplitude falls by $1/\mathrm{e}$ in a time $1/\gamma=2Q/\omega_0$, that is, after about $Q/\pi$ oscillations; critical damping corresponds to $Q=\tfrac12$.

^def-free-q

> [!explain] Explanation — Typical values
> A door with a closer has $Q\lesssim1$, a plucked guitar string is of order $10^3$, a quartz watch crystal around $10^4$ to $10^5$. In Eq. (3) the frequency shift is tiny for any good oscillator: $\omega_d=\omega_0\sqrt{1-1/(4Q^2)}$ differs from $\omega_0$ by less than $1\%$ once $Q>3.6$.

^exp-free-values

> [!conclusion] Conclusion — Two numbers describe free motion
> The natural frequency $\omega_0$ and the damping rate $\gamma$, combined in $Q$, fix the free motion completely: oscillation at $\omega_d$ inside an $\mathrm{e}^{-\gamma t}$ envelope for $Q>\tfrac12$, non-oscillatory decay for $Q\le\tfrac12$. ==The same $Q$ will set how sharply the oscillator responds to a periodic force.==

^con-free-summary

> [!series] Damped and driven oscillations
> [[Home]]
>
> [[Driven oscillations and resonance]]
>
> [[1 Damped and driven oscillations|Series map]]
