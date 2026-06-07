# Iteration 025: Solid Research Blueprint

Date: 2026-05-29

## Goal

Clarify how SEBA-XAI can become a solid research project rather than a broad idea.

## What Worked

- Reviewed the current research gap, existing-model scan, session handoff, contribution sentence, results findings, and prototype artifacts.
- Confirmed that the project already has a research prototype, baselines, multi-seed tables, and an adversarial benchmark direction.
- Identified the main unresolved issue: the current NS-PI contribution is not yet proven because cryptographic detectors outperform NS-PI on ordinary logged-field tampering attacks.
- Created `16_make_seba_xai_solid_research.md` as a supervisor-style blueprint.

## What Is Weak

- The final novelty claim still depends on the `compromised_signer` experiment.
- If that experiment fails, the research should pivot honestly to an ADV-AUDIT benchmark/system-evaluation paper instead of forcing a method claim.

## Evidence Produced

- New research-hardening file: `16_make_seba_xai_solid_research.md`

## Next Step

Implement and evaluate the `compromised_signer` attack, then decide whether the first paper is a novel NS-PI method paper or an ADV-AUDIT benchmark paper.
