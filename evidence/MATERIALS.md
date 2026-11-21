# GitHub release status, 21 November 2026

The author requested public GitHub distribution of this curated evidence package. Release v1.0.0: https://github.com/Huangev587/llm-test-retention-artifact/tree/v1.0.0 . The same evidence is provided as Online Resource 2 (ESM_2.zip). This release supersedes the earlier local-only and undecided-access notes below; those notes are historical provenance, not the current access status. No new open licence is assigned to the authors' or third-party materials. Production source, full source-containing prompts, model weights and runtimes remain excluded. Journal submission is a separate author decision.

---

# Material and licence observations

Checked 16 November 2026. This is a provenance and packaging record. It does not assign a new licence to third-party files or represent completion of an institutional rights review.

| Component | Observed evidence | Packaged treatment and remaining action |
| --- | --- | --- |
| MUTGEN HumanEval-Java conversion | Prior source inventory reports no licence found. Four common root licence filenames at the fixed commit returned HTTP 404 this check. A fresh recursive GitHub tree request returned HTTP 403 (rate limit), so this is not a complete fresh tree audit. | Production source and full prompts that embed it are excluded. Keep fixed source links/hashes. Confirm the specific Java conversion's permission/provenance before redistributing that source. Root 404 results alone do not establish the complete legal status. |
| Original OpenAI HumanEval | The [Python upstream repository](https://github.com/openai/human-eval/blob/master/LICENSE) displays MIT terms. | No Python dataset is bundled. Its MIT terms are not treated as automatic clearance for another repository's Java conversion or additional contributions. |
| Apache Commons Codec 1.15 | Fixed-commit [LICENSE.txt](https://raw.githubusercontent.com/apache/commons-codec/c89d2af770f05457fbefa5fb4713c888bf177fb2/LICENSE.txt) is Apache 2.0; [NOTICE.txt](https://raw.githubusercontent.com/apache/commons-codec/c89d2af770f05457fbefa5fb4713c888bf177fb2/NOTICE.txt) contains upstream notices. | The two texts are retained byte-for-byte under `notices/`. Production source is not required for this offline scoring package. Any later source distribution must be prepared under the applicable licence/notice terms. |
| Qwen2.5-Coder-7B-Instruct | [Model repository LICENSE](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/raw/main/LICENSE) is Apache 2.0. Downloaded licence SHA256 matches the licence hash in the recorded model identity. | Licence text and existing file metadata retained; no weights/tokenizer redistributed. Four weight shards have recorded sizes and modification times but no saved content SHA256; the package does not invent a fully hashed model revision. |
| PIT, JUnit, JDK, Maven and Python/plotting dependencies | Versions are reported in the manuscript/run metadata. Dependency binaries and environments are not part of this artifact. | No blanket licence claim for these products. No environment installation or binary redistribution is performed. |
| Project analysis code, result data, generated test outputs and figures | New study materials and project analysis routines; creator/author and institutional rights confirmation still pending. Model output does not by itself grant rights to all referenced third-party content. | Included for local author review. Author-approved software/data licences and any required exclusions must be determined before an open deposit. No MIT/CC licence or permission to publish is assigned by this preparation. |

The online checks and their precise scope are recorded in `notices/licensing_observations.json`. Where content is reused, `provenance.json` identifies the actual source file and its SHA256 rather than relying on a mutable web page alone.

The lack of a confirmed redistribution route for the historical production source does not change the saved scores or require new experiments. The offline calculation does not need that source. It does limit claims about a fully executable public generation/validation package. Access to the preserved original workspace is not replaced by an unsupported “available on request” promise.

## Release decisions still needed

1. Authors/institution choose the rights and licences for the project's own code and data.
2. Establish an actual supplementary-file identifier or repository access route; verify its content against the final artifact manifest.
3. If production Java or full source-containing prompts are to be added, finish the corresponding third-party permission/provenance check first. Otherwise describe the omission and retain fixed acquisition links.

No material has been uploaded or made public as part of this check.
