"""Pure scoring of frozen selection plans and already parsed PIT records.

No execution, filesystem access, outcome-based selection, or external dependency.
Each input report must contain the complete scoped mutation universe, including
development mutants; only evaluation_ids contribute to scores. Raw PIT records
remain the evidence for per-mutant status. Five fixed draws describe within-run
selection sensitivity, never independent model-generation replications.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json


POSITION_RULES = ('positions_1', 'positions_4', 'positions_8')
DRAW_RULES = tuple('matched_random_' + str(index) for index in range(5))
MATCHED_RULES = ('matched_prefix',) + DRAW_RULES
VALID_STATUSES = frozenset(('KILLED', 'SURVIVED', 'NO_COVERAGE', 'TIMED_OUT', 'MEMORY_ERROR'))
RESOURCE_STATUSES = frozenset(('TIMED_OUT', 'MEMORY_ERROR'))
IDENTITY_FIELDS = frozenset(('mutated_class', 'method', 'descriptor', 'mutator', 'indexes', 'line'))


def _unique_ids(ids, label):
    if not isinstance(ids, (list, tuple)) or any(not isinstance(item, str) or not item for item in ids):
        raise ValueError(label + ' must contain nonempty string IDs')
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate ' + label)
    return set(ids)


def suite_hash(ids):
    """Historical suite identity, with explicit duplicate rejection."""
    _unique_ids(ids, 'test IDs')
    return hashlib.sha256(json.dumps(sorted(ids)).encode()).hexdigest()


def _plan_rows(plan):
    if not isinstance(plan, dict) or type(plan.get('k')) is not int or plan['k'] < 0:
        raise ValueError('Plan k must be a nonnegative integer')
    rows = plan.get('rows')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Plan rows must be a nonempty list')
    keys = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('arm'), str) or not row['arm']:
            raise ValueError('Plan row needs an arm')
        if row.get('rule') not in POSITION_RULES + MATCHED_RULES:
            raise ValueError('Unknown selection rule')
        key = (row['arm'], row['rule'])
        if key in keys:
            raise ValueError('Duplicate plan arm/rule: ' + str(key))
        keys.add(key)
        suite_hash(row.get('ids'))
        if row['rule'] in MATCHED_RULES and len(row['ids']) != plan['k']:
            raise ValueError('Matched cardinality differs from k: ' + str(key))
    return keys


def _validate_reports(hashes, reports, evaluation):
    validated = {}
    reference = None
    for digest in sorted(hashes):
        if digest not in reports:
            raise ValueError('Missing report for suite ' + digest)
        raw = reports[digest]
        if not isinstance(raw, list) or not raw:
            raise ValueError('Missing mutant records for suite ' + digest)
        by_id = {}
        for record in raw:
            if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not record['id']:
                raise ValueError('Invalid mutant ID in suite ' + digest)
            mutant_id = record['id']
            if mutant_id in by_id:
                raise ValueError('Duplicate mutant in suite ' + digest + ': ' + mutant_id)
            if not IDENTITY_FIELDS.issubset(record):
                raise ValueError('Missing mutant identity metadata in suite ' + digest + ': ' + mutant_id)
            if record.get('status') not in VALID_STATUSES:
                raise ValueError('Unresolved or unknown PIT status in suite ' + digest + ': ' + str(record.get('status')))
            by_id[mutant_id] = record
        if not evaluation.issubset(by_id):
            raise ValueError('Missing evaluation mutants for suite ' + digest)
        # The frozen parser emits identity metadata only, apart from status.
        # Include line and every metadata field: ID equality alone is insufficient.
        identities = {mutant_id: {key: value for key, value in record.items() if key != 'status'}
                      for mutant_id, record in by_id.items()}
        if reference is None:
            reference = identities
        elif set(identities) != set(reference):
            raise ValueError('Unequal mutant universes for suite ' + digest)
        elif identities != reference:
            raise ValueError('Mutant metadata identity drift for suite ' + digest)
        validated[digest] = by_id
    return validated


def _score(report, evaluation):
    statuses = Counter(report[mutant]['status'] for mutant in sorted(evaluation))
    return {'evaluation_mutants': len(evaluation),
            'killed_ids': sorted(mutant for mutant in evaluation if report[mutant]['status'] == 'KILLED'),
            'statuses': dict(sorted(statuses.items())),
            'undefined': not evaluation}


def score_api(original_plan, recovered_plan, reports, evaluation_ids):
    """Score both conditions on identical primary and resource-clean universes.

    Invalid or incomplete evidence raises ValueError, never a zero score.
    Unrelated reports do not affect validation or resource exclusions. The caller
    verifies concrete test representatives, report provenance and partitions.
    """
    evaluation = _unique_ids(evaluation_ids, 'evaluation IDs')
    original_keys = _plan_rows(original_plan)
    recovered_keys = _plan_rows(recovered_plan)
    if original_keys != recovered_keys:
        raise ValueError('Original/recovered plan arm/rule cells differ')
    if not isinstance(reports, dict):
        raise ValueError('Reports must map suite hashes to raw PIT records')
    hashes = {suite_hash(row['ids']) for plan in (original_plan, recovered_plan) for row in plan['rows']}
    validated = _validate_reports(hashes, reports, evaluation)
    excluded = {mutant for report in validated.values() for mutant in evaluation
                if report[mutant]['status'] in RESOURCE_STATUSES}
    clean_evaluation = evaluation - excluded
    output = {'evaluation_ids': sorted(evaluation), 'evaluation_mutants': len(evaluation),
              'resource_excluded_ids': sorted(excluded), 'resource_excluded_count': len(excluded),
              'resource_evaluation_ids': sorted(clean_evaluation),
              'compared_suite_count': len(hashes)}
    for name, plan in (('original', original_plan), ('recovered', recovered_plan)):
        rows = []
        for row in plan['rows']:
            digest = suite_hash(row['ids'])
            rows.append({**row, 'ids': list(row['ids']), 'suite_hash': digest,
                         'valid_methods': len(row['ids']), **_score(validated[digest], evaluation),
                         'resource_clean': _score(validated[digest], clean_evaluation)})
        output[name] = {'k': plan['k'], 'rows': rows, 'evaluation_ids': sorted(evaluation),
                        'resource_evaluation_ids': sorted(clean_evaluation)}
    return output


def _metrics(row, clean):
    score = row['resource_clean'] if clean else row
    return {'valid_methods': row['valid_methods'], 'ids': list(row['ids']),
            'suite_hash': row['suite_hash'], 'evaluation_mutants': score['evaluation_mutants'],
            'killed_count': len(score['killed_ids']), 'killed_ids': list(score['killed_ids']),
            'statuses': dict(score['statuses']), 'undefined': score['evaluation_mutants'] == 0}


def _difference(before, after, comparable=True):
    added = sorted(set(after['killed_ids']) - set(before['killed_ids']))
    lost = sorted(set(before['killed_ids']) - set(after['killed_ids']))
    return {'killed_delta': after['killed_count'] - before['killed_count'] if comparable else None,
            'added_killed_ids': added, 'added_killed_count': len(added),
            'lost_killed_ids': lost, 'lost_killed_count': len(lost)}


def _relation(left, right, undefined):
    if undefined:
        return None
    if left == right:
        return 'tie'
    return 'left_greater' if left > right else 'right_greater'


def summarize(condition_scored, clean=False):
    """Report counts, killed identities, ties, strict reversals and all five draws.

    ``condition_scored`` is score_api(...)["original"] or ["recovered"].
    A full set of nine frozen rules is required for every included arm. All-zero
    counts on an empty denominator have undefined relations and differences.
    """
    _plan_rows(condition_scored)
    by_arm = {}
    for row in condition_scored['rows']:
        by_arm.setdefault(row['arm'], {})[row['rule']] = _metrics(row, clean)
    for arm, rows in by_arm.items():
        if set(rows) != set(POSITION_RULES + MATCHED_RULES):
            raise ValueError('Missing summary rules for arm ' + arm)
    denominators = {row['evaluation_mutants'] for rows in by_arm.values() for row in rows.values()}
    if len(denominators) != 1:
        raise ValueError('Summary denominators differ across compared cells')
    denominator = denominators.pop()
    undefined = denominator == 0
    positions = {arm: {rule: rows[rule] for rule in POSITION_RULES} for arm, rows in by_arm.items()}
    gains = []
    for arm, rows in by_arm.items():
        before, after = rows['positions_4'], rows['positions_8']
        gains.append({'arm': arm, 'from_rule': 'positions_4', 'to_rule': 'positions_8',
                      'killed_4': before['killed_count'], 'killed_8': after['killed_count'],
                      'evaluation_mutants': denominator, 'undefined': undefined,
                      'valid_methods_4': before['valid_methods'], 'valid_methods_8': after['valid_methods'],
                      'test_count_delta': after['valid_methods'] - before['valid_methods'],
                      **_difference(before, after, not undefined)})
    pairs = []
    for left, right in combinations(by_arm, 2):
        counts = {position: (by_arm[left][position]['killed_count'], by_arm[right][position]['killed_count'])
                  for position in ('positions_4', 'positions_8')}
        relation4 = _relation(*counts['positions_4'], undefined)
        relation8 = _relation(*counts['positions_8'], undefined)
        changed = not undefined and relation4 != relation8
        tie_change = changed and 'tie' in (relation4, relation8)
        pairs.append({'left_arm': left, 'right_arm': right, 'relation_4': relation4, 'relation_8': relation8,
                      'left_killed_4': counts['positions_4'][0], 'right_killed_4': counts['positions_4'][1],
                      'left_killed_8': counts['positions_8'][0], 'right_killed_8': counts['positions_8'][1],
                      'evaluation_mutants': denominator, 'undefined': undefined,
                      'changed': changed, 'tie_change': tie_change, 'strict_reversal': changed and not tie_change})
    strict = [pair for pair in pairs if pair['strict_reversal']]
    tie_changes = [pair for pair in pairs if pair['tie_change']]
    k = condition_scored['k']
    comparable = k > 0 and not undefined
    matched = {'k': k, 'comparable': comparable,
               'reason': 'k_zero' if k == 0 else ('empty_evaluation_universe' if undefined else None),
               'draw_count': 5, 'independent_generation_replications': False,
               'interpretation': 'Five fixed shared-order draws are within-run selection sensitivity.', 'arms': []}
    for arm, rows in by_arm.items():
        prefix = rows['matched_prefix']
        draws = []
        for rule in DRAW_RULES:
            draw = rows[rule]
            difference = _difference(prefix, draw, comparable)
            draws.append({'rule': rule, **draw, **difference,
                          'delta_vs_prefix': difference['killed_delta'],
                          'test_ids_differ_from_prefix': set(draw['ids']) != set(prefix['ids'])})
        matched['arms'].append({'arm': arm, 'prefix': prefix, 'draws': draws})
    return {'k': k, 'resource_clean': bool(clean), 'evaluation_mutants': denominator,
            'undefined': undefined, 'positions': positions, 'position_gains': gains,
            'ordering_changes': {'pairs': pairs, 'pair_count': len(pairs),
                                 'strict_reversals': strict, 'strict_reversal_count': len(strict),
                                 'tie_changes': tie_changes, 'tie_change_count': len(tie_changes),
                                 'unchanged_count': sum(not pair['changed'] and not pair['undefined'] for pair in pairs),
                                 'undefined_count': sum(pair['undefined'] for pair in pairs)},
            'matched': matched}
