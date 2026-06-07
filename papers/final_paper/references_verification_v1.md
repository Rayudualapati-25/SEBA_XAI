# Reference Verification Notes v1

Created: 2026-05-30
Status: working verification note for `references_ieee_map.md`; not a final
IEEE bibliography.

## 1. Purpose

This note records what was checked during the reference-cleanup pass for the
SEBA-XAI paper. It exists so later paper edits do not reintroduce guessed
author names, unverifiable citations, or mismatched DOIs.

## 2. Verified Entries

The following entries in `papers/final_paper/references_ieee_map.md` were
checked against publisher, DOI, arXiv, CEUR/dblp, PubMed, MDPI,
ScienceDirect, SciTePress, J-GLOBAL/CoLab, ORCA/Rutgers, or PMC metadata where
available:

| Ref | Status | Notes |
|---:|---|---|
| [6] | verified | Fabric+ABAC paper metadata checked against ScienceDirect/DOI. |
| [7] | verified | Two-level digital crime evidence blockchain paper checked against MDPI/PubMed metadata. |
| [8] | verified | LEChain paper checked against ScienceDirect/DOI metadata. |
| [10] | verified | Law-enforcement XAI paper checked against Frontiers metadata. |
| [13] | verified | Fabric digital evidence management paper checked against JIPS metadata. |
| [14] | verified | Auditable blockchain access-control paper checked against IEEE/dblp metadata. |
| [15] | verified | Blockchain access-control survey checked against arXiv metadata. |
| [16] | verified | Accountable privacy-preserving blockchain access-control paper checked against ScienceDirect/DOI metadata. |
| [17] | verified | PPML survey checked against arXiv metadata. |
| [18] | verified | Differential privacy paper checked against ACM/DOI metadata. |
| [20] | verified | Fair prediction/disparate impact paper checked against DOI metadata. |
| [21] | verified | Fair risk-score trade-off paper checked against arXiv metadata. |
| [22] | verified | Dialogue-based XAI paper checked against CEUR proceedings metadata. |
| [23] | verified | Legal AI blockchain-audit paper checked against Engineering Applications of AI/DOI metadata. |
| [24] | verified | XAI-justice blockchain paper checked against MDPI metadata. |
| [25] | corrected and verified | Earlier local notes had incorrect venue details; current entry is Computers and Electrical Engineering, vol. 109, article 108761, DOI `10.1016/j.compeleceng.2023.108761`. |
| [26] | verified | India murder-motive XAI paper checked against IEEE/J-GLOBAL metadata. |
| [27] | verified | CriX paper checked against SciTePress/ICAART metadata. |
| [28] | verified | IndianBailJudgments-1200 checked against arXiv metadata. |

## 3. Remaining Bibliography Work

The current map has no remaining "Author details to verify" markers. The
remaining work is stylistic and consistency-focused:

1. Convert all entries to final IEEE punctuation and capitalization.
2. Add access dates for web-only references such as PIB, MHA, NIST landing
   pages, NCRB/data.gov.in, and arXiv/CEUR pages if required by the target
   venue.
3. Standardize conference abbreviations and venue names.
4. Confirm final ordering after the manuscript stops moving sections around.
5. Keep local artifact paths in Methodology/Results until a reproducibility
   appendix or artifact citation format is finalized.

## 4. Guardrails

- Do not add literature claims while doing bibliography cleanup.
- Do not infer author lists from memory.
- If a citation cannot be verified later, remove or replace it rather than
  leaving an unverifiable entry.
- Keep the distinction between official India sources, academic sources, and
  local experiment artifacts visible in the paper.
