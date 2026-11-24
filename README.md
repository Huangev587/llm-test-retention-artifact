# Test retention in evaluating LLM-generated unit tests

Reproduction evidence for **Test Retention in Evaluating LLM-Generated Unit Tests: Local Effects and Limits**.

**Authors:** Wei Zheng, Shuhuan Lv, Xin Fan, Hao Pan, Fengyu Yang, Peng Xiao. School of Software, Nanchang Hangkong University, China. Corresponding author: Shuhuan Lv (ShuhuanLv@Outlook.com).

**Current release:** `v1.1.0` (24 November 2026); evidence snapshot `20261124-esm2-r8-em64`. Prepared for submission to *Empirical Software Engineering*. Publication here does not imply journal acceptance.

## Download the fixed replication package

Download [ESM_2.zip from v1.1.0](https://github.com/Huangev587/llm-test-retention-artifact/releases/download/v1.1.0/ESM_2.zip). The archive is publicly accessible without a GitHub account. Its SHA-256 is:

```
74633866b6c37b37f5c29596843f165bc11d1770c68c6dc76c22661cf953642b
```

The ZIP preserves the previously verified evidence exactly. This public download replaces the earlier plan to deliver the ZIP through the submission portal. Older delivery wording within the frozen files is historical. See [release notes](RELEASE_NOTES.md).

## Recompute the stored results

Extract the ZIP into a fresh directory. With Python 3.12, run:

```sh
python -I -S -B verify.py
python -I -S -B archives/core_evidence.zip
```

For the historical and initial six-API evidence, extract `archives/historical_replication.zip` into another fresh directory and run its `verify.py` with Python 3.12.

Alternatively, clone this repository, check out tag `v1.1.0`, and run the commands from `evidence/`.

The main verifier checks file hashes, reconstructs Tables 6, 8, 10, and 12, validates 52 test-mutant matrices against 413 executed subsets, and repeats 300 deterministic conditional draws. It also checks the fresh-generation experiment's 72 scoring cells against 51 distinct PIT reports for nine blocks and 81 recorded model calls.

These checks use the Python standard library, run offline, and need no GPU or paid model calls. They do not rerun model inference, Java validation, or original timing measurements.

## Contents and scope

- [Evidence README](evidence/README.md): instructions and table mappings.
- [Manifest](evidence/evidence.json) and [checksums](evidence/checksums.json).
- `evidence/library/`: original responses, validation and recovery records.
- `evidence/reports/`: PIT and JUnit evidence for matrix and subset checks.
- `evidence/external/`: frozen pair-selection and exclusion records.
- `evidence/generation/`: fresh-generation prompts, responses, validation and PIT evidence, with Apache source notices.
- `evidence/prompt_templates/`: historical message-building functions and local prompt constructors.
- `evidence/code/` and `evidence/verify.py`: offline analysis and checking.
- `evidence/archives/`: historical evidence and independent verification entries.
- `evidence/manuscript.md`: manuscript snapshot containing the checked tables.

The third-party Java test-suite archive remains at [its original Zenodo record](https://doi.org/10.5281/zenodo.21230015). Declaration order is not claimed to recover response order. Full production source trees, earlier full source-containing prompts, model weights, and runtimes are excluded. The fresh-generation archive contains actual prompts with focal Commons Codec excerpts and their licence and notice.

The 300 draws describe within-pool selection variation, not independent generation repeats or an equal-effectiveness null distribution.

## Citation, rights, and preservation

See [CITATION.cff](CITATION.cff) for six-author metadata and [RIGHTS.md](RIGHTS.md) for the current reuse terms. Public access is authorized; no blanket MIT or Creative Commons licence is assigned. Existing third-party licences remain applicable.

Funding: National Natural Science Foundation of China (Grant No. 62467005).

A Zenodo preservation record is being prepared. No Zenodo DOI is currently assigned to this version. Use the fixed release URL and version above in the meantime; the original third-party archive DOI is not the DOI of this replication package.
