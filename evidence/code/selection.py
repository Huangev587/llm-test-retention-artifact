"""Outcome-blind selection; fixed response positions and matched valid counts."""
import hashlib
import json
import random

ARMS = ('generic', 'execution', 'mutation')
SEED = 'java-selection-breadth-20261115-v1'


def prefix_ids(responses, limit):
    return list(dict.fromkeys(m['id'] for response in responses for m in response[:limit] if m['status'] == 'PASS'))


def matched(api, prefix, pools, seed=SEED):
    k = min(len(prefix[a]) for a in ARMS)
    common = sorted({m for a in ARMS for m in pools[a]})
    orders = []
    for repeat in range(5):
        key = json.dumps([seed, api, repeat], separators=(',', ':')).encode()
        rng = random.Random(int.from_bytes(hashlib.sha256(key).digest(), 'big'))
        orders.append(rng.sample(common, len(common)))
    return {'k': k, 'arms': {a: {'prefix': prefix[a][:k], 'random':
            [sorted([m for m in order if m in set(pools[a])][:k]) for order in orders]} for a in ARMS}}


def suite_hash(ids):
    assert len(ids) == len(set(ids))
    return hashlib.sha256(json.dumps(sorted(ids)).encode()).hexdigest()
