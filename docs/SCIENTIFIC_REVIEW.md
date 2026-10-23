# Scientific review and remaining limitations

This file is the current editorial assessment. Original Claude answers are retained as historical material and contain errors.

## Initial answer

1. At 10^4 K, b_th(H) is about 12.9 km/s and b_th(Fe) about 1.73 km/s. Claude initially gave approximately 1 and 0.13 km/s.
2. A thermal lower bound on b needs a temperature lower bound; 10^4 K cannot simply be assumed.
3. Black core pixels alone supply optical-depth lower limits. Wings or additional transitions can constrain N; the entire spectrum cannot be reduced to the black core alone.
4. AOD avoids choosing discrete Voigt components but still needs continuum, covering, contamination, and resolution assumptions for inference.

## Audit still needs qualification

- A measured AOD column is not always a strict lower bound: noise, continuum errors, and blends can raise it. The smoothing inequality is an idealized result.
- AOD column conversion uses f and wavelength, not the damping constant Gamma. The audit's table incorrectly groups these together.
- The intrinsic doublet relation cannot generally be imposed directly on convolved observed pixels.
- The CMB is not a universal hard floor for gas kinetic temperature; do not use that audit statement as a general physical bound without an appropriate heating/cooling model.
- Voigt fitting does not intrinsically require Gaussian independent noise: other likelihoods and covariance models are possible. Neither a component-selection criterion nor treating a model's integration extent as automatically complete is universal.
- Damping-wing upper limits depend on coverage, continuum, blends, and sensitivity. A generic column-density threshold is not a substitute for a particular spectrum.
- The ideal observed AOD relation is -ln(LSF * exp(-tau)); optical depth itself is not what the spectrograph convolves.

## Experiment 1

The code matches the stated Gaussian setup. Equivalent-width conservation, intrinsic relation, and apparent covering factors reproduce on independent execution. The Jensen argument requires a common normalized nonnegative smoothing operator for both transitions. A different LSF between wavelengths changes the simple argument.

The minimum apparent covering fraction is chosen over an arbitrary depth mask and is not representative of the core. Pixel-level covering formulas become ill-conditioned near the continuum. Broadening can mimic a signature; this does not establish that all partial-covering claims are instrumental.

## Experiment 2

Noise is added after convolution and pixel binning, independently per detector pixel and per line. SNR_pix = SNR_resolution / sqrt(3), so sigma_pix = sqrt(3)/30 = 0.057735 for normalized continuum. This is consistent for the adopted independent constant-variance noise, not a general model for resampled UV spectra or source-count Poisson noise.

240 flux samples are fitted with two free parameters, so the chi-square degrees of freedom are 238. Forty LSF-width intervals across each velocity window describe spectral resolution, not a replacement for 120 independent detector-noise samples per line.

The fitting code fixes C_f=1 and v0=0, and assumes exact continuum and LSF. It estimates tau0 and b, not covering fraction. The figure label 'truth / fitted model: C_f=1' should be interpreted as imposed, not measured.

W_tau = integral(tau dv) is integrated optical depth, not flux equivalent width. It is proportional to column density for specified atomic data. No actual ion or wavelength was chosen to convert it into cm^-2.

The local Jacobian covariance is approximate. Reported 1-sigma coverage is 70.2% for tau0, 67.9% for b, and 73.7% for W_tau. The last is noticeably above 68.3%; symmetric intervals and nonlinear propagation are not perfectly calibrated.

Noise changes the selected depth mask and the denominator-validity selection, producing estimator/selection bias as well as scatter. The noisy median covering factor 0.744 need not equal the noiseless median 0.639. Calling noise 'scatter only' is too simple.

The global reduced chi-square includes many continuum pixels and can dilute local profile mismatch; inspect line-region residuals as well.

Changing truth/fit grid resolution reduces a numerical identity issue, but identical underlying model families still make this an ideal recovery check, not robustness to physical model mismatch.

## Next learning questions (not completed)

1. Why is flux, rather than optical depth, convolved?
2. Why does the direct formula give apparent C_f<1 for a fully covered source?
3. Why is fitting a fixed-covering model different from measuring covering?

Possible future extensions: free C_f, uncertain LSF/continuum, multiple unresolved components, realistic noise covariance, and evaluation of Claude's uncertainty and error detection. These are not presented as completed work.
