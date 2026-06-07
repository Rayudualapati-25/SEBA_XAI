# Iteration 020 - Prototype Learning Syllabus

Date: 2026-05-28

## What Worked

- Created a dedicated syllabus for learning the SEBA-XAI prototype in technical detail.
- Kept the general Blockchain/XAI course separate from the implementation-specific learning path.
- Mapped the original simulator, the newer `src/seba/` research package, experiments, outputs, tests, and current limitations into one student-friendly study document.

## What Was Added

- `blockchain_xai_course/SEBA_XAI_PROTOTYPE_SYLLABUS.md`

The syllabus covers:

- synthetic data generation;
- policy oracle validation;
- rule-trace XAI;
- mutable logs;
- signed hash chains;
- permissioned blockchain-style audit;
- off-chain storage;
- latency and storage overhead;
- policy ablation;
- schema and immutability;
- attack catalog;
- baseline defenses;
- AAS scoring;
- NS-PI learning;
- drift detection;
- counterfactual XAI;
- paper evidence pack;
- compromised-signer next experiment.

## What Is Weak Or Still Missing

- The syllabus is a study guide only. It does not add new experiments.
- The main research uncertainty remains unchanged: NS-PI has not yet been proven to beat cryptographic baselines under the current attack catalog.
- The next meaningful research step is still the `compromised_signer` attack.

## Next Recommended Step

Implement `src/seba/attacks/compromised_signer.py`, update detector behavior for re-signed valid chains, add tests, and rerun `make reproduce`.

