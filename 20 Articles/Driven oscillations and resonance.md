---
type: article
series: "[[1 Damped and driven oscillations]]"
series_no: 1
seq: 2
summary: 'How a damped oscillator answers a periodic force: the steady-state amplitude and phase lag, the resonance peak and its width, and the transient that dies out before the steady state is reached'
sections: ["The steady-state response", "Resonance", "Transients"]
kinds: [Definition, Explanation, Proposition, Derivation, Caution, Conclusion]
terms: ["[[Steady-state response]]", "[[Resonance]]", "[[Quality factor]]", "[[Damping rate]]", "[[Natural frequency]]"]
sources: ["[[French1971]]", "[[Landau1976]]"]
figures: 2
equations: 4
words: 1554
cssclasses: [card-note, article-note]
---
Left alone, a damped oscillator always comes to rest. Push it periodically and it ends up moving at the frequency of the push, with an amplitude and a lag that depend strongly on how close that frequency is to its own. This article asks what that steady response is, why it peaks near the natural frequency, how sharp the peak is, and how long the oscillator takes to get there ([[French1971|French 1971]]; [[Landau1976|Landau and Lifshitz 1976]]).

## The steady-state response

### A periodic force

Add a sinusoidal force $F_0\cos\omega t$ to the free oscillator. The drive frequency $\omega$ is set from outside and need not be related to the [[Natural frequency|natural frequency]] $\omega_0$.

> [!definition] Definition — Driven damped oscillator
> With the natural frequency $\omega_0$ and the [[Damping rate|damping rate]] $\gamma$ defined as for free motion, the displacement obeys
>
> $$
> \ddot x+2\gamma\,\dot x+\omega_0^2\,x=\frac{F_0}{m}\cos\omega t . \tag{1}
> $$

^def-drv-eom

Equation (1) is linear, so its solutions are a particular solution plus any free motion; the free part dies out as $\mathrm{e}^{-\gamma t}$. What survives is a motion at the drive frequency, and the cleanest way to find it uses complex numbers.

> [!explain] Explanation — Why a complex trial solution works
> Write the force as $\operatorname{Re}\,[F_0\mathrm{e}^{\mathrm{i}\omega t}]$ and look for $x=\operatorname{Re}\,[A\,\mathrm{e}^{\mathrm{i}\omega t}]$ with a complex amplitude $A$. Because Eq. (1) has real coefficients, taking the real part commutes with the left-hand side, so it is enough to solve the equation for the complex exponential. Each time derivative then becomes a factor $\mathrm{i}\omega$, and the differential equation turns into one algebraic equation for $A$.

^exp-drv-complex

### Amplitude and phase

> [!proposition] Proposition — Steady-state response
> The **[[Steady-state response]]** to Eq. (1) is $x(t)=|A|\cos(\omega t-\delta)$ with the complex amplitude
>
> $$
> A(\omega)=\frac{F_0/m}{\omega_0^2-\omega^2+2\mathrm{i}\gamma\omega}, \tag{2}
> $$
>
> whose modulus and phase lag are
>
> $$
> |A|=\frac{F_0/m}{\sqrt{(\omega_0^2-\omega^2)^2+4\gamma^2\omega^2}},\qquad \tan\delta=\frac{2\gamma\omega}{\omega_0^2-\omega^2},\quad 0\le\delta\le\pi . \tag{3}
> $$
>
> **The displacement always lags the force; the lag passes through $\pi/2$ exactly at $\omega=\omega_0$, whatever the damping.**

^pro-drv-amp

> [!derivation] Derivation — Solving for the complex amplitude
> **Step 1: substitute.** With $x=A\,\mathrm{e}^{\mathrm{i}\omega t}$, Eq. (1) becomes $(-\omega^2+2\mathrm{i}\gamma\omega+\omega_0^2)\,A=F_0/m$, which is Eq. (2).
>
> **Step 2: polar form.** Write the denominator as $D\,\mathrm{e}^{\mathrm{i}\delta}$ with $D=\sqrt{(\omega_0^2-\omega^2)^2+4\gamma^2\omega^2}$ and $\tan\delta=2\gamma\omega/(\omega_0^2-\omega^2)$. Its imaginary part $2\gamma\omega$ is positive, so $\delta$ lies between $0$ and $\pi$.
>
> **Step 3: take the real part.** $A=(F_0/mD)\,\mathrm{e}^{-\mathrm{i}\delta}$, so $x=\operatorname{Re}\,[A\,\mathrm{e}^{\mathrm{i}\omega t}]=|A|\cos(\omega t-\delta)$.

^der-drv-amp

Equation (3) is easiest to read in three frequency ranges, where a different term of Eq. (1) dominates.

> [!explain] Explanation — Stiffness, damping and mass control
> - **$\omega\ll\omega_0$, stiffness-controlled:** $|A|\to F_0/(m\omega_0^2)=F_0/k$, the static stretch, with $\delta\to0$; the spring follows the force.
> - **$\omega=\omega_0$, damping-controlled:** the spring and inertia terms cancel, $|A|=F_0/(2m\gamma\omega_0)$ and $\delta=\pi/2$; only the drag limits the motion.
> - **$\omega\gg\omega_0$, mass-controlled:** $|A|\approx F_0/(m\omega^2)$ and $\delta\to\pi$; the mass moves against the force.

^exp-drv-regions

> [!figure] **Fig. 1** Steady-state response of a driven damped oscillator. (a) Amplitude in units of the static displacement $F_0/(m\omega_0^2)$ versus drive frequency, for $Q=0.5$, 1, 2, 5 and 10; (b) phase lag $\delta$ for the same $Q$ values, with $\omega=\omega_0$ and $\delta=\pi/2$ dotted.
> ![[resonance.png|720]]

^fig-drv-resonance

Fig. 1(a) shows the gain of Eq. (3): far below $\omega_0$ every curve tends to 1, because a slow force simply stretches the spring; near $\omega_0$ the peak height grows in proportion to $Q$ while the peak narrows, and for $Q=0.5$ there is no peak at all, the response only falls with frequency. Fig. 1(b) shows who leads whom: at low frequency the mass follows the force ($\delta\approx0$), far above $\omega_0$ it moves against it ($\delta\to\pi$), and every curve passes through $\delta=\pi/2$ exactly at $\omega_0$, where the force is in phase with the velocity and therefore does the most work. The larger $Q$, the narrower the frequency range over which this phase change happens, the same narrowing that sharpens the peak in Fig. 1(a).

## Resonance

### Absorbed power

The amplitude peak is not quite at $\omega_0$; the power the force delivers is the cleaner quantity, because in the steady state it equals the power the drag dissipates.

> [!proposition] Proposition — Resonance curve and its width
> Averaged over a cycle, the force delivers the power
>
> $$
> \bar P(\omega)=\frac{F_0^2}{m}\,\frac{\gamma\,\omega^2}{(\omega_0^2-\omega^2)^2+4\gamma^2\omega^2},\qquad \Delta\omega_{\mathrm{FWHM}}=2\gamma=\frac{\omega_0}{Q} . \tag{4}
> $$
>
> $\bar P$ peaks exactly at $\omega=\omega_0$ with $\bar P_{\max}=F_0^2/(4m\gamma)$. ==The full width at half maximum of the power curve is exactly $2\gamma$==, so a sharp **[[Resonance]]** means weak damping.

^pro-drv-power

> [!derivation] Derivation — Mean power and its half-width
> **Step 1: mean power.** The velocity is $\dot x=-\omega|A|\sin(\omega t-\delta)$. Averaging $F_0\cos\omega t\cdot\dot x$ over a cycle keeps only the in-phase part, $\bar P=\tfrac12F_0\,\omega|A|\sin\delta$.
>
> **Step 2: insert Eq. (3).** From Step 2 of the previous derivation, $\sin\delta=2\gamma\omega/D$ and $|A|=F_0/(mD)$, so $\bar P=F_0^2\gamma\omega^2/(mD^2)$, the first part of Eq. (4). At $\omega=\omega_0$, $D=2\gamma\omega_0$ and $\bar P_{\max}=F_0^2/(4m\gamma)$.
>
> **Step 3: half maximum.** $\bar P/\bar P_{\max}=4\gamma^2\omega^2/D^2=\tfrac12$ requires $(\omega_0^2-\omega^2)^2=4\gamma^2\omega^2$, i.e. $\omega_0^2-\omega^2=\pm2\gamma\omega$. The positive roots are $\omega_\pm=\sqrt{\omega_0^2+\gamma^2}\pm\gamma$, whose difference is exactly $2\gamma$.

^der-drv-power

### Sharpness and the quality factor

The width in Eq. (4) ties the driven response back to free decay. The same number $Q$ appears in both, which is what makes it the natural figure of merit.

> [!explain] Explanation — One $Q$, three meanings
> - **Free decay:** $Q=\omega_0/(2\gamma)$ is $2\pi$ times the stored energy over the energy lost per cycle ([[Free damped oscillations#^def-free-q|“Free damped oscillations” Eq. (4)]]).
> - **Bandwidth:** by Eq. (4), $Q=\omega_0/\Delta\omega_{\mathrm{FWHM}}$, the resonance frequency over the width of the power curve.
> - **Gain:** at $\omega=\omega_0$, Eq. (3) gives $|A|=Q\,F_0/k$; the resonant amplitude is $Q$ times the static stretch.

^exp-drv-q

> [!warning] Caution — The amplitude peak is shifted
> Maximising $|A|$ in Eq. (3) gives the amplitude-resonance frequency $\omega_r=\sqrt{\omega_0^2-2\gamma^2}$, slightly below $\omega_0$ and existing only for $Q>1/\sqrt2$; the $Q=0.5$ curve in Fig. 1(a) has no peak at all. The power peak, the $\pi/2$ phase point and the free frequency $\omega_d=\sqrt{\omega_0^2-\gamma^2}$ are three further, distinct frequencies; for large $Q$ all four agree to order $1/Q^2$.

^warn-drv-peak

## Transients

### Start-up from rest

The steady state is only what remains after the free motion has died out. How long does that take, and what does the motion look like in between?

> [!proposition] Proposition — Transient plus steady state
> The general solution of Eq. (1) is the steady-state response plus a free solution of the undriven equation,
>
> $$
> x(t)=|A|\cos(\omega t-\delta)+B\,\mathrm{e}^{-\gamma t}\cos(\omega_d t+\phi),
> $$
>
> with $B$ and $\phi$ fixed by the initial conditions. **The transient decays at the damping rate $\gamma$, so the steady state is reached after a few times $1/\gamma=2Q/\omega_0$, i.e. after roughly $Q$ cycles.**

^pro-drv-transient

> [!figure] **Fig. 2** Start-up of a driven oscillator from rest, $x(0)=\dot x(0)=0$, for $Q=10$ and $\omega=0.85\,\omega_0$. Displacement in units of the steady-state amplitude versus time in free periods: full solution (blue), steady-state part (orange, dashed) and transient part (green).
> ![[transient.png|720]]

^fig-drv-transient

In Fig. 2 the full solution starts at zero, so at $t=0$ the transient must exactly cancel the steady-state part; the two then run at different frequencies, $\omega_d$ and $\omega$, and the early beating of the full curve, overshooting the steady amplitude by about 40 %, is their interference. The transient shrinks as $\mathrm{e}^{-\gamma t}$ and is negligible after a few $1/\gamma\approx3T_0$, after which the full and steady-state curves coincide, as the proposition above predicts.

### Why the transient matters

> [!warning] Caution — Sweeping too fast distorts the resonance
> A resonance curve measured by stepping the drive frequency is the steady-state curve of Fig. 1 only if each frequency is held for many times $1/\gamma$. For a high-$Q$ oscillator this time is long, and sweeping faster leaves transients that shift and skew the measured peak.

^warn-drv-sweep

> [!conclusion] Conclusion — What the driven oscillator does
> A linear oscillator driven at $\omega$ settles, after a transient lasting a few $1/\gamma$, into motion at $\omega$ with the amplitude and lag of Eq. (3). Its absorbed power peaks at $\omega_0$ with width $2\gamma$, so ==the quality factor measured from free decay predicts the sharpness and the height of the resonance==.

^con-drv-summary

> [!series] Damped and driven oscillations
> [[Free damped oscillations]]
>
> [[Impulse response and arbitrary forces]]
>
> [[1 Damped and driven oscillations|Series map]]
