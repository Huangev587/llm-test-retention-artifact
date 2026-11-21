"""Recompute the manuscript's Tables 6, 8 and 10 from immutable evidence."""
import hashlib
import json
import math
import random
import re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "code"))

from scoring import score_api, suite_hash
from selection import ARMS, matched


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((ROOT / name).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def xml(digest):
    return ET.parse(ROOT / "reports" / f"{digest}.xml").getroot()


def mutant(row):
    klass, method, descriptor, mutator = [row.findtext(f) for f in (
        "mutatedClass", "mutatedMethod", "methodDescription", "mutator")]
    indexes = sorted(int(node.text) for node in row.findall("indexes/index"))
    identity = json.dumps([klass, method, descriptor, mutator, indexes], separators=(",", ":"))
    return dict(id=identity, mutated_class=klass, method=method, descriptor=descriptor,
                mutator=mutator, indexes=indexes, line=int(row.findtext("lineNumber")),
                status=row.attrib["status"])


def scoped_report(digest, scope):
    return [mutant(row) for row in xml(digest).findall("mutation")
            if row.findtext("mutatedClass") in scope and (
                "*" in scope[row.findtext("mutatedClass")] or
                row.findtext("mutatedMethod") in scope[row.findtext("mutatedClass")])]


def selection_plan(api, slots, seed):
    def prefix(arm, cap):
        return list(dict.fromkeys(slots[slot][i] for slot in ("seed", arm + "_1", arm + "_2")
                                  for i in sorted(slots[slot]) if i < cap))

    rows = [dict(arm=arm, rule=f"positions_{cap}", ids=prefix(arm, cap))
            for arm in ARMS for cap in (1, 4, 8)]
    match = matched(api, {a: prefix(a, 4) for a in ARMS}, {a: prefix(a, 8) for a in ARMS}, seed=seed)
    for arm, choices in match["arms"].items():
        rows.append(dict(arm=arm, rule="matched_prefix", ids=choices["prefix"]))
        rows.extend(dict(arm=arm, rule=f"matched_random_{n}", ids=ids)
                    for n, ids in enumerate(choices["random"]))
    return dict(k=match["k"], rows=rows)


def compare_scores(condition, expected_rows, clean=False):
    observed = condition["rows"]
    require(len(observed) == len(expected_rows), "Selection evidence count differs")
    for row, expected in zip(observed, expected_rows):
        keys = ("arm", "rule", "ids", "suite_hash", "valid_methods", "evaluation_mutants", "killed_ids", "statuses")
        require(all(row[key] == expected[key] for key in keys), f"PIT score differs for {row['suite_hash']}")
        if clean:
            require(row["resource_clean"] == expected["resource_clean"], "Common-mask score differs")


def library_metrics(condition):
    def reversal(clean):
        counts = {(r["arm"], r["rule"]): len((r["resource_clean"] if clean else r)["killed_ids"])
                  for r in condition["rows"]}
        return any((counts[a, "positions_4"] - counts[b, "positions_4"])
                   * (counts[a, "positions_8"] - counts[b, "positions_8"]) < 0
                   for a, b in combinations(ARMS, 2))

    k = condition["k"]
    different = any(len({len(r["killed_ids"]) for r in condition["rows"]
                         if r["arm"] == a and r["rule"].startswith("matched_")}) > 1 for a in ARMS)
    return [int(reversal(False)), int(reversal(True)), int(k > 0), int(k > 0 and different)]


def table2(manifest):
    columns = {name: [] for name in ("qwen", "granite", "granite format replay")}
    for item in manifest:
        api, model = item["api"], item["model"]
        slots = {}
        for slot, entry in item["responses"].items():
            response = ROOT / entry
            require(response.is_file(), f"Missing saved response {entry}")
            val = read(response.with_name("validation.json").relative_to(ROOT))
            slots[slot] = {m["index"]: m["id"] for m in val["methods"] if m["status"] == "PASS"}
        original = selection_plan(api, slots, item["seed"])
        require(original == item["original_plan"], f"Original selection differs for {model}/{api}")
        reports = {key: scoped_report(report, item["scope"]) for key, report in item["reports"].items()}
        evaluation = read(item["partition"])["evaluation_ids"]
        scored = score_api(original, original, reports, evaluation)["original"]
        compare_scores(scored, item["original_rows"])
        columns[model].append(library_metrics(scored))
        if model == "granite":
            for recovery in item["recovery"]:
                row = read(recovery["validation"])["methods"][0]
                response = ROOT / item["responses"][recovery["slot"]]
                require(sha(response.read_bytes()) == recovery["response_sha256"], "Recovery response differs")
                require(row["id"] == recovery["body_id"] and sha(row["source"].encode()) == recovery["source_sha256"],
                        "Recovered method differs")
                if row["status"] != "PASS":
                    continue
                selected = slots[recovery["slot"]]
                require(recovery["index"] not in selected, "Recovery overwrites an admitted position")
                selected[recovery["index"]] = row["id"]
            recovered = selection_plan(api, slots, item["seed"])
            require(recovered == item["recovered_plan"], f"Recovered selection differs for {api}")
            score = score_api(original, recovered, reports, evaluation)
            compare_scores(score["recovered"], item["recovered_rows"], clean=True)
            columns["granite format replay"].append(library_metrics(score["recovered"]))
    require([len(v) for v in columns.values()] == [24, 30, 30], "Wrong library panel sizes")
    return [[sum(api[n] for api in values) for values in columns.values()] for n in range(4)]


def transition(start, end, margin=0):
    start = 0 if abs(start) <= margin else start
    end = 0 if abs(end) <= margin else end
    if start * end < 0:
        return "strict_reversal"
    if start and not end:
        return "lead_to_tie"
    if end and not start:
        return "tie_to_lead"
    return "same_order"


def states(document, fixed):
    observed = {}
    for row in document.findall("mutation"):
        key = mutant(row)["id"]
        if key in fixed:
            require(key not in observed, f"Repeated fixed mutant {key}")
            observed[key] = row.attrib["status"]
    require(observed.keys() == fixed, "Report is missing fixed mutant identities")
    return observed


def external_prefix(exclusion):
    with zipfile.ZipFile(ROOT / "archives/core_evidence.zip") as core:
        data = json.loads(core.read("manifest.json"))
        fixed = {target: set(ids) for target, ids in data["catalogs"].items()}

        def report(digest, target):
            raw = core.read(f"pit/{digest}.xml")
            require(sha(raw) == digest, "Core report digest differs")
            return states(ET.fromstring(raw), fixed[target])

        gaps = defaultdict(dict)
        planned = Counter()
        for case in data["pairs"] + data["short_suites"]:
            cap, target, pair = case.get("upper", 8), case["target"], case["pair"]
            planned[cap] += 1
            if case.get("status", "COMPARED") != "COMPARED":
                require(case["timeout_reports"] and all("TIMED_OUT" in report(d, target).values()
                                                        for d in case["timeout_reports"]), "Missing short-suite timeout")
                continue
            gaps[cap][pair] = [sum(s == "KILLED" for s in report(a, target).values()) -
                               sum(s == "KILLED" for s in report(b, target).values()) for a, b in case["reports"]]

    catalog = {mutant(row)["id"] for row in xml(exclusion["catalog"]).findall("mutation")}
    before = states(xml(exclusion["published_full"]), catalog)
    after = states(xml(exclusion["replayed_full"]), catalog)
    require(any(before[k] == "KILLED" and after[k] == "TIMED_OUT" for k in catalog), "Missing primary timeout")
    require(exclusion["pair"] not in gaps[8], "Excluded primary pair also scored")
    planned[8] += 1
    rows = []
    for cap in (8, 5, 6, 7):
        events = Counter(transition(*g) for g in gaps[cap].values())
        require(events["strict_reversal"] == 0, f"Strict reversal in declaration-order cap {cap}")
        rows.append([planned[cap], len(gaps[cap]), *(events[t] for t in ("lead_to_tie", "tie_to_lead", "same_order"))])
    return rows, gaps, fixed


def matrix_for(suite, fixed):
    document = xml(suite["matrix"])
    results = states(document, fixed)
    methods = suite["methods"]
    require(len(methods) == len(set(methods)) and len(methods) >= 8, "Invalid matrix method order")
    junit = xml(suite["junit"]).findall("testcase")
    require(sorted(c.attrib["name"].removesuffix("()") for c in junit) == sorted(methods)
            and all(c.find(tag) is None for c in junit for tag in ("failure", "error", "skipped")),
            "Matrix suite did not execute all original-program tests")
    prefix = f"{suite['class']}.[engine:junit-jupiter]/[class:{suite['class']}]/[method:"
    suffix = "()]"

    def names(row, tag):
        refs = (row.findtext(tag) or "").split("|")
        require(all(ref.startswith(prefix) and ref.endswith(suffix) for ref in refs if ref), "Unexpected PIT test ID")
        values = {ref[len(prefix):-len(suffix)] for ref in refs if ref}
        require(values <= set(methods), "Matrix uses a method outside the recorded suite")
        return values

    matrix = {}
    for row in document.findall("mutation"):
        key = mutant(row)["id"]
        if key not in fixed:
            continue
        status = results[key]
        tags = ("killingTests", "succeedingTests", "coveringTests")
        require(status in {"KILLED", "SURVIVED", "NO_COVERAGE"}
                and (status == "NO_COVERAGE" or all(row.find(tag) is not None for tag in tags)),
                "Incomplete PIT matrix")
        killed, passed, covered = (names(row, tag) for tag in tags)
        require(bool(killed) == (status == "KILLED") and not killed & passed and killed | passed == covered,
                "Inconsistent matrix outcomes")
        matrix[key] = killed
    return matrix


def count_transitions(gaps, classes, margin):
    events = Counter()
    changed_by_class = Counter()
    for pair, gap in gaps.items():
        event = transition(*gap, margin)
        events[event] += 1
        changed_by_class[classes[pair]] += event != "same_order"
    return dict(changes=len(gaps) - events["same_order"], strict_reversals=events["strict_reversal"],
                lead_to_tie=events["lead_to_tie"], tie_to_lead=events["tie_to_lead"],
                class_equal_changes_pct=round(100 * statistics.mean(
                    changed_by_class[c] / n for c, n in Counter(classes.values()).items()), 6))


def table4(suites, gaps, fixed, archived):
    prefixes, random_gaps, classes = {}, [dict() for _ in range(300)], {}
    scores, subset_count = {}, 0
    require(len(suites) == 52, "Wrong matrix suite count")
    for suite in suites:
        pair, prompt, target = suite["pair"], suite["prompt"], suite["target"]
        require((pair, prompt) not in scores, "Duplicate matrix suite")
        classes[pair] = target
        methods = suite["methods"]
        matrix = matrix_for(suite, fixed[target])

        def kills(indices):
            selected = {methods[i] for i in indices}
            return {mutant_id for mutant_id, killers in matrix.items() if selected & killers}

        masks = set()
        for result in suite["executed_subsets"]:
            indices = result["indices"]
            mask = tuple(indices)
            require(mask not in masks, "Repeated reference subset")
            masks.add(mask)
            saved = states(xml(result["report"]), fixed[target])
            require(kills(indices) == {k for k, value in saved.items() if value == "KILLED"},
                    f"Executed subset differs for {pair}/{prompt}")
        subset_count += len(masks)
        values = [[len(kills(range(k))) for k in (4, 8)]]
        for draw in range(1, 301):
            indices = random.Random(f"{archived['random_seed']}:{suite['source_id']}:{draw}").sample(range(len(methods)), 8)
            if draw <= 3:
                require(all(tuple(sorted(indices[:k])) in masks for k in (4, 8)), "Initial draw differs from frozen subset")
            values.append([len(kills(indices[:k])) for k in (4, 8)])
        scores[pair, prompt] = values

    for pair in classes:
        left, right = (scores[pair, p] for p in ("zero_shot", "few_shot"))
        traces = [[x - y for x, y in zip(a, b)] for a, b in zip(left, right)]
        prefixes[pair] = traces[0]
        for d, trace in zip(random_gaps, traces[1:]):
            d[pair] = trace
    require(prefixes == gaps[8] and subset_count == 413, "Unexpected prefix gaps or reference subset count")
    short = [g for k in (5, 6, 7) for g in gaps[k].values()]
    prefix_row, random_row, short_row = [len(prefixes)], [len(prefixes)], [len(short)]
    for margin in (0, 1):
        obs = count_transitions(prefixes, classes, margin)
        draws = [count_transitions(draw, classes, margin) for draw in random_gaps]
        summary = {}
        for metric, prefix_value in obs.items():
            vals = sorted(d[metric] for d in draws)
            summary[metric] = dict(median=statistics.median(vals),
                                   central_95_pct_draw_interval=[vals[math.ceil(300 * p) - 1] for p in (0.025, 0.975)],
                                   draws_below_prefix=sum(x < prefix_value for x in vals),
                                   draws_equal_to_prefix=sum(x == prefix_value for x in vals),
                                   draws_above_prefix=sum(x > prefix_value for x in vals))
        expected = archived["tie_margins_killed_mutants"][str(margin)]
        require(dict(prefix=obs, draws=draws, random=summary) == expected, f"Random draw distribution differs at margin {margin}")
        keys = ("changes", "strict_reversals")
        prefix_row.extend(obs[k] for k in keys)
        random_row.extend(summary[k]["median"] for k in keys)
        short_events = [transition(*g, margin) for g in short]
        short_row.extend((sum(e != "same_order" for e in short_events), short_events.count("strict_reversal")))
    return [prefix_row, random_row, short_row], subset_count


def main():
    hashes = read("checksums.json")
    actual_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
    require(actual_files == set(hashes) | {"checksums.json"}, "Artifact file list differs")
    for path, expected in hashes.items():
        require(sha((ROOT / path).read_bytes()) == expected, f"Digest differs for {path}")
    manifest = read("evidence.json")
    primary, gaps, fixed = external_prefix(manifest["primary_exclusion"])
    randomized, subset_count = table4(manifest["matrices"], gaps, fixed, read("results/matrix_batch.json"))
    tables = {"6": table2(manifest["library"]), "8": primary, "10": randomized}
    require(tables == manifest["manuscript_tables"], "Recomputed values differ from the manuscript")
    source = (ROOT / "manuscript.md").read_text(encoding="utf-8")
    require(sha((ROOT / "manuscript.md").read_bytes()) == manifest["manuscript_sha256"], "Manuscript hash differs")
    for number, expected in tables.items():
        body = source.split(f"**Table {number}.", 1)[1]
        lines = re.search(r"(?:^\|.*\n)+", body, re.M)[0].splitlines()[2:]
        rows = [[int(v) for cell in line.strip('|').split('|')[1:] for v in cell.split('/')]
                for line in lines]
        require(rows == expected, f"Printed Table {number} differs from reanalysis")
    return dict(status="PASS", tables=tables, files=len(hashes), matrices=len(manifest["matrices"]),
                archived_subsets=subset_count, draws=300,
                library_responses=sum(len(row["responses"]) for row in manifest["library"]),
                paired_records=sum(row[0] for row in primary))


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
