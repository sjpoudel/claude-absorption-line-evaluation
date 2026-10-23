# Claude's first experiment report

Source: Claude response pasted by Suraj; formatting normalized.

NumPy 2.x removed `trapz`; I'll switch to `trapezoid`.

Yes: instrumental broadening alone can produce a spurious partial-covering signature in a doublet whose true covering factor is 1. The script `doublet_lsf_experiment.py` and the figure `doublet_lsf_experiment.png` contain the experiment.

## Setup and assumptions

- **Opacity:** The strong line has τ_s(v) = 4 exp[−(v/b)²] with b = 10 km/s, and the weak line has τ_w = τ_s/2.
- **Frame:** Both lines are overlaid in one velocity frame, with no damping wings, noise or blends.
- **Covering:** C_f = 1 and the continuum is 1.
- **LSF:** A normalized Gaussian with FWHM = 15 km/s, applied to the flux, not to τ.
- **Grid:** 0.05 km/s pixels over ±400 km/s. The flux is padded with 1 beyond the window, so the continuum is not distorted at the edges.

## Verification

| Check | Result |
|---|---|
| Intrinsic relation I_w = I_s^½ | max deviation 1.1×10⁻¹⁶ (machine precision) |
| LSF kernel normalization | sum = 1.000000000000 |
| Continuum at window edges after convolution | 1.000000000000 for both lines |
| Window half-width | 40 b, 63 σ_LSF |
| EW conservation, strong line | relative change +6×10⁻¹⁵ |
| EW conservation, weak line | relative change +8×10⁻¹⁵ |

The equivalent widths and the continuum are preserved, so the LSF here only redistributes absorption. The relation then breaks even though no flux is lost.

## Result

After convolution, I_w,obs < √I_s,obs at every velocity where there is absorption. At line center the weak line is 0.263, where the intrinsic relation applied to the observed strong line would predict 0.314. The deviation reaches −0.076 off-center.

This sign is fixed by Jensen's inequality. The LSF averages flux linearly, and √ is concave, so ⟨√I_s⟩ ≤ √⟨I_s⟩. Since I_w = √I_s intrinsically, the convolved weak line must lie below √(convolved strong line). That is what the Jensen check in the output confirms.

The inferred covering fraction uses the standard 2:1 solution, C_f = (1 − I_w)²/(1 − 2I_w + I_s). Intrinsically it returns exactly 1. From the convolved profiles it returns:

- 0.95 at line center
- 0.19 at the edge of the region where the strong line is at least 10% deep (|v| ≈ 23 km/s)

The deficit is smallest at the core and grows toward the wings. A fit to the observed profiles would show a velocity-dependent covering fraction, with the lowest values where the profile is shallowest.

## Sweep

The minimum apparent C_f for true C_f = 1, evaluated only where the strong line is at least 10% deep:

| τ₀ (strong) | FWHM/b = 0.25 | 0.5 | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|---|
| 0.5 | 0.94 | 0.80 | 0.57 | 0.45 | 0.39 |
| 2 | 0.89 | 0.67 | 0.36 | 0.24 | 0.19 |
| 4 | 0.86 | 0.61 | 0.29 | 0.19 | 0.16 |
| 16 | 0.82 | 0.51 | 0.22 | 0.15 | 0.13 |

The spurious deficit grows with LSF width relative to b. It is mild when the LSF is a quarter of b but severe when the LSF is comparable to or wider than b. It also grows with τ₀, since stronger lines have steeper profiles.

## Caveats

- **My first run was wrong.** It reported a minimum apparent C_f of 0.000 from the far wings, where both lines are near unity and the doublet solution is 0/0. I restricted the diagnostic to pixels with at least 10% strong-line depth. That threshold is arbitrary, and the minimum values in the sweep sit at the edge of the masked region, so they depend on it. The core values are less sensitive.
- **Real data add noise.** With noise, wing pixels would scatter widely, so a real fit would be dominated by the better-measured pixels. The effect would still show up as a systematic offset, not as scatter.
- **The model is simplified.** I used Gaussian opacity, a Gaussian LSF and a single component. Real profiles have wings and multiple components, and real LSFs are non-Gaussian, which changes the size of the effect but not its sign.
- **The sign argument is general.** It applies to any normalized, non-negative LSF and any intrinsic profile. The magnitude depends on the profile and the LSF.

## Practical consequence

A weak line darker than √I_s predicts is the signature of partial covering, but it is also the signature of unresolved structure convolved with the LSF. To distinguish them, convolve the model with the measured LSF before comparing, and test whether a full-covering model passes through the instrument model. Partial covering should be claimed only if the convolved full-covering model fails to reproduce both lines.
