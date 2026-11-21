# Test retention in evaluating LLM-generated unit tests

Reproduction evidence for **Test Retention in Evaluating LLM-Generated Unit Tests: Local Effects and Limits**.

**Authors:** Shuhuan Lv and Wei Zheng (corresponding author: zhengwei@nchu.edu.cn), School of Software, Nanchang Hangkong University, China.

**Version:** `v1.0.0` (21 November 2026); evidence version `20261121-rewrite-v6-github`.
The study is a manuscript in preparation; this repository does not imply journal acceptance.

## Reproduce the saved results

Use Python 3.12. No third-party Python packages, model API, GPU, Maven or Java installation are needed for this offline check.

```sh
git clone https://github.com/Huangev587/llm-test-retention-artifact.git
cd llm-test-retention-artifact
git checkout v1.0.0
cd evidence
python -I -S -B verify.py
python -I -S -B archives/core_evidence.zip
```

The first command verifies checksums, reconstructs main Tables 6, 8 and 10, checks 52 test-mutant matrices against 413 executed subsets, and repeats 300 deterministic draws. The second reconstructs the earlier case attribution and external-prefix analyses. For the historical and initial six-API evidence, extract `evidence/archives/historical_replication.zip` to a separate directory and run its `verify.py` there.

An equivalent ZIP is available under [Releases](https://github.com/Huangev587/llm-test-retention-artifact/releases/tag/v1.0.0). Its checksums and instructions are included. File bytes in `evidence/` are preserved exactly; adding files inside that directory can invalidate its integrity check.

## Contents and scope

- [Evidence instructions](evidence/README.md): table mappings and deterministic seed construction.
- [Checksums](evidence/checksums.json) and [evidence manifest](evidence/evidence.json).
- `evidence/library/`: 378 saved responses and validation records, partitions and recovery records.
- `evidence/reports/`: PIT execution reports and stripped JUnit outcomes; matrix and subset reports are keyed by their SHA-256.
- `evidence/external/`: pair-selection plan and inclusion/exclusion records (78 planned pairs across the two panels).
- `evidence/code/` and `evidence/verify.py`: offline reconstruction and checking.
- `evidence/archives/`: self-contained earlier evidence and verification entries.
- [Associated manuscript text](evidence/manuscript.md): the table version checked by the verifier.

This package recomputes **stored outcomes**. It does not regenerate LLM responses, rerun Java correctness checks or reproduce original wall-clock timings. Full production source trees, source-containing prompts, model weights and runtime binaries are excluded. The third-party Java suite archive is cited at [Zenodo](https://doi.org/10.5281/zenodo.21230015); its declaration order is not claimed to recover original response order.

The 300 draws describe selection variability within fixed saved pools; they are neither independent generation replicates nor an equal-effectiveness null distribution.

## Attribution and rights

Funding: National Natural Science Foundation of China (Grant No. 62467005).
See [CITATION.cff](CITATION.cff) for citation metadata and [MATERIALS.md](evidence/MATERIALS.md) for provenance, exclusions and existing third-party notices. Public access does not assign a new blanket MIT or Creative Commons licence. No new licence is granted to third-party material.
