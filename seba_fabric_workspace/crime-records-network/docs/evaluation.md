# Evaluation

## What is verified, and by what

| Level | Command | Cases | Establishes |
|---|---|---|---|
| Unit | `make test-chaincode` | 70 | Contract logic and every policy rule, against a mocked stub. Does not establish behaviour on Fabric. |
| Integration | `make test-backend` | 48 | API, chaincode and ledger operating together with real certificates. |
| End-to-end | `make smoke` | 11 | The cross-department scenario driven through the `peer` CLI as the seeded officers, with real endorsement. |
| Ledger | `make inspect` | 9 sections | Block contents, endorsement signatures, certificate attributes, key history, world state. |

The unit layer uses a mock stub, so it cannot observe Fabric-specific behaviour.
One known divergence is documented: the real `fabric-shim` returns an empty
buffer for a missing key where a naive mock returns `undefined`. The mock
reproduces the real semantics for this reason.

Coverage is approximately 97% of statements on the chaincode. Coverage measures
which lines the tests execute, not whether the behaviour is correct.

## Measurements

`experiments/measure.js` writes `experiments/results/live_fabric_measurements.{json,md}`.

Workload: 10 requests per seed over seeds {7, 21, 42, 99, 123}, giving 50 timed
submissions; verification measured 50 times. Latencies are client-observed and
include the REST layer, gateway, endorsement, ordering and commit wait.

| Quantity | Simulation | This implementation |
|---|---|---|
| Build latency p50, end to end | 11.10 ms | 2072.69 ms |
| — orderer batch wait (configured) | — | 2000 ms |
| — marginal processing cost | 11.10 ms | 72.69 ms |
| Verification latency p50 | 2.50 ms | 3.99 ms |
| Storage per audit event | 353.50 B | 857 B |

Two qualifications apply to this table and are repeated in the generated report:

**Build latency.** The end-to-end figure is dominated by the orderer's
`BatchTimeout`. The p50 is 2072.69 ms with a min–max spread of 82.4 ms, which is
the signature of a fixed batch wait rather than variable computation. The
quantity comparable to the simulation is the marginal cost. `BatchTimeout` is a
throughput/latency tuning parameter.

**Storage.** Not like-for-like. This implementation commits the full explanation
artifact inline; the simulation figure covers a leaner record. The difference
reflects record schema, not per-byte overhead introduced by Fabric.

## Attack replay

Six attacks, each asserted with an expected outcome. The script exits non-zero if
any attack is undetected, so a regression fails rather than passing silently.

| Attack | Detected by |
|---|---|
| Explanation-hash substitution | recomputation of the committed explanation hash |
| Off-chain record tampering | payload hash versus on-chain commitment |
| Unauthorised record injection | chaincode `clientIdentity` MSP check |
| Request backdating | schema allow-list and `stub.getDateTimestamp()` |
| Approval-token exposure | only `sha256(token)` is committed |
| Access-log tampering | hash chain plus on-chain anchor |

All six are blocked. These are integrity, authorisation and metadata-exposure
attacks. The compromised-signer attack is not included: on a live network it
requires a compromised MSP administrator key, which is a stronger assumption than
the simulation makes.

## Explanation quality

`experiments/evaluate-explanations.js` writes
`experiments/results/explanation_quality.{json,md}`. Six decisions covering six
distinct policy rules are rendered twice, once by the deterministic template and
once through the local model.

| Metric | Template | Model arm |
|---|---|---|
| Decisive-attribute coverage, mean | 1.00 | 0.92 |
| Full coverage rate | 1.00 | 0.83 |
| Decision-label fidelity | 1.00 | 1.00 |
| Counterfactual mentioned | 1.00 | 0.67 |
| Validator rejection rate | — | 0.50 |

The coverage rule is reimplemented from `decisive_attribute_text_coverage()` in
`src/seba/xai_quality.py` (line 117) so that figures are comparable with the
0.781 full-coverage rate reported in the paper.

Four qualifications:

1. **The template scores higher than the model.** The metric credits an
   explanation for naming the decisive attributes, which a template does on every
   input. The Python implementation describes it as "a weak textual proxy, not a
   human explanation-quality score." A template advantage is therefore the
   expected result and is not evidence against the model; it indicates that this
   metric does not measure fluency.

2. **The model arm measures displayed output, not raw model quality.** When the
   validator rejects a generation the arm falls back to template wording, and
   that text is scored. At a rejection rate of 0.50, a substantial share of the
   arm's score is template text.

3. **Four attribute hints were added** that the paper's hint table lacks
   (`subject.role`, `subject.clearance`, `object.recordType`, `subject.mspId`),
   because the Fabric policy uses attributes absent from the earlier synthetic
   schema. Without them those attributes could never be credited.

4. **The comparability claim is not itself verified.** The scoring function is a
   port, and the Python and JavaScript implementations have not been run on
   identical input and shown to agree. Until that check exists, "computed the
   same way as the paper" is an assertion rather than a demonstrated fact.

## Sample sizes

Latency uses 50 samples on a single host. Explanation quality uses six decisions.
These are sufficient to demonstrate that the mechanisms operate and to compare
orders of magnitude; they are not sufficient for confidence intervals. The
simulation-side results used 1,000 requests across five seeds.

## Reproducing the reported numbers

```bash
make up && make deploy && make seed
make ollama
ENABLE_EXPERIMENTS=1 make backend    # in a second terminal
make measure
make evaluate
```

`ENABLE_EXPERIMENTS=1` mounts the routes that deliberately corrupt off-chain
state for the tampering attacks. It is off by default.
