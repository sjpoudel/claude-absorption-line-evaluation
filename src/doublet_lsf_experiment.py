"""
Synthetic 2:1 absorption doublet, full covering, convolved with a Gaussian LSF.
Tests whether instrumental broadening alone can mimic partial covering.

Assumptions
-----------
* Both lines share one velocity frame (doublet components overlaid in v-space).
* tau_strong(v) = tau0 * exp(-(v/b)^2)  (Gaussian opacity; damping wings neglected).
* tau_weak = tau_strong / 2 at every v  (f*lambda ratio exactly 2:1).
* Covering factor C_f = 1, continuum = 1, no noise, no blends.
* LSF: normalized Gaussian, convolved in FLUX space (what a spectrograph does).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- setup ----------------
dv = 0.05                       # km/s pixel (oversampled so quadrature is exact enough)
b = 10.0                        # km/s
tau0_strong = 4.0               # peak tau of strong line -> weak peak = 2
fwhm_lsf = 15.0                 # km/s (R ~ 20,000)
sigma_lsf = fwhm_lsf / (2*np.sqrt(2*np.log(2)))

# Wide window: absorption is negligible beyond ~ +-5b; LSF wings out to ~ 8 sigma.
# Use a window much wider than both so the continuum recovers to 1 at the edges.
vmax = 400.0
v = np.arange(-vmax, vmax + dv/2, dv)

def make_profiles(tau0):
    ts = tau0*np.exp(-(v/b)**2)
    tw = 0.5*ts
    return np.exp(-ts), np.exp(-tw)

def gaussian_kernel(sigma):
    half = int(np.ceil(8*sigma/dv))
    x = np.arange(-half, half+1)*dv
    k = np.exp(-0.5*(x/sigma)**2)
    return k/k.sum()            # normalized: sum = 1

def convolve_flux(I, sigma):
    k = gaussian_kernel(sigma)
    pad = len(k)//2
    Ip = np.pad(I, pad, mode="constant", constant_values=1.0)  # continuum beyond window
    return np.convolve(Ip, k, mode="valid"), k

DEPTH_MIN = 0.10   # only evaluate where the strong line is >=10% deep (else 0/0 in the wings)

def apparent_Cf(Iw, Is, depth_min=DEPTH_MIN):
    """Standard 2:1 doublet solution: C = (1-Iw)^2 / (1 - 2Iw + Is).
    Evaluated only where 1-Is >= depth_min; the solution is ill-conditioned
    (0/0) where both lines approach the continuum."""
    num = (1 - Iw)**2
    den = 1 - 2*Iw + Is
    out = np.full_like(num, np.nan)
    ok = (1 - Is >= depth_min) & (den > 1e-12)
    out[ok] = num[ok]/den[ok]
    return out

def ew(I):
    return np.trapezoid(1 - I, v)

# ---------------- main case ----------------
Is, Iw = make_profiles(tau0_strong)
Is_o, k = convolve_flux(Is, sigma_lsf)
Iw_o, _ = convolve_flux(Iw, sigma_lsf)

# Intrinsic relation: Iw = Is^(1/2)
dev_int = Iw - np.sqrt(Is)
dev_obs = Iw_o - np.sqrt(Is_o)
C_int = apparent_Cf(Iw, Is)
C_obs = apparent_Cf(Iw_o, Is_o)

print("=== CHECKS ===")
print(f"LSF kernel sum                      : {k.sum():.12f}")
print(f"Intrinsic max|Iw - sqrt(Is)|        : {np.max(np.abs(dev_int)):.3e}  (machine precision expected)")
print(f"Continuum at window edges (obs)     : strong {Is_o[0]:.12f}/{Is_o[-1]:.12f}, weak {Iw_o[0]:.12f}/{Iw_o[-1]:.12f}")
print(f"Window half-width / b, / sigma_LSF  : {vmax/b:.0f}, {vmax/sigma_lsf:.1f}")
for name, a, bb in (("strong", Is, Is_o), ("weak", Iw, Iw_o)):
    e0, e1 = ew(a), ew(bb)
    print(f"EW {name:6s} intrinsic {e0:.6f}  observed {e1:.6f}  rel. diff {(e1-e0)/e0:+.2e}  (km/s)")
print(f"Min intrinsic Is, Iw                : {Is.min():.4f}, {Iw.min():.4f}")
print(f"Min observed  Is, Iw                : {Is_o.min():.4f}, {Iw_o.min():.4f}")
print(f"Observed deviation Iw - sqrt(Is)    : min {dev_obs.min():+.4f}, max {dev_obs.max():+.2e}")
i0 = np.argmin(np.abs(v))
print(f"Pixels used for C_f (depth>={DEPTH_MIN:.0%})      : {np.isfinite(C_obs).sum()} of {len(v)}")
print(f"Apparent C_f (intrinsic)            : min {np.nanmin(C_int):.6f}")
print(f"Apparent C_f (observed)             : min {np.nanmin(C_obs):.4f}, at v=0: {C_obs[i0]:.4f}")
print(f"Deviation at v=0 (observed)         : {dev_obs[i0]:+.4f}  (Iw_o={Iw_o[i0]:.4f}, sqrt(Is_o)={np.sqrt(Is_o[i0]):.4f})")
print(f"Jensen sign check (Iw_o <= sqrt(Is_o) everywhere): {np.all(dev_obs <= 1e-12)}")

# ---------------- sweep: size of the spurious C_f deficit ----------------
print("\n=== SWEEP: minimum apparent C_f from LSF alone (true C_f = 1) ===")
taus = [0.5, 1, 2, 4, 8, 16]
ratios = [0.25, 0.5, 1.0, 1.5, 2.0]     # FWHM_LSF / b_FWHM-ish: use FWHM/b
print("tau0_strong | " + " ".join(f"FWHM/b={r:4.2f}" for r in ratios))
for t in taus:
    row = []
    s_, w_ = make_profiles(t)
    for r in ratios:
        sg = r*b/(2*np.sqrt(2*np.log(2)))
        so, _ = convolve_flux(s_, sg)
        wo, _ = convolve_flux(w_, sg)
        c = apparent_Cf(wo, so)
        row.append(np.nanmin(c) if np.isfinite(c).any() else np.nan)
    print(f"{t:11.1f} | " + " ".join((f"{x:11.3f}" if np.isfinite(x) else "        n/a") for x in row))

# ---------------- plots ----------------
fig, ax = plt.subplots(2, 2, figsize=(12, 9))
m = np.abs(v) < 80

a = ax[0, 0]
a.plot(v[m], Is[m], "C3-", label="strong, intrinsic")
a.plot(v[m], Is_o[m], "C3--", label="strong, observed")
a.plot(v[m], Iw[m], "C0-", label="weak, intrinsic")
a.plot(v[m], Iw_o[m], "C0--", label="weak, observed")
a.axhline(1, color="gray", lw=0.5)
a.set_xlabel("v (km/s)"); a.set_ylabel("normalized flux")
a.set_title(f"Profiles (tau0={tau0_strong:g}:{tau0_strong/2:g}, b={b:g} km/s, LSF FWHM={fwhm_lsf:g} km/s)")
a.legend(fontsize=8)

a = ax[0, 1]
x = np.linspace(0, 1, 200)
a.plot(x, np.sqrt(x), "k-", lw=1.5, label=r"$I_w=I_s^{1/2}$ (full covering)")
a.plot(Is, Iw, "g.", ms=3, label="intrinsic")
a.plot(Is_o, Iw_o, "m.", ms=3, label="observed (LSF)")
a.set_xlabel(r"$I_{strong}$"); a.set_ylabel(r"$I_{weak}$")
a.set_title("Doublet relation in the flux-flux plane")
a.legend(fontsize=8)

a = ax[1, 0]
a.plot(v[m], dev_int[m], "g-", label="intrinsic")
a.plot(v[m], dev_obs[m], "m-", label="observed")
a.axhline(0, color="gray", lw=0.5)
a.set_xlabel("v (km/s)"); a.set_ylabel(r"$I_w-\sqrt{I_s}$")
a.set_title("Deviation from the full-covering relation")
a.legend(fontsize=8)

a = ax[1, 1]
a.plot(v[m], C_int[m], "g-", label="intrinsic")
a.plot(v[m], C_obs[m], "m-", label="observed")
a.axhline(1, color="gray", lw=0.5)
a.set_ylim(0, 1.1)
a.set_xlabel("v (km/s)"); a.set_ylabel(r"apparent $C_f(v)$")
a.set_title("Apparent covering fraction (true $C_f=1$)")
a.legend(fontsize=8)

plt.tight_layout()
plt.savefig(FIGURES / "doublet_lsf_experiment.png", dpi=140)
