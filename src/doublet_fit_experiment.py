"""
Joint forward-model fit of a 2:1 doublet (C_f fixed to 1) through a known Gaussian LSF,
compared with the direct per-pixel covering-factor formula.

Forward model (identical structure for data generation and fitting):
    tau(v) -> flux exp(-tau) on a fine grid -> convolve with normalized Gaussian LSF
           -> average over detector pixels (pixel integration)
Data are generated on a 0.05 km/s fine grid; the fit uses a 0.5 km/s fine grid, so the
noiseless test also measures discretization error (it is not a pure "inverse crime").

Assumptions
-----------
* tau_strong = tau0 exp[-(v/b)^2], tau_weak = tau_strong/2, common velocity frame, v0 = 0 fixed.
* Continuum = 1 and known; LSF known exactly; no blends, no damping wings.
* Noise: Gaussian, independent between pixels and between the two lines, constant sigma
  (continuum-dominated; not Poisson-scaled with the signal).
* S/N = 30 per independent resolution element, with one resolution element = LSF FWHM.
  With N_RES pixels per FWHM and independent pixel noise: SNR_pix = SNR_res / sqrt(N_RES).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

rng = np.random.default_rng(20261022)

# ------------------------------------------------------------------ configuration
TAU0_T, B_T = 4.0, 10.0                    # true parameters (strong-line peak tau, km/s)
FWHM = 15.0                                # LSF FWHM, km/s
SIG_LSF = FWHM / (2*np.sqrt(2*np.log(2)))
VMAX, DPIX = 300.0, 5.0                    # window half-width and pixel size, km/s
NPIX = int(2*VMAX/DPIX)                    # 120 pixels
N_RES = FWHM / DPIX                        # 3 pixels per resolution element
SNR_RES = 30.0
SNR_PIX = SNR_RES/np.sqrt(N_RES)
SIG = 1.0/SNR_PIX                          # per-pixel sigma in continuum units
DEPTH_MIN = 0.10                           # mask for direct C_f formula
N_MC = 1000

class Forward:
    def __init__(self, dvf):
        self.dvf = dvf
        self.nsub = int(round(DPIX/dvf))
        self.vf = -VMAX + (np.arange(NPIX*self.nsub) + 0.5)*dvf
        half = int(np.ceil(8*SIG_LSF/dvf))
        x = np.arange(-half, half+1)*dvf
        k = np.exp(-0.5*(x/SIG_LSF)**2)
        self.k = k/k.sum()
        self.pad = half
        self.vpix = -VMAX + (np.arange(NPIX) + 0.5)*DPIX

    def intrinsic(self, tau0, b):
        ts = tau0*np.exp(-(self.vf/b)**2)
        return np.exp(-ts), np.exp(-0.5*ts)

    def convolve(self, I):
        Ip = np.pad(I, self.pad, mode="constant", constant_values=1.0)   # continuum beyond window
        return np.convolve(Ip, self.k, mode="valid")

    def observe(self, tau0, b):
        """Returns (strong, weak) pixel-binned convolved flux."""
        Is, Iw = self.intrinsic(tau0, b)
        return tuple(self.convolve(I).reshape(NPIX, self.nsub).mean(axis=1) for I in (Is, Iw))

FWD_TRUTH = Forward(0.05)
FWD_FIT = Forward(0.5)

# ------------------------------------------------------------------ fitting
LO, HI = [0.01, 1.0], [200.0, 100.0]

def fit(obs_s, obs_w, p0=(2.0, 8.0), fwd=FWD_FIT):
    def resid(p):
        ms, mw = fwd.observe(*p)
        return np.concatenate([(obs_s - ms)/SIG, (obs_w - mw)/SIG])
    r = least_squares(resid, p0, bounds=(LO, HI), jac="3-point", x_scale=[1.0, 5.0],
                      xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=200)
    J = r.jac
    cov = np.linalg.inv(J.T @ J)           # formal covariance (sigma already in residuals)
    chi2 = 2*r.cost
    return r.x, cov, chi2, r

def Wtau(tau0, b):                        # int tau_strong dv  (proportional to column density)
    return np.sqrt(np.pi)*tau0*b

# ------------------------------------------------------------------ direct covering-factor formula
def cf_direct(Iw, Is, depth_min=DEPTH_MIN):
    """C = (1-Iw)^2 / (1 - 2Iw + Is) on pixels with strong-line depth >= depth_min.
    Returns C (NaN if masked or denominator <= 0) and a mask array."""
    A = (1 - Iw)**2
    D = 1 - 2*Iw + Is
    mask = (1 - Is) >= depth_min
    C = np.full_like(A, np.nan)
    ok = mask & (D > 0)
    C[ok] = A[ok]/D[ok]
    return C, mask, D

def cf_sigma(Iw, Is):
    """First-order error propagation for per-pixel noise SIG on both lines."""
    A = (1 - Iw)**2
    D = 1 - 2*Iw + Is
    dCdIw = (-2*(1 - Iw)*D + 2*A)/D**2
    dCdIs = -A/D**2
    return SIG*np.sqrt(dCdIw**2 + dCdIs**2)

# ================================================================== run
print("="*72)
print("CONFIGURATION")
print(f" truth: tau0={TAU0_T}, b={B_T} km/s, C_f=1, W_tau=sqrt(pi) tau0 b={Wtau(TAU0_T,B_T):.4f} km/s")
print(f" LSF FWHM={FWHM} km/s (sigma={SIG_LSF:.3f}); pixel={DPIX} km/s; window=+-{VMAX:.0f} km/s; {NPIX} pixels")
print(f" pixels per resolution element = {N_RES:.2f}; SNR/res.el.={SNR_RES}; SNR/pixel={SNR_PIX:.3f}; sigma_pix={SIG:.4f}")
print(f" independent resolution elements across window = {NPIX/N_RES:.0f}")

# ---- sanity checks on the forward model
print("\n" + "="*72)
print("FORWARD-MODEL CHECKS")
for name, f in (("truth grid dv=0.05", FWD_TRUTH), ("fit grid   dv=0.50", FWD_FIT)):
    Is, Iw = f.intrinsic(TAU0_T, B_T)
    for lab, I in (("strong", Is), ("weak", Iw)):
        Ic = f.convolve(I)
        ew0 = np.sum(1 - I)*f.dvf
        ew1 = np.sum(1 - Ic)*f.dvf
        pix = f.convolve(I).reshape(NPIX, f.nsub).mean(axis=1)
        ew2 = np.sum(1 - pix)*DPIX
        print(f" {name} {lab:6s}: kernel sum={f.k.sum():.12f}  edges={Ic[0]:.12f}/{Ic[-1]:.12f}  "
              f"EW intrinsic={ew0:.6f}  convolved={ew1:.6f} ({(ew1-ew0)/ew0:+.1e})  pixel-binned={ew2:.6f} ({(ew2-ew0)/ew0:+.1e})")
ts_, tw_ = FWD_TRUTH.observe(TAU0_T, B_T)
tf_, wf_ = FWD_FIT.observe(TAU0_T, B_T)
print(f" discretization difference (fit grid vs truth grid), max |dI| = "
      f"{max(np.abs(ts_-tf_).max(), np.abs(tw_-wf_).max()):.2e}")

# ---- noiseless recovery (numerical recovery)
obs_s0, obs_w0 = FWD_TRUTH.observe(TAU0_T, B_T)        # noiseless data from the fine truth grid
print("\n" + "="*72)
print("NOISELESS RECOVERY  (numerical recovery; formal sigma = forecast for S/N=30)")
starts = [(2.0, 8.0), (0.5, 3.0), (10.0, 30.0), (30.0, 5.0), (4.0, 10.0)]
for p0 in starts:
    p, cov, chi2, r = fit(obs_s0, obs_w0, p0)
    print(f" start {str(p0):14s} -> tau0={p[0]:.6f}  b={p[1]:.6f}  chi2={chi2:.3e}  nfev={r.nfev}")
p_nl, cov_nl, chi2_nl, r_nl = fit(obs_s0, obs_w0, (2.0, 8.0))
sig_nl = np.sqrt(np.diag(cov_nl))
rho_nl = cov_nl[0, 1]/(sig_nl[0]*sig_nl[1])
g = np.sqrt(np.pi)*np.array([p_nl[1], p_nl[0]])
sigW_nl = np.sqrt(g @ cov_nl @ g)
print(f" fractional error  tau0: {(p_nl[0]-TAU0_T)/TAU0_T:+.2e}   b: {(p_nl[1]-B_T)/B_T:+.2e}   "
      f"W_tau: {(Wtau(*p_nl)-Wtau(TAU0_T,B_T))/Wtau(TAU0_T,B_T):+.2e}")
print(f" this is a numerical error (optimizer + 0.5 vs 0.05 km/s grid), NOT a statistical uncertainty")
print(f" Fisher forecast at S/N=30:  sigma(tau0)={sig_nl[0]:.3f} ({sig_nl[0]/TAU0_T:.1%})  "
      f"sigma(b)={sig_nl[1]:.3f} km/s ({sig_nl[1]/B_T:.1%})  corr={rho_nl:+.3f}  "
      f"sigma(W_tau)={sigW_nl:.3f} km/s ({sigW_nl/Wtau(TAU0_T,B_T):.1%})")

# ---- noiseless direct covering-factor formula on the pixelated data
C0, m0, D0 = cf_direct(obs_w0, obs_s0)
print(f"\n Direct C_f formula on NOISELESS pixels: n_used={m0.sum()}  median={np.nanmedian(C0):.4f}  "
      f"min={np.nanmin(C0):.4f}  max={np.nanmax(C0):.4f}")
cen = np.argsort(np.abs(FWD_TRUTH.vpix))[:2]
print(f"   central pixels (v={FWD_TRUTH.vpix[cen]}): C={C0[cen]}  (true C_f = 1; deviation is systematic, set by LSF)")

# ---- Monte Carlo at S/N = 30 per resolution element
print("\n" + "="*72)
print(f"MONTE CARLO: {N_MC} noise realizations at S/N={SNR_RES:.0f} per resolution element")
P = np.zeros((N_MC, 2)); S = np.zeros((N_MC, 2)); CH = np.zeros(N_MC); OK = np.zeros(N_MC, bool)
Wh = np.zeros(N_MC); sW = np.zeros(N_MC); CORR = np.zeros(N_MC)
Cmed = np.full(N_MC, np.nan); Ccen = np.full(N_MC, np.nan); Cbad = np.zeros(N_MC); Cn = np.zeros(N_MC)
single = None
for i in range(N_MC):
    ns = rng.normal(0, SIG, NPIX); nw = rng.normal(0, SIG, NPIX)
    os_, ow_ = obs_s0 + ns, obs_w0 + nw
    p, cov, chi2, r = fit(os_, ow_, (2.0, 8.0))
    P[i] = p; S[i] = np.sqrt(np.diag(cov)); CH[i] = chi2
    OK[i] = r.success and (LO[0]*1.001 < p[0] < HI[0]*0.999) and (LO[1]*1.001 < p[1] < HI[1]*0.999)
    Wh[i] = Wtau(*p); gg = np.sqrt(np.pi)*np.array([p[1], p[0]]); sW[i] = np.sqrt(gg @ cov @ gg)
    CORR[i] = cov[0, 1]/np.sqrt(cov[0, 0]*cov[1, 1])
    C, m, D = cf_direct(ow_, os_)
    Cn[i] = m.sum(); Cbad[i] = np.sum(m & (D <= 0))
    if np.isfinite(C).any():
        Cmed[i] = np.nanmedian(C)
    cc = C[cen]
    if np.isfinite(cc).all():
        Ccen[i] = cc.mean()
    if i == 0:
        single = dict(os=os_, ow=ow_, p=p, cov=cov, chi2=chi2, C=C, mask=m)

dof = 2*NPIX - 2
print(f" fit convergence/interior-of-bounds: {OK.sum()}/{N_MC}")
print(f" chi2/dof: mean={CH.mean()/dof:.3f}  (expected {1.0:.3f}+-{np.sqrt(2/dof):.3f} per realization; "
      f"std over MC={CH.std()/dof:.3f})")
ok = OK
def summ(name, x, truth, sig):
    pull = (x[ok] - truth)/sig[ok]
    q = np.percentile(x[ok], [16, 50, 84])
    print(f" {name:8s} truth={truth:8.3f} | mean={x[ok].mean():8.3f} median={q[1]:8.3f} "
          f"[16,84]=[{q[0]:.3f},{q[2]:.3f}] | MC std={x[ok].std():.3f} | median formal sigma={np.median(sig[ok]):.3f} "
          f"| pull mean={pull.mean():+.3f} std={pull.std():.3f} | |pull|<1: {np.mean(np.abs(pull)<1):.1%}")
    return pull
pull_t = summ("tau0", P[:, 0], TAU0_T, S[:, 0])
pull_b = summ("b[km/s]", P[:, 1], B_T, S[:, 1])
pull_W = summ("W_tau", Wh, Wtau(TAU0_T, B_T), sW)
print(f" correlation(tau0,b): formal median={np.median(CORR[ok]):+.3f}; MC sample={np.corrcoef(P[ok,0],P[ok,1])[0,1]:+.3f}")
print(f" Gaussian reference for |pull|<1 is 68.3%")

print("\n DIRECT PIXEL-LEVEL C_f FORMULA on the same noisy data (true C_f = 1)")
print(f"  pixels passing depth mask per realization: median {np.median(Cn):.0f}; "
      f"pixels with nonphysical denominator (<=0): mean {Cbad.mean():.2f} per realization")
cm = Cmed[np.isfinite(Cmed)]; cc_ = Ccen[np.isfinite(Ccen)]
print(f"  median-over-pixels C:  mean={cm.mean():.3f}  std={cm.std():.3f}  [16,50,84]={np.percentile(cm,[16,50,84]).round(3)}  "
      f"(noiseless value {np.nanmedian(C0):.3f})")
print(f"  central-pixel C:       mean={cc_.mean():.3f}  std={cc_.std():.3f}  [16,50,84]={np.percentile(cc_,[16,50,84]).round(3)}  "
      f"(noiseless value {C0[cen].mean():.3f})")
print(f"  fraction of realizations with median C < 0.9: {np.mean(cm<0.9):.1%};  central C < 0.9: {np.mean(cc_<0.9):.1%}")
print(f"  => offset from 1 persists at infinite S/N (systematic, LSF);  scatter is the statistical part")

# single realization
p1, cov1, chi21 = single["p"], single["cov"], single["chi2"]
print(f"\n single realization #0: tau0={p1[0]:.3f}+-{np.sqrt(cov1[0,0]):.3f}, b={p1[1]:.3f}+-{np.sqrt(cov1[1,1]):.3f}, "
      f"chi2/dof={chi21/dof:.3f}")

# ------------------------------------------------------------------ figure
fig, ax = plt.subplots(2, 3, figsize=(17, 9.5))
vp = FWD_FIT.vpix
sel = np.abs(vp) < 70

a = ax[0, 0]
ms1, mw1 = FWD_FIT.observe(*p1)
Is_i, Iw_i = FWD_TRUTH.intrinsic(TAU0_T, B_T)
mm = np.abs(FWD_TRUTH.vf) < 70
a.plot(FWD_TRUTH.vf[mm], Is_i[mm], "C3-", lw=1, alpha=0.5, label="strong, intrinsic (truth)")
a.plot(FWD_TRUTH.vf[mm], Iw_i[mm], "C0-", lw=1, alpha=0.5, label="weak, intrinsic (truth)")
a.errorbar(vp[sel], single["os"][sel], SIG, fmt="o", color="C3", ms=3.5, lw=0.8, label="strong, noisy data")
a.errorbar(vp[sel], single["ow"][sel], SIG, fmt="o", color="C0", ms=3.5, lw=0.8, label="weak, noisy data")
a.plot(vp[sel], ms1[sel], "k-", lw=1.4, label="C_f=1 model, fitted (LSF+pixel)")
a.plot(vp[sel], mw1[sel], "k-", lw=1.4)
a.set_xlabel("v (km/s)"); a.set_ylabel("normalized flux"); a.legend(fontsize=7)
a.set_title(f"Simultaneous fit, one realization (S/N={SNR_RES:.0f}/res. el.)")

a = ax[0, 1]
rs = np.concatenate([(single["os"]-ms1)/SIG, (single["ow"]-mw1)/SIG])
a.plot(vp, (single["os"]-ms1)/SIG, "C3.", label="strong"); a.plot(vp, (single["ow"]-mw1)/SIG, "C0.", label="weak")
a.axhline(0, color="k", lw=0.5); a.axhspan(-1, 1, color="gray", alpha=0.15)
a.set_xlim(-150, 150); a.set_xlabel("v (km/s)"); a.set_ylabel("(data - model)/sigma")
a.set_title(f"Residuals: chi2/dof = {chi21/dof:.2f} (dof={dof})"); a.legend(fontsize=8)

a = ax[0, 2]
a.plot(P[ok, 1], P[ok, 0], ".", ms=2.5, color="C2", alpha=0.35, label="MC fits")
cov_ref = cov_nl
vals, vecs = np.linalg.eigh(cov_ref[::-1, ::-1])   # (b, tau0) ordering
ang = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
for nsig, ls in ((1, "-"), (2, "--")):
    e = Ellipse((B_T, TAU0_T), 2*nsig*np.sqrt(vals[1]), 2*nsig*np.sqrt(vals[0]), angle=ang,
                fill=False, ec="k", ls=ls)
    a.add_patch(e)
bb = np.linspace(P[ok, 1].min(), P[ok, 1].max(), 100)
a.plot(bb, Wtau(TAU0_T, B_T)/(np.sqrt(np.pi)*bb), "C1:", label=r"$\tau_0 b$ = const")
a.plot(B_T, TAU0_T, "r*", ms=14, label="truth")
a.set_xlabel("b (km/s)"); a.set_ylabel(r"$\tau_0$"); a.legend(fontsize=7)
a.set_title("Parameter scatter vs formal 1σ, 2σ (Fisher) ellipses")

a = ax[1, 0]
xs = np.linspace(-4, 4, 200)
bins = np.linspace(-4, 4, 41)
a.hist(pull_t, bins, histtype="step", color="C0", density=True, label=r"$\tau_0$")
a.hist(pull_b, bins, histtype="step", color="C1", density=True, label="b")
a.hist(pull_W, bins, histtype="step", color="C2", density=True, label=r"$W_\tau$")
a.plot(xs, np.exp(-xs**2/2)/np.sqrt(2*np.pi), "k--", lw=1, label="N(0,1)")
a.set_xlabel("(estimate - truth) / formal sigma"); a.legend(fontsize=8)
a.set_title("Pull distributions (statistical calibration)")

a = ax[1, 1]
Cs = single["C"]; ms_ = single["mask"]
sg = cf_sigma(single["ow"], single["os"])
use = ms_ & np.isfinite(Cs)
a.errorbar(vp[use], Cs[use], sg[use], fmt="o", color="m", ms=4, lw=0.8, label="direct formula, noisy pixels")
a.plot(vp[m0], C0[m0], "b-", lw=2, label="direct formula, noiseless pixels")
a.axhline(1, color="g", lw=1.5, label=r"truth / fitted model: $C_f=1$")
a.set_ylim(-1, 2.5); a.set_xlim(-45, 45)
a.set_xlabel("v (km/s)"); a.set_ylabel("apparent $C_f$")
a.set_title("Direct per-pixel covering factor (error bars: 1st-order propagation)"); a.legend(fontsize=7)

a = ax[1, 2]
bins2 = np.linspace(-0.5, 1.8, 47)
a.hist(cm, bins2, histtype="step", color="m", label="median over pixels")
a.hist(cc_, bins2, histtype="step", color="C1", label="central pixels")
a.axvline(1, color="g", lw=2, label="truth ($C_f$=1)")
a.axvline(np.nanmedian(C0), color="b", ls="--", label="noiseless median")
a.set_xlabel("apparent $C_f$ from direct formula"); a.set_ylabel("MC realizations"); a.legend(fontsize=8)
a.set_title("Direct estimate: systematic offset + statistical scatter")

plt.tight_layout()
plt.savefig(FIGURES / "doublet_fit_experiment.png", dpi=130)
