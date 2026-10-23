# Audit of my previous answer

Source: Claude response pasted by Suraj. Formatting normalized. This audit itself contains claims requiring qualification; see SCIENTIFIC_REVIEW.md.

## Errors found

1. **Thermal Doppler parameters were wrong.** I gave ~1 km/s for H and ~0.13 km/s for Fe at 10⁴ K. The correct values are 12.9 km/s and 1.73 km/s (derivation below).
2. **Thermal broadening is not a lower bound on b when T is unknown.** I stated it as a bound on the physical range of b, which is only valid if T is fixed or bounded from below.
3. **"A black core constrains N only from below" was overstated.** It ignores that damping wings, or their absence, constrain N from both sides.
4. **Two curve-of-growth boundaries were imprecise.** I put the onset of the damped regime at N_HI ≳ 10¹⁹ cm⁻² and the end of the flat regime at τ₀ ~ 10³. Both depend on the transition and on b.
5. **Three smaller issues:**
   - Resolution biases N_a whenever τ is not ≪ 1, not only when the line is saturated.
   - The partial-covering test was worded loosely.
   - Total N is "robust" mainly in the optically thin regime, not generally.

## 1. Thermal Doppler parameters

b_th = √(2kT/m), with k = 1.3806×10⁻²³ J K⁻¹ and T = 10⁴ K, so 2kT = 2.761×10⁻¹⁹ J.

- **Hydrogen:** m = 1.6735×10⁻²⁷ kg, so b_th = √(1.650×10⁸ m² s⁻²) = 1.285×10⁴ m/s = **12.9 km/s**. The thermal FWHM is 1.665 b = 21.4 km/s.
- **Iron:** m = 55.845 u = 9.273×10⁻²⁶ kg, so b_th = √(2.978×10⁶ m² s⁻²) = 1.726×10³ m/s = **1.73 km/s**. The thermal FWHM is 2.87 km/s.

As a cross-check, b_th ≈ 0.129 √[(T/K)/A] km/s with A the atomic mass number. The H/Fe ratio is √(55.8/1.008) ≈ 7.4, which matches 12.9/1.73.

For context, an echelle at R ≈ 4×10⁴ has an LSF FWHM of c/R ≈ 7.5 km/s. Thermal Fe widths at 10⁴ K are therefore well below the resolution, while thermal H widths are resolved.

## 2. Does thermal broadening give a lower bound on b?

The line width satisfies b² = b_th² + b_turb², where b_turb is the non-thermal (Gaussian-turbulent) contribution.

When T is unknown, there is no useful lower bound:

- Since b_th ∝ √T, b ≥ b_th(T_min). Only a physical floor on T can supply a bound.
- The weakest defensible floor is roughly T_CMB(z) = 2.725(1+z) K, which gives b_th(Fe) ≈ 0.03 km/s at z = 0. That is not constraining.
- Cold gas (T ~ 10² K) gives b_th(Fe) = 0.17 km/s and b_th(H) = 1.3 km/s. Quoting the 10⁴ K value as a floor assumes T ≥ 10⁴ K.

What the data do bound is the other direction. For a single, resolved component, the LSF-deconvolved width gives b ≤ b_obs, hence T ≤ m b_obs²/2k. For Fe with b_obs = 5 km/s, T ≤ 8.4×10⁴ K.

If two ions of different mass are fitted at the same velocity, T and b_turb can in principle be separated. That requires:

- the ions are co-spatial;
- they share T and b_turb;
- the lines are resolved and unsaturated.

The solution is ill-conditioned when the masses are close.

**Consequence for N.** In the flat part of the curve of growth, N depends strongly on b, and there is no thermal floor to cap it. The bracket on N instead comes from:

- a model-free lower limit from the AOD;
- an upper limit from the absence of damping wings, or from weaker transitions.

## 3. Reconciling black cores and damping wings

Both statements are right once their domains are separated.

A black Doppler core alone tells you τ₀ is large. The AOD is then bounded below by roughly ln(1/(nσ)) per pixel, so the column is a lower limit if one looks only at the core.

In the wings the Lorentzian dominates, and the b-dependence cancels. For |Δv| ≫ b:

τ(Δv) = e² f λ² Γ N / (4π m_e c Δv²)

This depends only on N, atomic data (f, λ, Γ) and Δv, and not on b. For Lyα this gives roughly τ ≈ 2.6×10⁻¹⁵ N/Δv² (N in cm⁻², Δv in km/s). For example, N_HI = 10²⁰ cm⁻² and Δv = 100 km/s give τ ≈ 26.

So for a black core:

- **Wings detected:** N is measured from the wings, independent of b. It still depends on the continuum, blends, and the correctness of Γ. It is the total N of everything blended in the wings, and cannot be split among components.
- **Wings not detected at the S/N and continuum accuracy:** N has an upper limit. The threshold scales as 1/(f λ² Γ). For Lyα at high S/N in a clean continuum it is of order 10¹⁷–10¹⁸ cm⁻².
- **Weaker transitions unsaturated:** N is measured from them.
- **None of the above:** only a lower limit.

Related corrections:

- The wings begin to matter at N_HI ~ 10¹⁷–10¹⁸ cm⁻² for Lyα, and the full square-root regime (W ∝ √(Nγ)) sets in at higher columns.
- The flat regime ends where the damping wings emerge, which depends on the damping parameter a and hence on the transition and on b.

## 4. Assumptions: AOD versus Voigt decomposition

| Assumption | AOD | Voigt decomposition |
|---|---|---|
| Continuum and zero level correct | Yes | Yes |
| Covering factor = 1, no unabsorbed light or infilling | Yes | Yes (unless C_f is fitted) |
| Correct atomic data (f, λ, Γ) | Yes | Yes |
| No unrecognized blends | Yes | Yes |
| Integration window contains all the absorption | Yes | Not needed (the model sets it) |
| Profile shape | None | Each component has a Maxwellian (thermal + Gaussian turbulence) velocity distribution |
| Number and positions of components | None | Required, chosen by a model-selection criterion |
| LSF shape known | Not needed for the lower bound | Required, since the model is convolved with the LSF |
| Noise model | Per-pixel errors | Gaussian, uncorrelated pixels, valid χ² |
| Output | Lower bound on N, N_a ≤ N | Model-dependent estimate |

N_a ≈ N only if every part of the profile is intrinsically optically thin or fully resolved. Otherwise N_a < N, by Jensen's inequality applied to the instrumental smoothing. This applies whenever τ is non-negligible, not only at saturation.

Voigt fitting can do better than the AOD only by adding assumptions. In the optically thin regime it adds little beyond component velocities.

## 5. Corrected versions of earlier statements

- **Doppler widths:** at 10⁴ K, b_th(H) = 12.9 km/s and b_th(Fe) = 1.73 km/s.
- **Bounds:** the range on N for a saturated single line comes from the AOD lower limit and the wing or weak-line upper limit, not from b_th.
- **Partial covering:** for a doublet with f-ratio 2:1, C_f = 1 requires I_weak = I_strong^(1/2). If both lines are saturated and share the same nonzero floor, that floor equals 1 − C_f. Equal residual flux in unsaturated lines of different strength does not indicate partial covering.
- **Summed N:** it is robust mainly when the lines are optically thin. In the saturated regime, summing component columns does not remove the b–N degeneracy.
- **Table rows:**
   - Flat part of the curve of growth, one line: lower limit from the AOD, and an upper limit if wings are absent. The Voigt N within that bracket depends on the assumed b.
   - Damped wings visible: N is measured from the wings, independent of b, as long as the continuum is good and blends are controlled.
