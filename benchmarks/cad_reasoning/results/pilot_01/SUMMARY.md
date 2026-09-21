# Observed results

27 of 27 planned runs recorded; 27 uniformly re-scored with the corrected Python wrapper.

| Effort | Source | Construction | Repair | All cases passed | Mean CLI seconds | Input tokens | Cached input | Output tokens | Reasoning tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| medium | 3/3 | 3/3 | 3/3 | 9/9 | 27.4 | 133,512 | 0 | 6,457 | 2,256 |
| high | 3/3 | 3/3 | 3/3 | 9/9 | 37.8 | 133,512 | 0 | 9,121 | 4,676 |
| xhigh | 3/3 | 3/3 | 3/3 | 9/9 | 71.9 | 133,530 | 0 | 20,074 | 15,664 |

Output and reasoning fields are reported as returned by the CLI; do not add them together to infer billed tokens. Each task is all-or-nothing against fixed hard checks.

## Failures

None among completed trials.

## Limits

- Three distinct tasks; three repetitions per setting are not nine distinct problems.
- Tool use prohibited and audited. Not an autonomous CAD workflow comparison.
- CAD functions scored on nominal and varied dimensions plus STEP checks.
- Shared project-derived source interpretation is a reviewed reference, not metrology.
- Cached input and requested settings recorded; no billed-cost estimate or returned-model attestation.

For raw evidence see each trial directory: request, CLI events, answer, result, grading checks and native/STEP artifacts.
