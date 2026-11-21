# Online Resource 2: Test retention study evidence

Version `20261121-rewrite-v6-github` for *Test Retention in Evaluating LLM-Generated Unit Tests: Local Effects and Limits*, prepared for *Empirical Software Engineering*.

Authors: Shuhuan Lv and Wei Zheng. Corresponding author: Wei Zheng, School of Software, Nanchang Hangkong University, Nanchang 330063, China; zhengwei@nchu.edu.cn; ORCID https://orcid.org/0000-0002-1890-8186.

Public repository: [https://github.com/Huangev587/llm-test-retention-artifact](https://github.com/Huangev587/llm-test-retention-artifact). Fixed release: [v1.0.0](https://github.com/Huangev587/llm-test-retention-artifact/tree/v1.0.0). The same evidence is packaged as Online Resource 2 (`ESM_2.zip`) for journal submission. The experimental evidence and numerical results are unchanged; public hosting does not mean that the paper has been submitted or accepted.

Extract this archive into a fresh directory. From that directory, run the following command with Python 3.12, the version used to verify the draw sequence.

```sh
python -I -S -B verify.py
```

The script verifies file checksums, rebuilds Tables 6, 8 and 10 and compares the numeric rows with the included manuscript. It uses the Python standard library and runs offline. Generation, Java execution, correctness validation and timing were performed in the original study. This artifact reuses the stored outcomes of those runs.

| Evidence | Contents |
| --- | --- |
| Table 6 | The `library/` records contain the original responses and their positional validation outcomes, format recovery outcomes and mutant partitions. The manifest links each selection to the applicable PIT report. |
| Table 8 | `archives/core_evidence.zip` contains the scored prefixes and short-suite timeout evidence. `external/` contains the frozen primary plan and pair results including exclusions. The manifest links the excluded StackArray pair to the original and replayed full-suite reports. |
| Table 10 | The manifest maps each indexed method to its saved suite in the [third-party archive](https://doi.org/10.5281/zenodo.21230015). The verifier parses the raw PIT matrices and checks killed identities on 413 previously executed subsets before redoing the 300 draws. The seed is `20261118:source_id:d`, where `source_id` is the archive-relative suite path and draws are numbered 1–300. The draw intervals describe variation conditional on the saved pools. |

`evidence.json` maps the files to the manuscript and `checksums.json` records their SHA-256 digests. XMLs in `reports/` are named by content digest and include the raw PIT reports and the original-program JUnit testcase outcomes for the matrix suites. The JUnit copies retain testcase names and outcome tags plus the original report hash. The server workspace prefix is masked in validation diagnostics and in the historical review copy. Files in `results/` are the reference matrix summary and its previous independent audit.

For the historical replay and initial six Codec APIs, extract `archives/historical_replication.zip` separately and run its included `verify.py`. To reproduce the form-decoding attribution and third-party prefix counts with the earlier verifier, run `python -I -S -B archives/core_evidence.zip` from the artifact directory.

`MATERIALS.md` records source and licence observations and the current GitHub and supplementary-file access routes. The bundle includes generated responses, validation records and report evidence. Full prompts, production source trees, model weights and external runtimes remain with their respective sources. This package does not assign a new open-source or open-data licence to its contents; existing third-party notices remain applicable. The author requested GitHub distribution on 21 November 2026. Final approval for journal submission remains a separate decision.
