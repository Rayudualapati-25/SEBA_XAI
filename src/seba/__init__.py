"""SEBA-XAI: Secure Explainable Blockchain-Audited Access Overlay.

This package re-homes the SEBA-XAI work from the original ``prototype/`` scripts
into a testable, importable Python package. The original scripts under
``prototype/synthetic_access_sim/`` remain runnable; new mechanism work
(NS-PI policy induction, attack catalog, scorers) is built here.

The locked contribution sentence for the first paper lives in
``CONTRIBUTION.md`` at the repo root. Every module added to this package must
support, evaluate, or measure against that sentence.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
