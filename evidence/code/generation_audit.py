"""Offline reconstruction of the nine generation-cap blocks; no Java or model calls."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def transition(a, b):
    a, b = (a > 0) - (a < 0), (b > 0) - (b < 0)
    return 'same_order' if a == b else ('strict_reversal' if a*b < 0 else ('lead_to_tie' if b == 0 else 'tie_to_lead'))


def table(data, valid=False):
    labels={'form_decode':'Form decode','hex_decode':'Hex decode','base64_urlsafe':'URL-safe Base64'}
    rows=['| Target | Seed | N | (4,4) G / M | (4,8) G / M | (8,4) G / M | (8,8) G / M |',
          '| --- | ---: | ---: | --- | --- | --- | --- |']
    for r in data['rows']:
        cells=[]
        for c,k in ((4,4),(4,8),(8,4),(8,8)):
            cells.append(' / '.join(str(r['scores'][f'{a}_{c}_{k}']['valid' if valid else 'killed']) for a in ('generic','mutation')))
        rows.append('| '+' | '.join([labels[r['api']],str(r['seed']),str(r['catalog']),*cells])+' |')
    return '\n'.join(rows)


def audit(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        def read(p):
            return json.loads(z.read(p))
        root = 'generation_cap/'
        out = root + 'outputs/'
        plan = read(root+'protocol.json')
        result = read(out+'results.json')
        batch = read(out+'batch.json')
        checked = read(root+'setup/checked.json')
        assert result['protocol_sha256'] == sha(z.read(root+'protocol.json'))
        assert batch['sources'] == checked['sources']
        for name in ('protocol.json', 'runner.py', 'prepare.py', 'start.sh'):
            assert sha(z.read(root+name)) == batch['sources'][name]
        assert sha(z.read('external_confirmation/freeze.json')) == batch['sources']['freeze.json']
        assert len(result['blocks']) == 9 and result['model_calls'] == 81
        assert len([n for n in z.namelist() if '/calls/' in n and n.endswith('/request.json')]) == 81
        rows, states, exposure, empty, calls = [], Counter(), [], [], 0
        validation_statuses, structural = Counter(), Counter()
        reports = set()
        expected = {(a,s) for a in plan['targets'] for s in plan['seeds']}
        assert {(b['api'],b['seed']) for b in result['blocks']} == expected
        for b in sorted(result['blocks'],key=lambda b:(list(plan['targets']).index(b['api']),b['seed'])):
            api, seed = b['api'], b['seed']
            folder = out+f'blocks/{api}/{seed}/'
            assert b == read(folder+'result.json')
            family = {'form_decode':'form','hex_decode':'hex','base64_urlsafe':'base64'}[api]
            split = read(f'external_confirmation/setup/{family}_partition.json')
            evaluation, feedback = set(split['evaluation_ids']), set(split['feedback_ids'])
            assert evaluation.isdisjoint(feedback)
            def pit(ids):
                key = sha(json.dumps(ids).encode())
                p = out+f'pit/{api}/{key}/'
                assert read(p+'ids.json') == ids
                saved = read(p+'mutants.json')
                raw = {}
                for m in ET.fromstring(z.read(p+'raw/mutations.xml')):
                    ident = json.dumps([m.findtext(k) for k in ('mutatedClass','mutatedMethod','methodDescription','mutator')]+[sorted(int(x.text) for x in m.findall('indexes/index'))],separators=(',',':'))
                    assert ident not in raw
                    raw[ident] = m.attrib['status']
                assert {r['id']:r['status'] for r in saved} == raw
                assert set(raw) == evaluation | feedback
                reports.add(p)
                return saved
            vals, reqs, methods = {}, {}, {}
            slots = ['initial']+[f'cap{c}_{a}_{i}' for c in (4,8) for a in ('generic','mutation') for i in (1,2)]
            for slot in slots:
                request = read(folder+f'calls/{slot}/request.json')
                response = read(folder+f'calls/{slot}/response.json')
                vpath = folder+f'validations/{slot}/'
                val = read(vpath+'output/result.json')
                assert response['text'] == z.read(vpath+'output/response.txt').decode()
                step = 0 if slot=='initial' else int(slot[-1])
                rng = int.from_bytes(hashlib.sha256(f'paired-cap-20261123/{api}/{seed}/{step}'.encode()).digest()[:8],'big') % 2**63
                assert request['seed']==rng and request['sampling']==plan['sampling']
                structural[val['structure_pass']] += 1
                for i,m in enumerate(val['methods']):
                    assert m['index']==i
                    validation_statuses[m['status']] += 1
                    if m['status']=='PASS':
                        recorded=read(vpath+f"methods/{m['id']}/result.json")
                        assert recorded['source']==m['source'] and recorded['status']=='PASS'
                        assert all(m['junit'][side]['status']=='PASS' for side in ('original','reference'))
                vals[slot],reqs[slot]=val,request
                calls+=1
            def select(history,cap):
                return list(dict.fromkeys(m['id'] for slot in history for m in vals[slot]['methods'][:cap] if m['status']=='PASS'))
            selections=read(folder+'selections.json')
            exposures=[]
            def register(slot):
                for m in vals[slot]['methods']:
                    if m['status']=='PASS': methods[m['id']]=m['source']
            register('initial')
            for cap in (4,8):
                for arm in ('generic','mutation'):
                    hist=['initial']
                    for step in (1,2):
                        slot=f'cap{cap}_{arm}_{step}'
                        ids=select(hist,cap)
                        user=reqs[slot]['messages'][1]['content']
                        retained=user.split('\nRetained tests:\n',1)[1].split('\nGenerate complementary tests.',1)[0]
                        assert retained=='\n'.join(methods[i] for i in ids)
                        exp=dict(slot=slot,generation_cap=cap,retained=len(ids),retained_only_from_late_positions=sorted(set(ids)-set(select(hist,4))),last_response_diagnostic_positions=min(cap,len(vals[hist[-1]]['methods'])) if arm=='mutation' else 0)
                        exposures.append(exp)
                        if arm=='mutation':
                            payload=json.loads(user.split('\nAvailable mutation metadata (indexed tables preserve complete visible entries):\n')[1])
                            raw=pit(ids)
                            allowed=sorted((r for r in raw if r['id'] in feedback),key=lambda r:r['id'])
                            methods_f=sorted({(r['method'],r['descriptor']) for r in allowed})
                            operators=sorted({r['mutator'] for r in allowed})
                            entries=[[methods_f.index((r['method'],r['descriptor'])),r['line'],operators.index(r['mutator']),r['indexes'],r['status']] for r in allowed]
                            assert payload['entries']==entries and payload['methods']==[list(m) for m in methods_f] and payload['operators']==operators
                        register(slot)
                        hist.append(slot)
                    for replay in (4,8):
                        cell=f'{arm}_{cap}_{replay}'
                        ids=select(hist,replay)
                        assert selections[cell]==ids
                        report=pit(ids)
                        statuses={r['id']:r['status'] for r in report if r['id'] in evaluation}
                        assert len(statuses)==len(evaluation)
                        killed=sorted(i for i,s in statuses.items() if s=='KILLED')
                        unresolved=sorted(i for i,s in statuses.items() if s not in ('KILLED','SURVIVED','NO_COVERAGE'))
                        score=b['scores'][cell]
                        assert score['valid']==len(ids) and score['catalog']==len(evaluation)
                        assert score['killed']==len(killed) and sorted(score['killed_ids'])==killed and sorted(score['unresolved'])==unresolved
                        assert not unresolved
                        if not ids: empty.append([api,seed,cell])
            assert exposures==b['feedback_exposure']
            exposure.extend(dict(api=api,seed=seed,**x) for x in exposures)
            for c in (4,8):
                for k in (4,8):
                    gap=b['scores'][f'generic_{c}_{k}']['killed']-b['scores'][f'mutation_{c}_{k}']['killed']
                    assert b['gaps'][f'{c}_{k}']==gap and b['gap_bounds'][f'{c}_{k}']==[gap,gap]
            for name,left,right in [('native_transition','4_4','8_8'),('seeded_replay_transition','4_4','4_8'),('matched_scoring_cap_transition','4_8','8_8')]:
                assert b[name]==transition(b['gaps'][left],b['gaps'][right])
                states[name+':'+b[name]]+=1
            rows.append(dict(api=api,seed=seed,catalog=len(evaluation),scores={k:{f:v[f] for f in ('valid','killed')} for k,v in b['scores'].items()},gaps=b['gaps']))
        return dict(status='AUDIT_PASS',blocks=len(rows),model_calls=calls,scored_cells=len(rows)*8,unique_pit_reports_checked=len(reports),unresolved=0,transitions=dict(states),empty_cells=empty,validation_statuses=dict(validation_statuses),structure_pass=structural[True],structure_failure=structural[False],late_context_requests=sum(bool(x['retained_only_from_late_positions']) for x in exposure),late_context_blocks=len({(x['api'],x['seed']) for x in exposure if x['retained_only_from_late_positions']}),rows=rows,result_sha256=sha(z.read(out+'results.json')),evidence_sha256=sha(Path(path).read_bytes()))


if __name__=='__main__':
    folder=Path(__file__).resolve().parent
    data=audit(folder/'evidence_remote.zip')
    (folder/'audit.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k not in ('rows','empty_cells')},indent=2))
