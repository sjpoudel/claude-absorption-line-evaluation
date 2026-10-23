# Contributions and artifact provenance

## Roles

- **Suraj Poudel:** project participant and domain scientist; asked questions through Claude, shared its answers and artifacts, and requested this GitHub package. The visible record shows a guided learning workflow, not an independent development history.
- **Claude:** original scientific answers, audit, numerical implementations, plots, and reported outputs.
- **ChatGPT:** proposed exercises and follow-up prompts; identified numerical errors and overstatements; inspected both scripts; independently reran experiment 1 during the earlier review; packaged and made output paths portable. Some original review statements also need qualification; see SCIENTIFIC_REVIEW.md.

## What was available

The conversation contains user-pasted Claude answers and two uploaded archives. It does not contain a Claude-native chat export, model identifier, complete tool history, or independent record of the user's execution environment. No claim of Claude Code use is supported.

## Original artifacts

- `archive/files.zip`: original first script and figure.
- `archive/files_(1).zip`: original second script, figure, and console output.

Archives are byte-preserved. Figure copies initially come directly from those archives. Runnable script copies replace the `/mnt/user-data/outputs/` save path with repository-relative `figures/` and add pathlib setup. Numerical algorithms are unchanged.

## Validation

The first script was independently executed during ChatGPT review; its principal numbers matched the report. Both script copies are rerun during packaging, with stdout recorded separately under results/. This checks reproducibility in the packaging environment, not broad scientific validity. See packaging validation output for actual execution status.

## Claims not established

No systematic model evaluation, independently authored benchmark, new discovery, Claude Code experience, real-data validation, or independent measurement of covering fraction has been demonstrated. Model recovery is conditional on an exactly known LSF, fixed continuum, fixed centroid, common Gaussian opacity family, and the stated independent Gaussian noise model.
