# Online Resource 2: Test retention study evidence

Version `20261124-esm2-r8-em64` for *Test Retention in Evaluating LLM-Generated Unit Tests: Local Effects and Limits*, prepared for *Empirical Software Engineering*.

Authors: Wei Zheng, Shuhuan Lv, Xin Fan, Hao Pan, Fengyu Yang, Peng Xiao. Corresponding author: Shuhuan Lv, School of Software, Nanchang Hangkong University, Nanchang 330063, China. Email: ShuhuanLv@Outlook.com.

This ZIP accompanies the manuscript as supplementary material for peer review and for publication with the article upon acceptance. The archive is self-contained and can be used without a GitHub account.

Extract this archive into a fresh directory. From that directory, run the following command with Python 3.12, the version used to verify the draw sequence.

```sh
python -I -S -B verify.py
```

The verifier also reports the four-test profile across 52 equally weighted suites: the mean number killed and the number of suites at their fixed catalog ceiling. For each metric it reports the prefix value and the median and nearest-rank central 95% interval of 300 matched random draws. The prompt_templates directory contains the archived historical message-building functions and the local library prompt constructors as text for inspection, including instructions and variable insertion points. The results/form_decode_membership.json file lists the distinct valid method IDs and held-out kills for the initial Codec case.

The script verifies file checksums, rebuilds Tables 6, 8, 10 and 12 and compares the numeric rows with the included manuscript. It uses the Python standard library and runs offline. Generation, Java execution, correctness validation and timing were performed in the original study. This artifact reuses the stored outcomes of those runs.

| Evidence | Contents |
| --- | --- |
| Table 6 | The `library/` records contain the original responses and their positional validation outcomes, format recovery outcomes and mutant partitions. The manifest links each selection to the applicable PIT report. |
| Table 8 | `archives/core_evidence.zip` contains the scored prefixes and short-suite timeout evidence. `external/` contains the frozen primary plan and pair results including exclusions. The manifest links the excluded StackArray pair to the original and replayed full-suite reports. |
| Table 10 | The manifest maps each indexed method to its saved suite in the [third-party archive](https://doi.org/10.5281/zenodo.21230015). The verifier parses the raw PIT matrices and checks killed identities on 413 previously executed subsets before redoing the 300 draws. The seed is `20261118:source_id:d`, where `source_id` is the archive-relative suite path and draws are numbered 1–300. The draw intervals describe variation conditional on the saved pools. |

| Table 12 | `generation/evidence_remote.zip` preserves the frozen protocol, actual requests/responses, per-position validations, selection IDs, feedback partitions and raw PIT reports for the 81-call follow-up. The offline verifier checks all 72 scoring cells against 51 unique PIT reports, retained-source prompts and seeds. It reads this nested ZIP directly; no long-path extraction is required. The original execution paths are provenance only. |

`evidence.json` maps the files to the manuscript and `checksums.json` records their full SHA-256 digests. XML basenames use the first 32 characters of the original identifiers to meet the submission system's 64-character filename limit; indices and verifiers retain full identities and content checksums. This naming adaptation also applies to the historical and core nested archives, without changing XML contents. XMLs in `reports/` include the raw PIT reports and the original-program JUnit testcase outcomes for the matrix suites. The JUnit copies retain testcase names and outcome tags plus the original report hash. The server workspace prefix is masked in validation diagnostics and in the historical review copy. Files in `results/` are the reference matrix summary and its previous independent audit.

For the historical replay and initial six Codec APIs, extract `archives/historical_replication.zip` separately and run its included `verify.py`. To reproduce the form-decoding attribution and third-party prefix counts with the earlier verifier, run `python -I -S -B archives/core_evidence.zip` from the artifact directory.

`MATERIALS.md` describes the contents and points to the source and licence records. The bundle includes generated responses, validation records and report evidence. The fresh-generation archive includes its full prompts and focal Commons Codec source excerpts; generation/CODEC_LICENSE.txt and CODEC_NOTICE.txt preserve the upstream Apache license and notice. Full prompts from earlier stages, production source trees, model weights and external runtimes remain with their respective sources. This package does not assign a new open-source or open-data licence to its contents; existing third-party notices remain applicable.
