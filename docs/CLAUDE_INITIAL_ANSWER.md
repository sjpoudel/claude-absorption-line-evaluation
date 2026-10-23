# Claude's initial answer

Source: response pasted by Suraj into this conversation. Formatting normalized; historical claims below are not all correct. See SCIENTIFIC_REVIEW.md.

**Assumptions**

- The absorber is a collection of discrete, intervening or circumstellar components along a pencil-beam sightline, with a Voigt-profile opacity per component.
- The background continuum is a smooth source, covering factor C_f = 1 unless stated otherwise.
- The atomic data (f-values, wavelengths, damping constants) are correct.
- The noise is approximately Gaussian and the continuum is placed correctly.

**1. The measurement without a model: apparent optical depth (AOD)**

The data directly give τ_a(v) = ln[I_c(v)/I(v)]. Then

N_a = (m_e c / πe²) · (1/(f λ)) ∫ τ_a(v) dv ≈ 3.768×10¹⁴ / (f λ[Å]) ∫ τ_a dv [cm⁻², with v in km/s]

This is the quantity the data constrain most cleanly. It is a column density only under specific conditions. It is equivalent to the true N if the instrument has smoothed nothing and the profile has no unresolved saturated structure. In the optically thin limit (τ ≲ 0.1–0.3 everywhere), N_a ≈ N_true, independent of b and of the component structure. Integrating the weak line directly is then the most robust approach, because it requires no Voigt decomposition.

**2. Saturation**

Saturation is the main failure mode. The equivalent width W_λ follows a curve of growth:

- **Linear regime** (τ₀ ≲ 1): W ∝ N, independent of b. The measurement is reliable.
- **Flat (logarithmic) regime** (τ₀ ~ 1 to ~10³): W depends weakly on N and strongly on b. Here the line core carries almost no information about N. A modest error in b translates into an error of an order of magnitude in N.
- **Damped regime** (N_HI ≳ 10¹⁹ cm⁻²): W ∝ √(N γ). The damping wings constrain N regardless of b, so such measurements are reliable again.

The key point is that apparent optical depth at line center is bounded by the noise floor. If the core flux is consistent with zero, the data give only a lower limit on τ, hence on N. A line with a flat-bottomed, zero-flux core therefore constrains N only from below, whatever the Voigt fit returns.

**The subtler problem: unresolved saturation.** The AOD profile can look unsaturated while hiding saturated sub-structure. When the instrument smooths sharp, narrow components, the measured τ_a is a convolution in intensity space, not in optical depth. By Jensen's inequality, τ_a is then systematically below the true τ, so N_a underestimates N. Savage & Sembach (1991) showed this explicitly: the error grows with the fraction of the profile that is saturated at the intrinsic resolution.

**Diagnostic that uses the data, not the model.** If you have two or more transitions of the same ion with different f λ (e.g., the Si II 1190, 1193, 1260, and 1304 lines, or the Fe II multiplets), compare the AOD profiles scaled by f λ. If τ_a/(f λ) agrees across the lines at all velocities, the profile is not significantly saturated or unresolved. If the stronger transition falls below the scaled weaker one, the stronger transition is saturated or affected by unresolved structure. The weakest transition then bounds N from below, and the discrepancy gives a correction (the Savage-Sembach apparent-optical-depth correction), which is itself approximate.

**3. Instrumental broadening and unresolved velocity structure**

Convolution with the line-spread function (LSF) conserves the integrated equivalent width. It does not conserve N_a once any part of the profile is saturated, for the Jensen reason above. So the effects separate as follows:

- If everything is optically thin, N_a is unaffected by resolution. Resolution only matters for velocity structure.
- If lines are saturated, resolution matters strongly. A resolving power R below the line's intrinsic width in velocity (FWHM_inst ≳ b) smears the saturated core and produces an artificially low-depth, broad profile.

What the data constrain: the observed convolved profile, and the equivalent width. What depends on the model: the intrinsic b and the number of components, since the same convolved profile can be fit by one broad component or several narrow ones. This is the classic b–N degeneracy.

**Number of components.** Voigt fitting needs a choice of how many components to include. Information criteria (AIC/BIC) or an F-test can limit overfitting, but they assume Gaussian noise and a correct continuum and LSF. Even then, the component decomposition is non-unique when the profile is blended or the S/N is limited. Total N, summed over components, is usually far more robust than individual (N_i, b_i). So report the summed column and the velocity-integrated AOD, and treat individual component values with caution.

**Bounds from b.** For a single saturated line with unknown b, the physical range of b is bounded below by thermal broadening (b_th = √(2kT/m), which is ~ 0.13 km/s for Fe at 10⁴ K, but ~ 1 km/s for H) and above by the observed line width. Taking b at its lower limit yields an upper bound on N. Taking the largest allowed b yields a lower bound. The allowed range can span orders of magnitude.

**4. Other systematics that affect N**

- **Continuum placement**: this matters most for weak lines and for lines in the Lyα forest or near broad emission lines. A few percent error in the continuum changes τ in the wings and can significantly alter N for weak lines.
- **Partial covering**: if C_f < 1, a saturated line does not reach zero flux, and the Voigt model with C_f = 1 will give a falsely low N. Detecting this requires doublets with different f λ but the same ion, such as Si IV, C IV, N V, or the Lyman series, where the residual flux should differ if C_f = 1. Equal residual flux in lines of different strength signals partial covering. This matters particularly for AGN intrinsic absorbers and for small background sources. The recovered N depends on the covering model.
- **Blends and contamination**: unrecognized interlopers inflate N_a, especially in the Lyα forest. Comparing multiple transitions helps identify them.
- **Noise and Poisson statistics at low counts**: when the core flux is a few counts, Gaussian errors break down, and the likelihood should use Poisson statistics, particularly in the UV with HST/COS.
- **Atomic data**: f-value uncertainties of 5–10% for some ions transfer directly to N. Some of the Fe II and Ni II f-values have been revised repeatedly.

**5. Summary: when a measurement is reliable**

| Situation | What constrains N | Reliability |
|---|---|---|
| Optically thin line, adequate S/N | Integrated τ_a directly | High, nearly model-independent |
| Multiple transitions, scaled AODs agree | AOD plus consistency check | High, with saturation tested |
| Flat part of the curve of growth, one line | Only a lower limit from AOD | Low; Voigt N depends on assumed b |
| Damped wings visible | Wing shape | High, independent of b |
| Instrument unresolved, saturated structure | Lower limit only | Low; correction is model-dependent |
| Partial covering suspected | Doublet residual-flux ratios | Depends on covering model |

**What the data constrain versus what the model supplies**

*Data*: the transmitted flux at each pixel, hence τ_a(v); the equivalent width; line ratios for same-ion transitions, which test saturation; and lower limits on N wherever the core is black.

*Model*: the number of components; the b values; the decomposition of blended structure; the covering factor; the LSF shape (if poorly known); and any correction applied to a saturated AOD.

Practical recommendation: report the AOD-integrated column as a direct measurement, say explicitly whether the line is optically thin, state the Voigt result separately with the model assumptions, and quote lower limits when the core is saturated at the resolution and S/N of the data.

If you'd like, I can go through a specific case, such as a particular ion or an HST/COS versus a high-resolution echelle dataset, where the trade-offs differ.
