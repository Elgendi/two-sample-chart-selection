"""Positive reporting of the existing minimum-payload, tolerance-constrained selector.

No fitted weights. Raw observations define the zero-compression reference.
This score measures eligible scalar-payload reduction, not perceptual performance.
"""
import math

def score_candidates(candidates, tolerance, n_raw):
    if n_raw <= 0 or not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('Require a positive raw count and finite nonnegative tolerance')
    rows = []
    for candidate in candidates:
        r = dict(candidate)
        finite = math.isfinite(r['error']) and r['error'] >= 0
        qualifies = finite and r['error'] <= tolerance * (1 + 1e-8)
        reduction = 100 * max(0.0, 1.0 - r['N'] / n_raw)
        r.update(score=reduction if qualifies else (0.0 if finite else float('nan')),
                 qualifies=qualifies,
                 score_status='qualifies' if qualifies else ('does_not_qualify' if finite else 'numerically_unavailable'),
                 n_raw=n_raw,
                 discrepancy_ratio=r['error']/tolerance if tolerance > 0 else (0.0 if r['error']==0 else float('inf')))
        rows.append(r)
    # Positive ties are equal retained sizes: discrepancy resolves them.
    # At zero, feasibility precedes size and discrepancy; unavailable comes last.
    rows.sort(key=lambda r: (-r['score'], not r['qualifies'], r['N'] if r['qualifies'] else r['error'], r['error'] if r['qualifies'] else r['N'])
              if math.isfinite(r['score']) else (float('inf'), True, float('inf'), r['N']))
    for i, r in enumerate(rows):
        r['order'] = i + 1
    return rows
