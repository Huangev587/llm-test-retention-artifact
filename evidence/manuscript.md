# Test Retention in Evaluating LLM-Generated Unit Tests: Local Effects and Limits

**Authors:** Wei Zheng; Shuhuan Lv (corresponding author); Xin Fan; Hao Pan; Fengyu Yang; Peng Xiao

**Affiliation:** School of Software, Nanchang Hangkong University, Nanchang 330063, China

**Correspondence:** Shuhuan Lv; ShuhuanLv@Outlook.com

**ORCID (Wei Zheng):** https://orcid.org/0000-0002-1890-8186

**ORCID (Shuhuan Lv):** https://orcid.org/0009-0004-3873-6520

## Abstract

Evaluations of large language model (LLM) test generators often retain only part of each response. We examine this evaluation decision through paired post-generation replay, holding responses fixed while changing admission limits or selected subsets. Our Java replay evidence comprises 14 functions, 30 library interfaces, and an independent archive of zero-shot and few-shot suites. For form URL decoding, generic continuation moved from trailing mutation feedback at four eligible positions to leading at eight; two later tests explained all seven added mutant detections. Detection remained unchanged on 18 of 24 Qwen-extension interfaces. The external archive yielded no strict reversal under declaration-order prefixes: nine transitions among 26 pairs lay within the 6–16 central 95% draw interval from 300 nested random selections. All 15 shorter-suite transitions disappeared under a one-mutant tie margin. A separate fresh-generation experiment crossed generation-time and replay caps on three selected interfaces with three stochastic repeats, totaling 81 model calls. Native four-to-eight comparisons changed tie status in three of nine blocks without a strict reversal; replay alone captured two of those changes. These results distinguish local attributable reversals, ceiling-induced ties, and generation-trajectory effects. They support reporting retention units, actual test counts, paired scores, and tie rules together, while leaving population recurrence and cross-language transfer unestablished.

**Keywords:** large language models, unit test generation, test retention, mutation testing, paired replay, Java

## 1 Introduction

Large language models can generate a complete test class, several test methods, or a sequence of candidate tests in response to one request. Evaluating such outputs requires decisions beyond choosing a model and a prompt. The evaluator must extract methods, reject invalid candidates, decide how many positions to inspect, remove duplicates, and assemble the suite that will actually be executed. A reported mutation score therefore describes the tests admitted by this process. It need not describe every test the model produced.

Retention is one concrete decision in that process. An evaluation may keep the first method from each response, inspect the first four positions, or retain the first four methods that pass validation. These policies have different units. Under a position cap, an invalid early method consumes a position; under a valid-test quota, the evaluator may continue searching later output. Even when two policies admit the same number of tests, they can retain different assertions. A shared numerical cap is consequently insufficient to reconstruct the comparison unless the unit and admission procedure are also specified.

This issue arises in realistic comparisons of LLM-based test generators. A recent fine-tuning evaluation retained the first test from a response when comparing against a model that produced one test per focal method [3]. Other systems use execution or mutation feedback to produce additional candidates [1, 19, 20, 21]. Such choices can be appropriate for a study's budget and purpose. The question addressed here is what an observed comparison says about the saved generated output when its retention policy changes. Our main replay holds responses and their generation histories fixed. A separate, targeted follow-up changes retention during fresh generation to examine the boundary of that control.

The general relationship between suite size and test effectiveness is already established. Inozemtseva and Holmes show why suite size must be considered when interpreting coverage and effectiveness [18]. Mutation testing also depends on the chosen mutant population, its redundancy, and potentially equivalent mutants [22]. Our contribution is more specific than observing that additional tests may kill additional mutants. We trace how a retention decision changes a *paired comparison*, identify the saved methods responsible, and test the limits of that observation using equal-count controls and an independent archive.

A local example motivates the analysis. For form URL decoding, generic continuation killed four held-out mutants and mutation feedback killed nine under a four-position cap. Replaying the same responses with an eight-position cap yielded eleven and nine kills, respectively. Two generic tests at positions six and seven accounted for all seven additional detections. However, an isolated reversal cannot establish that retention broadly destabilizes comparisons. Most interfaces in our extension gained no detections, and the external archive produced tie transitions rather than strict reversals. The paper examines these observations together.

We organize the study around five research questions:

- **RQ1: How do retained-test limits affect detection across the saved local targets?** We report all evaluable historical functions, all six initial library interfaces, and all 24 Qwen extension interfaces, including unchanged and empty-pool cases.
- **RQ2: Which tests explain local changes, and does selection still matter at an equal valid-test count?** We connect response positions to test bodies and killed-mutant identities, then compare fixed-count prefixes with saved-pool draws.
- **RQ3: What changes occur under declaration-order retention in an independent archive?** We reproduce published full suites before comparing equal-size prefixes and retain exclusions in the accounting.
- **RQ4: How do the external transitions compare with conditional random selection and alternative tie rules?** We use checked test–mutant matrices to extend the executed subset controls to 300 deterministic draws.
- **RQ5: Does changing the cap during generation yield the same comparison as post-generation replay?** A follow-up uses fresh paired stochastic trajectories at both generation caps on three selected targets.

The contributions are threefold. First, the paired replay protocol makes the path from a retention decision to admitted tests and mutant detections inspectable. Second, the empirical results establish attributable local reversals alongside clear limits: unchanged targets, admission failures, and ceiling-induced ties. Third, conditional random selection and a fresh generation-cap follow-up distinguish saved-pool sensitivity from trajectory changes, supporting an explicit reporting procedure. We do not present G, E, and M as reproductions of complete published tools, nor claim that any of them is generally superior.

The research problem is not intrinsically tied to Java. A multi-test response in another language also requires an admission policy. Java supplies the implementation and evidence in this study through JUnit execution, PIT mutation reports, and compatible public archives. Porting the protocol to another language would require a corresponding extraction and execution adapter; the frequency and direction of its effects would need separate validation. Throughout the paper, the results refer to the Java corpora studied here.

Section 2 relates the study to test generation and evaluation research. Section 3 defines the replay protocol and evidence units. Section 4 answers RQ1–RQ5 with the main experimental results. Sections 5 and 6 discuss practical interpretation and validity, and Section 7 concludes. Online Resource 1 provides extended protocols and detailed evidence not needed to follow the main comparisons.

## 2 Background and Related Work

### 2.1 LLM-based test generation and feedback

Execution feedback can help an LLM repair or extend tests, but systems differ in what they return to the model and how they admit candidates. TestPilot generates JavaScript tests and retries unsuccessful candidates with execution information [19]. ChatUniTest combines focal context, generation, validation, and repair for Java [20]. CoverUp guides Python test generation using coverage information [21]. MutGen uses mutation information together with execution feedback in iterative generation [1]. These systems illustrate why the final executed suite depends on more than the initial prompt.

The G, E, and M response groups in our local study isolate three feedback descriptions within a shared experimental scaffold. They are generic continuation, execution feedback, and mutation feedback. All receive the source and retained tests, so G is not a condition without any execution-derived information: retained tests already reflect admission outcomes. The study compares replays of those response groups. It does not compare the end-to-end implementations of TestPilot, ChatUniTest, CoverUp, and MutGen, and their published effectiveness numbers are not used as baselines.

Practical test generation also involves context and selection. CATGen investigates contextual support and post-processing for reliable generation [5]. Work on heterogeneous prompting and execution feedback selects issue tests using additional signals [6]. Studies of fine-tuning and newer model versions further show that the generator itself is a moving experimental component [3, 4]. We hold that component fixed by reusing saved responses. This enables attribution to downstream selection while the separate generation-cap follow-up in Section 3.9 directly tests selected alternative trajectories.

### 2.2 Suite size, composition, and mutation-based assessment

Controlling test quantity is necessary when relating coverage to effectiveness [18], but equal quantity does not force two suites to exercise the same behaviors. A test–mutant matrix makes this distinction concrete: each method is associated with a set of killed mutants, and a suite's detection count is the size of their union. Two equally sized subsets can have different unions because their assertions target different behaviors or overlap to different degrees. Our fixed-valid-count controls measure that variation within the saved pools.

Mutation testing provides executable fault proxies, not a direct count of naturally occurring defects. Its interpretation depends on the mutation operators, the evaluated program scope, and the treatment of unresolved and equivalent mutants [22]. PIT supplies the execution outcomes used here [8]. We preserve each target's mutant identities across compared suites rather than comparing percentages computed from changing denominators. Resource-status sensitivity checks use a shared exclusion set for all compared suites of a target.

Recent work also examines the relation between coverage, mutation scores, and effectiveness of LLM-generated suites [15]. Our question concerns a different intervention: which saved tests are admitted before a fixed catalog is scored. We therefore distinguish a newly detected mutant, a change in which response group leads, and a transition to a tie. A one-mutant difference can produce an exact ranking change without providing strong evidence of a practically important advantage.

### 2.3 Evaluation choices and empirical scope

Empirical software engineering studies have examined whether findings remain stable as tools, benchmarks, or configurations change. Golmohammadi et al. revisit parameter choices in an evolving test-generation tool and explicitly connect their questions to a bounded tool and problem setting [23]. Our intervention is downstream of generation, but the methodological concern is related: a reported comparison is conditional on experimental choices that need to be visible to the reader.

CDBench evaluates LLM mutation and test generation through competitive games on executable Java tasks [24]. Its benchmark changes the interaction between generators, whereas our replay holds generated output fixed and changes downstream admission. We do not reuse its tests or infer that its model comparisons apply to our response groups. Guidelines for studies involving LLMs further motivate documenting model versions, experimental units, and study limitations [17].

Our external evidence comes from a public archive of zero-shot and few-shot Java test suites [16]. That archive is independent of our local generation, but it preserves source declarations rather than the original mapping from response positions to extracted methods. Its role is therefore to test *declaration-order prefix sensitivity*. It cannot independently reproduce the local response-position mechanism. This distinction is maintained in the research questions, result tables, and conclusions.

## 3 Study Design

### 3.1 Overview and units of evidence

The design combines a local response-level replay with an archive-level replay. Both keep the underlying saved tests fixed while changing the admitted subset. A separate follow-up crosses generation-time and replay caps using fresh stochastic responses. The local study can trace a method to its position in a model response; the external study can trace a method only to its declaration in an archived suite. Table 1 describes the evidence stages without treating them as interchangeable replications.

**Table 1. Corpora, retention units, and analytical roles.** The six original Codec APIs are part of the 30 replayed library APIs. The fresh-generation follow-up adds one focal API within the previously studied Base64 class, bringing the total to 31. The Granite extension revisits those six and includes the other 24; it does not add 30 new interfaces.

| Stage | Saved material | Compared retention | Main role |
| --- | --- | --- | --- |
| Historical replay | 14 Java functions; 98 logical response slots | First, first four, all eligible positions up to 32 | Diagnose local effects; 12 functions support held-out scoring |
| Initial Codec study | Six APIs; 42 logical response slots | One, four, eight positions per response | Trace additional detections across three behavior families |
| Qwen extension | 24 APIs; 168 logical response slots | Four and eight positions per response | Report target-level scope, including unchanged results |
| Granite extension | 30 APIs; 210 logical response slots | Four and eight positions per response | Check another model family and admission barriers |
| External primary panel | 27 frozen suite pairs; 26 evaluable | First four and first eight declarations per suite | Independent archive under equal counts |
| External shorter suites | 51 frozen pairs; 34 evaluable | First four and first five, six, or seven declarations | Describe the short-suite boundary |
| Conditional selection | The same 26 evaluable primary pairs | 300 nested random four/eight subsets | Locate prefix results within saved-pool variation |
| Fresh generation | Three Codec targets, three repeats; 81 new responses | Generation caps 4/8 crossed with replay caps 4/8 | Separate trajectory change from post-generation admission |

A logical response slot is a scheduled response in a trajectory, including a cached response reused in that slot. A target is a historical function or a library API with a declared mutation scope. A suite pair in the external archive matches one class, model, and generation round across two prompts. These units must not be summed into a single sample size. In particular, 300 draws from 26 saved pairs are not 7,800 independent generation experiments.

### 3.2 Local generation and replay boundary

The historical and initial Codec material uses Qwen2.5-Coder-7B-Instruct [7]. The extension adds Granite-3.3-8B-Instruct [10]. Historical generation used an input bound of 8192 tokens and an output bound of 1024 tokens. The library studies used local greedy decoding with bounds of 8192 input and 2048 output tokens and requested eight JUnit methods per response. The software subjects are Commons Codec 1.15, the pinned Commons Lang revision, and Joda-Time 2.12.7 [9, 11, 12]. Model and software identifiers are preserved with the evidence.

Each local trajectory contains a shared seed response and two continuation slots for each of G, E, and M. G receives source and retained tests. E additionally receives compilation and original-program execution information. M additionally receives results from the feedback mutation partition. These are response-source definitions within this study. They do not imply that G has no feedback, because its retained tests have already passed the admission procedure.

In the original library generation loop, the first four original positions were processed before each continuation, and jointly validated tests were retained. The later eight-position replay does not rewrite those continuation prompts. Thus, it asks which additional tests were already present in the saved trajectories and what they detect. It does not measure the generator that would have resulted from using eight positions throughout the feedback loop. Section 3.9 defines a separate fresh-generation experiment that changes the cap during the feedback loop; its results are kept distinct from this replay.

Greedy decoding fixes the decoding policy for the recorded runs; it does not establish that another model version, prompt, or repeated generation would produce the same responses. We make conditional statements about these saved outputs. The common responses across retention conditions are an experimental control for replay, not a substitute for independent generation replication.

### 3.3 Retention, validation, and deduplication

Table 2 distinguishes the operations that are otherwise easily described by the same phrase, “keep four tests.” A position cap is applied before validity is known. Invalid candidates occupy their original positions and do not cause later methods to move forward. A valid-test quota instead operates on the validated pool. The equal-count analysis uses the latter unit and is reported separately from the original-position replay.

**Table 2. Operational definitions used throughout the study.** A cap or quota applies to the unit in the middle column; changing units changes the intervention.

| Term | Unit | Operation |
| --- | --- | --- |
| Eligible position cap | Original positions within each response | Inspect positions up to the cap, then validate; failures are not backfilled |
| Admitted test count | Unique validated methods in the final suite | Count after joint validation and body-level deduplication |
| Common valid-test count k | Methods per response group and target | Use the minimum available count across G, E, and M under the four-position rule |
| Declaration-order prefix | Methods in an archived test class | Keep the first k declarations; original response positions are unknown |
| Strict reversal | Paired detection difference | The nonzero sign changes between retention conditions |
| Tie transition | Paired detection difference | A lead becomes a tie, or a tie becomes a lead |

We apply structural and method checks consistently across the compared caps. Joint validation requires compilation and successful execution against the original program and a separate reference binding, with the generated assertions preserved. Library tasks also enforce declared input domains. For example, form URL decoding uses canonical form-encoded inputs under a bounded decoded length and a reference based on the JDK decoder. The checks establish acceptance under those contracts and observed assertions; they do not prove a generated test correct on every possible input.

Rejected structures, compilation failures, original-program failures, reference mismatches, out-of-domain inputs, and unresolved contracts remain separate states. After validation, we deduplicate method bodies by tokens while ignoring method names, whitespace, and comments. This is a syntactic duplicate criterion. Methods that differ syntactically can still exercise the same behavior, so deduplication does not make their mutant detections disjoint.

Let $R_{t,g}$ contain the shared seed and two saved continuations for target $t$ and response group $g$. For position cap $k$, method $m_{r,i}$ from response $r$ enters the final suite only if its original position satisfies the cap and it passes validation $V_t$:

$$
T_{t,g,k}=\operatorname{dedup}\!\left(\bigcup_{r\in R_{t,g}}\{m_{r,i}:i\leq k,\ V_t(m_{r,i})=\mathrm{PASS}\}\right).
$$

The union is over responses, while the position test applies separately within each response. Consequently, cap four does not mean that a final suite contains exactly four methods. The admitted count also depends on invalid candidates, repeated responses, and duplicate bodies. All three quantities—eligible positions, validated occurrences, and unique suite methods—must remain distinguishable.

### 3.4 Mutation scoring and comparison outcomes

We used PIT 1.14.4 for the historical functions and local library studies, and PIT 1.20.1 for the external test–mutant matrices [8]. For the local study, we group mutation sites by class, method, descriptor, and source line before assigning sites to feedback and evaluation partitions. The evaluation partition is held out from mutation feedback, although program source remains visible to the model. This separates the mutation evidence used for continuation from the evidence used to score the resulting suite.

The historical evaluation excludes two functions from held-out comparison: function 0 has an unresolved contract, and function 2 has only one usable mutation site. All 14 remain in the response and validation accounting. The six Codec interfaces use three class-level mutant universes, so encoding and decoding within a family share a catalog containing overloads and code outside the focal direction. The extension narrows mutation scope to the declared methods and listed direct helpers. These protocols support comparisons within a target but not a pooled mutation score across stages.

For a fixed catalog $H_t$, let $K_t(T)$ be the set of mutants marked KILLED by suite $T$. We report $s_t(T)=|K_t(T)|$ and the catalog size $N_t=|H_t|$. A paired gap is $d_{t,a,b,k}=s_t(T_{t,a,k})-s_t(T_{t,b,k})$. A strict reversal requires opposite nonzero signs at the two caps. A tie transition involves one zero difference. A newly killed mutant can increase both suites equally and leave their comparison unchanged.

The primary scores retain each fixed catalog. The extension additionally removes, from every compared suite for a model and API, the same union of mutants marked TIMED_OUT or MEMORY_ERROR in any evaluated suite. This resource-status sensitivity check prevents a favorable comparison from being attributed merely to inconsistent handling of unresolved executions. The raw and common-exclusion results are both retained; unresolved executions are not silently relabeled as successful detections.

### 3.5 Equal-count controls and local attribution

We use two controls with distinct interpretations. The historical candidate-count control samples as many original positions from an accepted response as the four-position rule admits for inspection. It examines position selection before validation. The valid-count control instead fixes the number of validated unique tests in each response group. It uses the minimum of the three groups' counts at cap four and selects that many methods from each group's larger valid pool.

For the valid-count control, we compare a prefix of that length with five fixed draws without replacement. A zero common count is recorded as such and supplies no positive-count comparison. A target remains one descriptive unit regardless of the number of subsets scored. These draws ask whether different same-sized subsets of the saved tests detect different mutants. They do not estimate model sampling variance, and they do not make the G, E, and M pools exchangeable.

Attribution follows the observed changes rather than selecting a new generator. We map added kills to original response positions, validated method bodies, and mutant identities. A trace can show that a particular late assertion accounts for a saved-suite reversal. It cannot establish that the model systematically places that assertion late. We retain unchanged targets alongside the traced cases so that a detailed explanation is not mistaken for a common event.

### 3.6 Independent archive and exclusion accounting

The public archive provides Java suites for several models, prompts, and rounds [16]. Of 240 possible zero-shot/few-shot pairings across 16 classes, 82 have published full-suite reports on both sides. The primary panel freezes 27 pairs with at least eight tests per side, a unique source version, and a matching mutant catalog. We first reproduce the full-suite mutant states and check original-program execution, then execute the first four and first eight declared methods in separate builds. One pair remains unresolved, leaving 26 evaluable comparisons.

A separate follow-up freezes all 51 other pairs with two published reports and a shorter suite of five, six, or seven methods. Both sides use four methods at the lower cap and the shorter suite's length at the upper cap. Four pairs have unresolved timeouts in the published reports; 13 have unresolved full-suite timeouts on replay. These 17 pairs remain visible as exclusions rather than becoming zero-scoring comparisons. The remaining 34 pairs are the shorter-suite panel.

Declaration order is observable in the archive; original response order is not. The archive therefore supplies evidence about prefixes of saved test classes. It does not establish how the original models ordered methods within responses, whether a source file combines several responses, or which tests supplied feedback during generation. Matching by class, model, and round improves comparability, but repeated rounds can still contain identical normalized source and are not necessarily independent.

### 3.7 Conditional random selection and tie sensitivity

The initial external replay executes three nested random selections per suite in addition to the ordered prefixes. For draw $d$, the seed is the string `20261118:source_id:d`, supplied to Python's `random.Random`; `source_id` is the original suite path inside the archive. We sample an ordered sequence of eight distinct declaration indices. Its first four elements form the smaller subset. The four-test set is therefore nested in the eight-test set, with the same sampled order at both caps.

After the prefix results were inspected, we extended this control to 300 draws using PIT test–mutant matrices for the same 52 suites. All suites passed the original-program checks. For a selected subset, a mutant is counted as killed if at least one selected method killed it in the matrix. Matrix-derived killed-mutant identities matched all 413 distinct previously executed subsets, including full suites, prefixes, and the initial random draws. This validates the approximation on those executions; it does not guarantee equivalence for arbitrary stateful suites.

The reported central 95% draw interval uses the nearest-rank empirical percentiles: order statistics 8 and 293 of 300 sorted values. It describes selection variation conditional on the saved suites, not a confidence interval over independently generated responses. The randomization does not impose equal prompt effectiveness. It is consequently not a null distribution for a hypothesis that the prompts have identical effectiveness, and we report no p-value from it.

The primary comparisons use exact integer ties. Post hoc sensitivity checks treat differences of at most one killed mutant as ties, or use margins of 5 and 10 percentage points in mutation score. These thresholds reveal dependence on small differences. They are not validated practical-equivalence margins. We distinguish the original comparisons from the subsequent diagnostics in both the result headings and the interpretation.

### 3.8 Reproducibility and recorded work

The evidence records preserve response text, extracted methods, validation states, suite membership, mutation catalogs, raw PIT reports, and deterministic subset selections. SHA256 checks bind the analysis to the frozen inputs. Online Resource 2 provides the records and code for recomputing the core comparisons offline, along with the local prompt-construction templates. Per-call prompts containing project source are excluded. Its role is to make the reported evidence inspectable; the main article contains the results needed to assess the argument.

We account separately for extraction, per-method validation, final-suite compilation, and PIT commands. When work is cached, each logical comparison is attributed the measured operations it uses. The recorded timings are single command measurements and attribution totals. They are not repeated end-to-end latency estimates. Generation cost has already been incurred and is common to the replayed retention conditions, so the replay costs cannot establish which complete generation system is cheaper.

We used OpenAI Codex to draft, restructure, and revise the English manuscript based on the recorded experimental results.

### 3.9 Fresh generation-time cap comparison

To examine the replay boundary directly, we froze a targeted follow-up before collecting new responses. It uses form URL decoding, the earlier reversal case; Hex decoding, an unchanged case; and URL-safe Base64 encoding, a new focal API in the previously studied Base64 class. The third target adds an entry point, not an independent project or mutation catalog.

For each target and each seed (231101, 231102, 231103), one fresh initial response is shared across G and M and generation caps c=4 and c=8. Each of the four branches then receives two continuations, giving nine calls per block and 81 calls across nine blocks. Qwen2.5-Coder-7B-Instruct uses temperature 0.7, top_p=0.95, top_k=0, and the same 8192/2048 input/output limits as the library study. A seed derived from target, repeat, and round supplies matched random streams across branches. These are fresh stochastic repetitions, distinct from the original greedy trajectories. Section S4 specifies the derivation and runtime.

Before each continuation, the generation cap admits valid methods from the first c original positions of every earlier response, followed by body deduplication. G receives the retained test source. M additionally receives original-program diagnostics for up to c positions of the latest response and mutation feedback restricted to the frozen feedback partition. Changing c therefore changes permitted context and diagnostic feedback together; it does not isolate these two components. Every completed trajectory is scored at both replay caps k=4 and k=8 against the same held-out sites, producing eight G/M scoring cells per block.

The primary comparison is the signed G-minus-M kill gap at native settings (c,k)=(4,4) and (8,8). We also compare (4,4) with (4,8), which changes replay on a fixed trajectory, and (4,8) with (8,8), which changes generation at a common scoring cap. The fourth setting, (8,4), is retained in the results. Targets, seeds, caps, and the 81-call limit were fixed before these calls. We report every block, including empty suites, and use no replacement responses or added seeds. This follow-up was motivated by earlier observations; it is not a preregistered representative study or a new-model comparison.

## 4 Results

### 4.1 RQ1: Detection changes and unchanged targets

The local data show that wider retention can expose additional detections, but the added detections are concentrated in a subset of targets. Tables 3–5 present the full historical, initial-library, and Qwen-extension outcomes rather than only the cases that change a lead.

**Historical functions.** Across all 14 historical functions, the first, first-four, and all-eligible rules admitted 35, 126, and 164 unique jointly validated methods, respectively, deduplicated by function and method body across response groups. Table 3 reports the 12 functions with held-out scoring. At least one group gained detections on five functions when moving from the first method to four positions. Expanding further from four positions to all eligible methods changed detection on two functions: SortNumbers and MatchParens. Several functions were already at their catalog ceiling, while MakePalindrome remained at three of five kills despite retaining more output.

**Table 3. Complete held-out results for the 12 evaluable historical functions.** Each triplet gives first / first four / all eligible positions. G, E, and M are response sources. The two functions without a usable held-out comparison remain in the validation accounting.

| ID and function | Held-out mutants | G | E | M |
| --- | ---: | --- | --- | --- |
| 1 SeparateParenGroups | 5 | 5 / 5 / 5 | 5 / 5 / 5 | 5 / 5 / 5 |
| 3 BelowZero | 5 | 4 / 5 / 5 | 4 / 5 / 5 | 4 / 5 / 5 |
| 4 MeanAbsoluteDeviation | 3 | 0 / 3 / 3 | 0 / 3 / 3 | 0 / 3 / 3 |
| 5 Intersperse | 3 | 3 / 3 / 3 | 3 / 3 / 3 | 3 / 3 / 3 |
| 6 ParseNestedParens | 5 | 5 / 5 / 5 | 5 / 5 / 5 | 5 / 5 / 5 |
| 7 FilterBySubstring | 2 | 2 / 2 / 2 | 2 / 2 / 2 | 0 / 2 / 2 |
| 8 SumProduct | 2 | 2 / 2 / 2 | 2 / 2 / 2 | 2 / 2 / 2 |
| 9 RollingMax | 2 | 2 / 2 / 2 | 2 / 2 / 2 | 2 / 2 / 2 |
| 10 MakePalindrome | 5 | 3 / 3 / 3 | 3 / 3 / 3 | 3 / 3 / 3 |
| 11 StringXor | 3 | 3 / 3 / 3 | 3 / 3 / 3 | 3 / 3 / 3 |
| 19 SortNumbers | 13 | 6 / 10 / 13 | 4 / 13 / 13 | 6 / 13 / 13 |
| 119 MatchParens | 10 | 3 / 4 / 9 | 3 / 4 / 9 | 3 / 4 / 9 |

The presence of equal triplets has two interpretations that should not be conflated. A result such as SeparateParenGroups already detects its entire catalog under the smallest cap. MakePalindrome instead retains a gap to the catalog ceiling. Wider retention cannot improve the measured score if the additional saved tests contribute no new kills, whether because they are invalid, redundant in behavior, or unable to distinguish the remaining mutants. The score alone does not identify which explanation applies.

**Initial library interfaces.** Table 4 gives all six Codec interfaces. Moving from four to eight positions adds detections for four interfaces, but only form URL decoding changes the lead between G and M. Base64 decoding illustrates a different pattern: all groups gain the same 16 detections from tests already present in their shared seed. Hex encoding and decoding plateau after four positions. These outcomes show why detection gain and comparison change must be reported separately.

**Table 4. Complete held-out results for the six Commons Codec interfaces.** Each triplet gives one / four / eight eligible positions per response. Encoding and decoding share the class-level universe within each behavior family, so the rows are not independent mutant catalogs.

| API | Held-out mutants | G | E | M |
| --- | ---: | --- | --- | --- |
| Hex encoding | 33 | 0 / 0 / 0 | 0 / 0 / 0 | 2 / 11 / 11 |
| Hex decoding | 33 | 0 / 4 / 4 | 1 / 4 / 4 | 1 / 4 / 4 |
| Base64 encoding | 86 | 0 / 0 / 0 | 0 / 8 / 8 | 0 / 13 / 18 |
| Base64 decoding | 86 | 0 / 0 / 16 | 0 / 0 / 16 | 0 / 0 / 16 |
| Form URL encoding | 27 | 1 / 2 / 4 | 1 / 2 / 4 | 1 / 2 / 4 |
| Form URL decoding | 27 | 4 / 4 / 11 | 0 / 2 / 8 | 4 / 9 / 9 |

The family-level scopes matter. For example, the denominator of 86 is the shared Base64 catalog rather than the number of mutants exclusively attributable to its decoder entry point. The 16 additional kills in the decoding row demonstrate a change within this fixed scope. They are not evidence of a 16-mutant improvement on an independently sampled decoder-only benchmark.

**Qwen extension.** Table 5 adds the 24 Commons Lang and Joda-Time interfaces. Wider retention leaves detection unchanged on 18 interfaces and adds detections for at least one group on six. Five interfaces change at least one pairwise ordering when ties are included; two contain a strict reversal. The positive common valid-test count is zero for nine interfaces, which limits what can be said using fixed-count controls.

**Table 5. All 24 Qwen extension interfaces.** G 4/8, E 4/8, and M 4/8 are killed-mutant counts at four/eight original positions per response. H is the fixed held-out catalog size. The common valid-test count k is based on the four-position pools; zero is not a zero mutation score for every group.

| API | H | G 4/8 | E 4/8 | M 4/8 | k |
| --- | --- | --- | --- | --- | --- |
| lang_reverse | 2 | 2/2 | 2/2 | 2/2 | 4 |
| lang_rotate | 17 | 0/0 | 0/0 | 7/7 | 0 |
| lang_count_matches | 22 | 2/2 | 2/2 | 2/2 | 9 |
| lang_between | 7 | 6/7 | 6/6 | 6/6 | 8 |
| lang_left_pad | 40 | 4/4 | 4/4 | 4/4 | 6 |
| lang_split | 25 | 6/6 | 6/6 | 6/6 | 9 |
| lang_capitalize | 6 | 5/5 | 5/5 | 5/5 | 7 |
| lang_overlay | 8 | 4/5 | 4/5 | 4/5 | 9 |
| lang_subarray | 27 | 0/0 | 0/0 | 4/4 | 0 |
| lang_remove | 13 | 9/9 | 0/9 | 0/9 | 0 |
| lang_index_of | 47 | 5/5 | 5/5 | 5/5 | 7 |
| lang_to_boolean | 62 | 11/11 | 6/11 | 9/12 | 11 |
| joda_plus_days | 3 | 2/2 | 2/2 | 2/2 | 4 |
| joda_plus_months | 43 | 18/18 | 13/15 | 7/15 | 4 |
| joda_day_of_month | 8 | 0/0 | 0/0 | 0/0 | 0 |
| joda_day_of_week | 7 | 2/2 | 2/2 | 2/2 | 7 |
| joda_day_of_year | 5 | 5/5 | 5/5 | 5/5 | 9 |
| joda_plus_minutes | 3 | 1/1 | 1/1 | 1/1 | 5 |
| joda_millis_of_second | 9 | 0/0 | 0/0 | 0/0 | 0 |
| joda_millis_of_day | 8 | 2/2 | 2/2 | 2/2 | 5 |
| joda_days_between | 5 | 0/0 | 3/3 | 0/0 | 0 |
| joda_standard_days | 17 | 0/0 | 0/0 | 0/0 | 0 |
| joda_divided_by | 8 | 0/0 | 0/0 | 0/0 | 0 |
| joda_parse_duration | 22 | 0/7 | 6/11 | 7/7 | 0 |

The two strict reversals concern BooleanUtils.toBoolean and Duration.parse. In toBoolean, G leads M by 11 to 9 kills at four positions; M leads G by 12 to 11 at eight. In Duration.parse, E moves from 6 versus 7 kills against M to 11 versus 7. Both reversals persist after the common resource-status exclusions. Other changes are less dramatic: StringUtils.substringBetween gains one G kill, while ArrayUtils.remove moves E and M from zero to nine kills and closes their gaps to G.

A zero common count needs careful interpretation. Duration.parse has k = 0 because at least one group contributes no validated tests under the four-position rule, even though E and M detect mutants. It is therefore informative for the position-cap comparison but supplies no positive equal-count comparison under that rule. Omitting such rows would make fixed-count applicability look broader than it is.

**Second model and admission limits.** Table 6 preserves the denominators for Qwen and Granite. The original Granite protocol yields only one interface with a positive common count. Structural admission fails for 149 of its 210 logical response slots, compared with three of Qwen's 168 extension slots. This limits the evidence about retention effects for Granite; it is not evidence that retention is intrinsically unimportant for that model family.

**Table 6. Extension outcomes and applicability of equal-count comparison.** The first two columns use the original rules. The last column is a post hoc replay after recovering complete fenced code from saved Granite responses. Its raw reversal does not survive the shared resource-status exclusion.

| Quantity | Qwen original (24 APIs) | Granite original (30 APIs) | Granite format replay (30 APIs) |
| --- | ---: | ---: | ---: |
| Strict reversal under primary scoring | 2 | 0 | 1 |
| Strict reversal after common resource exclusions | 2 | 0 | 0 |
| Positive common valid-test count | 15 | 1 | 5 |
| Detection varies among equal-count selections | 11 | 1 | 3 |

The format replay raises the number of Granite APIs with a positive common count from one to five. It changes extraction of existing responses while preserving the generated assertions and subsequent validation conditions. Because it was designed after observing the structural failures, it is auxiliary evidence about admission barriers, not an independent favorable replication. The raw reversal disappears after harmonizing the resource exclusions. We retain the original Granite results as the primary second-model observations.

**Answer to RQ1.** Wider retention sometimes adds detections and occasionally changes a local lead, but most extension targets do not improve. Empty pools and admission failures also restrict the population on which selection can be compared. The complete target tables support a localized finding rather than a general claim that a larger cap changes which strategy is best.

### 4.2 RQ2: Attributable reversals and equal-count selection

**Response positions explain two local cases.** Figure 1 shows SortNumbers and form URL decoding using their original fixed catalogs. On SortNumbers, G leads E by 6 to 4 kills under the first-method rule and trails 10 to 13 at four positions. Both reach 13 with all eligible methods. The test asserting the numerical ordering of reversed number words appears sixth in G's first continuation but second in the corresponding E and M continuations. Its body is present in all three sources. The first-four comparison thus separates sources partly because the same useful test occupies different positions.

![Figure 1. Two attributable local changes in comparison.](../../figures/fig1_comparisons.png)

**Figure 1. Two attributable local changes in comparison.** G, E, and M denote generic continuation, execution feedback, and mutation feedback. SortNumbers uses 13 held-out mutants and form URL decoding uses 27. Each panel replays fixed responses across retention caps; it does not compare independent generations at those caps.

For form URL decoding, the G suite kills four mutants at four positions and eleven at eight. M remains at nine. The additional G method at position six tests that plus signs decode to spaces, accounting for two newly killed mutants. Position seven tests that encoding `%25` decodes to the percent character, accounting for five others. The union of those sets accounts for all seven extra detections. Both methods pass the original and reference checks; no assertion repair is used to obtain the result.

The four- and eight-position rules admitted two and four distinct valid tests for G, and four and five for M. The common valid-test quota for this API was one, the minimum across all three arms at the four-position cap. Thus the two additional G tests explain the reversal under the position rule; the equal-count control asks how scores vary when suite sizes are matched.

**Fixed-count comparisons.** Figure 2 compares prefixes with five same-sized saved-pool draws for two historical functions and the two form URL interfaces. A dot represents a subset draw, not a new model generation. The spread shows which detection counts are attainable under those particular subsets; five draws do not characterize the entire subset space.

![Figure 2. Detection under a fixed number of validated tests.](../../figures/fig2_matched_count.png)

**Figure 2. Detection under a fixed number of validated tests.** Diamonds denote prefixes and dots denote five fixed draws from the same validated pools. The panels give the common valid-test count per group and the held-out catalog size. Subsets share responses and mutants and are not independent generation replicates.

Among the 15 Qwen extension APIs with a positive common count, alternative selections vary the detection count on 11. Ten retain variation after the common resource exclusions. This is a statement about detection counts within a fixed pool, not eleven strict reversals between generators. Table 7 makes two cases explicit, including all five draws for each response group.

**Table 7. Equal-valid-count controls for two Qwen interfaces.** Prefix and draw entries are killed-mutant counts. Each group contributes k valid unique methods. The denominators are 43 for plusMonths and 62 for toBoolean; the kth valid method need not occupy original response position k.

| Model and API | Group | k | Prefix | Five draws |
| --- | --- | --- | --- | --- |
| Qwen plus_months | G | 4 | 7 | 14, 13, 17, 7, 6 |
| Qwen plus_months | E | 4 | 13 | 11, 13, 13, 6, 7 |
| Qwen plus_months | M | 4 | 6 | 5, 7, 6, 6, 6 |
| Qwen to_boolean | G | 11 | 11 | 7, 10, 11, 10, 11 |
| Qwen to_boolean | E | 11 | 6 | 10, 10, 11, 5, 7 |
| Qwen to_boolean | M | 11 | 9 | 7, 11, 11, 9, 12 |

LocalDate.plusMonths illustrates why the unit must accompany the number four. Under four *original positions per response*, the G/E scores are 18/13. Under the first four *validated methods per group*, they are 7/13. These two policies change both the unit of admission and the suite, so the difference cannot be assigned solely to ordering at a fixed raw-position cap. Within the valid-count control, however, all five draws contain exactly four tests per group. Their G/E comparisons comprise three G leads, one E lead, and one tie. Selection can therefore change the observed leader in this pool even with quantity aligned.

The toBoolean control makes another distinction visible. At k = 11, the prefix produces 11, 6, and 9 kills for G, E, and M; other equally sized draws yield overlapping detection ranges. An exact lead for one chosen subset is not a characterization of every subset of that size. The results support checking composition after aligning quantities, while leaving open how often such sensitivity would occur in independently generated pools.

**Answer to RQ2.** The traced local reversals are supported by method-level evidence, and equal-count examples show residual composition sensitivity. Neither analysis identifies a generally superior response source. Position effects, admission rules, and suite composition need separate descriptions even when all are implemented through a retention policy.

### 4.3 RQ3: Declaration-order prefixes in the external archive

The independent archive yields no strict reversal in either prefix panel. Table 8 gives the full planned and evaluated denominators. The primary panel's 26 evaluable pairs span ten target classes. Of the nine transitions, eight are leads that become ties and one is a tie that becomes a lead. Seventeen pairs retain the same ordering. Five of the eight disappearing leads end with both suites killing the complete fixed catalog. The one emerging lead was substantial within its catalog. For primes, Llama round 3, the zero-shot and few-shot suites each killed 6 of 20 mutants at four declarations. At eight they killed 16 and 9, respectively, opening a gap of 7 mutants (35 percentage points).

**Table 8. Complete accounting for the external prefix panels.** Caps five, six, and seven are separate sets of shorter suites, not repeated observations of the same panel. A transition can involve a tie; all rows have zero strict reversals.

| Caps | Planned | Scored | Lead to tie | Tie to lead | Same order |
| --- | ---: | ---: | ---: | ---: | ---: |
| 4 to 8 | 27 | 26 | 8 | 1 | 17 |
| 4 to 5 | 24 | 11 | 3 | 1 | 7 |
| 4 to 6 | 13 | 12 | 4 | 0 | 8 |
| 4 to 7 | 14 | 11 | 7 | 0 | 4 |

Table 9 shows the primary results by class, including the ranges of zero-shot-minus-few-shot gaps at each cap. These are ranges over the recorded pairs within a class, not confidence intervals. They preserve the scale of the underlying differences and expose the small catalogs behind some transitions. All 78 frozen pairs across both panels, their raw scores, and their exclusion states are listed in Online Resource 1.

**Table 9. Class-level view of the 26 primary archive comparisons.** N is the fixed catalog size. Gaps are zero-shot minus few-shot killed-mutant counts; a range summarizes the class's observed model/round pairs. The transition column counts changed sign or tie status, with zero strict reversals throughout.

| Class | N | Pairs | Gap at 4 | Gap at 8 | Transitions |
| --- | ---: | ---: | --- | --- | ---: |
| anagrams | 11 | 2 | 0 to 2 | 0 | 1 |
| area | 11 | 3 | 1 | 0 | 3 |
| charrange | 22 | 1 | -1 | -1 | 0 |
| charsetutils | 9 | 1 | 0 | 0 | 0 |
| fraction | 17 | 1 | 4 | 5 | 0 |
| hex | 9 | 1 | -1 | 0 | 1 |
| matrixutil | 9 | 4 | 0 to 2 | 0 to 2 | 1 |
| primes | 20 | 5 | -3 to 0 | -3 to 7 | 3 |
| range | 5 | 4 | 0 | 0 | 0 |
| stringcompression | 20 | 4 | 0 to 1 | 0 to 1 | 0 |

For shorter suites, 34 of the 51 frozen pairs are evaluable and span six classes. The 17 exclusions all concern HashMapCuckooHashing or StackArray, so the evaluated subset is not an unselected representation of the archive. There are 15 transitions: 14 disappearing leads and one emerging lead. Every disappearing lead is a one-mutant advantage at four methods, followed by both suites reaching the catalog ceiling. These occur in eight Area pairs (eleven mutants), four Hex pairs (nine mutants), and two BinaryTree pairs (three mutants).

These outcomes demonstrate small-catalog ceiling effects in this archive. They do not reproduce the local strict-reversal mechanism. The distinction matters both empirically and constructually: the archive lacks original response positions, and the added declarations frequently close a marginal gap rather than admit a test that makes the formerly trailing suite strictly better.

**Answer to RQ3.** Increasing declaration-order prefix length changes some exact comparisons, chiefly by turning small leads into ties. The evaluated archive contains no strict prefix reversal. Exclusions and repeated-source dependencies limit the populations to which even these descriptive rates apply.

### 4.4 RQ4: Conditional variation and post hoc sensitivity

**Tie margins.** Table 10 separates exact transitions from those that remain when a difference of at most one killed mutant is treated as a tie. Four of the primary panel's nine transitions disappear, leaving five across three of its ten classes. All 15 shorter-suite transitions disappear. The latter result reinforces the limited magnitude of the short-suite finding rather than providing another independent retention effect.

**Table 10. External transitions under exact ties and a one-mutant margin.** Entries are changed comparisons / strict reversals. The random row gives a separate median for each count over 300 draws; the values need not occur together in any one draw.

| Selection | Pairs | Exact ties | One-mutant margin |
| --- | ---: | ---: | ---: |
| Prefix, 4 to 8 | 26 | 9 / 0 | 5 / 0 |
| Random, 300 draws (medians) | 26 | 11 / 2 | 6 / 0 |
| Prefix, shorter suites | 34 | 15 / 0 | 0 / 0 |

**Conditional random selection.** Table 11 reports the distribution more fully. With exact ties, nested random selection yields a median of eleven transitions and two strict reversals. The prefix count of nine transitions lies inside the central draw interval of six to sixteen. Random transition counts exceed the prefix count in 206 of 300 draws. Under the one-mutant margin, the median is six transitions, with an interval of two to ten; the prefix count is five, and 192 draws exceed it.

**Table 11. Distribution over 300 nested random selections from the primary saved suites.** Prefix counts are fixed observations. Intervals are empirical draw percentiles, not population confidence intervals or a no-effect reference distribution.

| Margin | Outcome | Prefix | Random median | Central 95% draw interval | Draws above prefix |
| --- | --- | ---: | ---: | --- | ---: |
| 0 mutant(s) | Transitions | 9 | 11 | 6 to 16 | 206/300 |
| 0 mutant(s) | Reversals | 0 | 2 | 0 to 4 | 252/300 |
| 1 mutant(s) | Transitions | 5 | 6 | 2 to 10 | 192/300 |
| 1 mutant(s) | Reversals | 0 | 0 | 0 to 2 | 109/300 |

Total transitions and strict reversals tell different stories. With exact ties, 252 of 300 draws produced at least one strict reversal, compared with none in declaration order. To check whether the first four declarations were unusually effective, we averaged their kill counts across the 52 suites, weighting each suite equally. The prefix mean was 8.63 mutants, compared with a median mean of 9.02 across random draws (central 95% draw interval 8.60 to 9.40). At four declarations 14 of 52 suites already reached their catalog ceiling, compared with a random median of 11 (interval 7 to 15). More prefix suites reached the ceiling than in the median draw, but their average kill count was lower. Neither aggregate identifies the cause of an individual pair's reversal.

**Catalog size and weighting.** A one-mutant margin has different relative meanings across catalogs. For the short-suite classes with disappearing leads, one mutant represents 9.1%, 11.1%, or 33.3% of the catalog. Relative margins probe this dependence: at five percentage points, the primary and short-suite panels retain nine and fifteen transitions; at ten percentage points, each retains six. Neither margin produces a strict reversal. No threshold is presented as a universally meaningful minimum effect.

Unequal numbers of model/round pairs per class also affect descriptive aggregation. Giving the ten primary classes equal weight yields a prefix transition rate of 33.5%; the corresponding random-selection median is 42.3%, with a central draw interval of 18.3–63.5%. This weighting changes the summary but does not remove dependence between rounds or make the selected classes a random sample. Additional target-weight and catalog diagnostics remain in Online Resource 1 as post hoc analyses.

**Answer to RQ4.** The primary panel's total prefix transitions fell inside the random-selection interval. Strict reversals were absent from the observed prefixes and present in most exact-tie random draws. The one-mutant margin removed every shorter-suite transition and left five on the primary panel.

### 4.5 RQ5: Generation-time changes versus replay on fixed trajectories

Changing the cap during generation and widening admission after generation did not always yield the same comparison. All nine fresh blocks completed, with 81 responses and 72 scored cells. Table 12 gives every held-out result. Native comparisons from (4,4) to (8,8) yielded two tie-to-G-lead transitions, one M-lead-to-tie transition, and six unchanged orderings. None was a strict reversal. Replay alone on the c=4 trajectories yielded two tie transitions; at common scoring cap k=8, changing c yielded one additional tie-to-G-lead transition.

**Table 12. All fresh generation-cap comparisons.** Entries are G / M held-out kills. (c,k) denotes generation cap and replay cap, each in original positions per response. N is the fixed class-level evaluation catalog. Seeds are paired repeat identifiers; the nine rows are not nine independent targets.

| Target | Seed | N | (4,4) G / M | (4,8) G / M | (8,4) G / M | (8,8) G / M |
| --- | ---: | ---: | --- | --- | --- | --- |
| Form decode | 231101 | 27 | 9 / 9 | 11 / 9 | 9 / 0 | 11 / 2 |
| Form decode | 231102 | 27 | 11 / 11 | 11 / 11 | 11 / 11 | 11 / 11 |
| Form decode | 231103 | 27 | 6 / 11 | 11 / 11 | 6 / 11 | 11 / 11 |
| Hex decode | 231101 | 33 | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| Hex decode | 231102 | 33 | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| Hex decode | 231103 | 33 | 4 / 0 | 4 / 0 | 4 / 0 | 4 / 0 |
| URL-safe Base64 | 231101 | 86 | 12 / 7 | 12 / 7 | 12 / 7 | 12 / 7 |
| URL-safe Base64 | 231102 | 86 | 7 / 7 | 7 / 7 | 7 / 0 | 7 / 0 |
| URL-safe Base64 | 231103 | 86 | 12 / 0 | 12 / 0 | 12 / 0 | 12 / 0 |

For form decoding at seed 231101, replay alone changed the gap from 0 to +2; the native eight-position workflow produced +9, because M killed only two held-out mutants. At seed 231103, G caught up with M under both comparisons, while seed 231102 remained tied. Thus the earlier greedy-decoding strict reversal did not recur in these three sampled blocks. For URL-safe Base64 at seed 231102, replay left G and M tied at seven kills, but the native eight-position workflow produced 7 versus 0. That M suite contained one valid test with zero held-out detections, rather than an empty suite. The other two Base64 blocks and all three Hex blocks kept their ordering.

Distinct valid tests available only beyond the first four positions entered eight continuation contexts, all within the three form-decoding blocks. The Base64 transition had no such extra valid-source exposure; M could still receive diagnostics for additional rejected positions. It therefore demonstrates a difference between the combined generation-cap workflows, not a proven benefit of admitting later valid tests. Nine of the 72 scored cells were empty, all in three blocks. Table S15 reports all valid counts, including these zeros. No held-out mutant status was unresolved.

**Answer to RQ5.** This small experiment establishes that post-generation replay can miss a comparison change produced by a different generation-cap workflow. It did not reproduce a strict reversal or establish that wider feedback improves effectiveness. The three repeats expose target-specific variation; they do not estimate its frequency across projects or models.

## 5 Discussion

### 5.1 What the evidence adds beyond the suite-size observation

The study does not overturn the familiar expectation that additional tests can increase detection. Its added value is the distinction between three outcomes that an aggregate score can obscure: a method-attributable local reversal, a marginal lead disappearing at a fixed catalog ceiling, and variation among equally sized subsets of the same generated pool. Each has a different implication for interpreting a comparison.

For form URL decoding and SortNumbers, the trace connects a comparison change to identifiable saved methods and their positions. For the shorter external suites, the one-mutant leads and catalog ceilings explain why exact ordering changes without a robust effectiveness reversal. The conditional random benchmark further shows that the external prefix transitions fall within selection variation already obtainable from the archived suites. These observations together support a bounded evaluation lesson, not a universal instability claim.

A comparison at one retention policy remains a valid description of that policy if its unit and execution rules are stated. The difficulty arises when a policy-specific lead is treated as a property of the generator irrespective of output admission. Our results make that distinction observable in concrete cases. They do not estimate how common the mistake is in published research, and they do not imply that all evaluations must discard a practical cap.

The fresh-generation follow-up provides a concrete boundary check. For URL-safe Base64 seed 231102, widening replay alone retained a tie, whereas changing the generation workflow produced a seven-mutant G lead. Form decoding also showed a larger gap under the native workflow than under replay. These differences justify keeping the generation cap and replay cap distinct in reported configurations. The sampled runs did not reproduce the original strict reversal, so that case remains an attributable saved-trajectory observation rather than a recurring effect established by the follow-up.

### 5.2 A reporting procedure for retained multi-test outputs

The following procedure follows from the evidence without presuming that wider retention is always preferable. First, distinguish the cap used during feedback-guided generation from the cap used for final replay. State whether the cap applies to original positions per response, validated methods per suite, or execution attempts. Include what happens when a method fails validation. Second, report the resulting unique valid-test counts and major exclusion categories. This makes clear whether nominally equal caps produced comparable suites.

Third, report paired detection counts and fixed catalog sizes at the chosen policy. Where a second replay is feasible, select its cap using available test counts and execution resources before inspecting its score. Report all eligible targets, including no-change and empty-pool cases. Separate strict reversals from tie transitions and identify whether both suites reach the catalog ceiling. These steps prevent a single aggregate from hiding the kind of change being observed.

Fourth, if quantities differ or a local lead matters to the conclusion, consider a common positive valid-test count. Use the original prefix as one selection and describe alternative subset selections precisely. Preserve a zero common count in the accounting. A conditional draw distribution can expose selection sensitivity, but its repeated draws must not be relabeled as independent model runs or interpreted as a prompt-effectiveness null hypothesis.

Finally, distinguish the article's explanatory evidence from the replication files. The article should include the main target-level outcomes, key controls, and boundaries; the artifact should permit reconstruction of method membership and killed-mutant sets. Applying the procedure does not guarantee that a result generalizes. It makes the conditions under which the result was obtained sufficiently explicit to evaluate or repeat.

### 5.3 Retention and recorded execution work

Table 13 gives the measured work for selected historical comparisons. Wider retention can improve detection, leave detection unchanged, or reach a ceiling while still requiring additional validation. On SortNumbers, M already kills all thirteen held-out mutants at four positions; its attributed work increases from 31.29 to 36.60 seconds when all eligible methods are considered. On MatchParens, G's score increases from four to nine kills, while attributed work changes from 17.38 to 37.30 seconds.

**Table 13. Detection and attributed work in the historical replay.** Times are single command measurements attributed through shared caches. They describe recorded workload, not replicated speed measurements or full generation-system cost.

| Function and source | First-four detection | All-method detection | First-four work (s) | All-method work (s) |
| --- | ---: | ---: | ---: | ---: |
| SortNumbers / G | 10/13 | 13/13 | 33.09 | 50.20 |
| SortNumbers / E | 13/13 | 13/13 | 34.17 | 38.89 |
| SortNumbers / M | 13/13 | 13/13 | 31.29 | 36.60 |
| MatchParens / G | 4/10 | 9/10 | 17.38 | 37.30 |
| MatchParens / E | 4/10 | 9/10 | 17.74 | 37.67 |
| MatchParens / M | 4/10 | 9/10 | 28.67 | 63.84 |
| SeparateParenGroups / G | 5/5 | 5/5 | 24.91 | 35.30 |

The table supports recording admission and execution work together with detection. It does not establish an optimal retention cap or a stable speedup factor. JVM startup, caches, target complexity, and failed candidates influence these measurements, while the original LLM inference cost is shared by the replay conditions. A deployment decision would require its own cost model and, for latency claims, repeated timing measurements.

### 5.4 Language scope and transfer of the protocol

The central question—how retained subsets shape evaluation—is applicable to generated tests in more than one programming language. The protocol needs observable candidate order, an explicit validation contract, stable test identities, and a comparable outcome measure. Those requirements can be stated independently of Java. The implementation used to satisfy them here is language-specific.

For another language, an adapter would need to identify test units, execute them under an appropriate framework, and bind detections to a fixed fault catalog or other justified metric. Framework fixtures, parameterized tests, shared state, and execution order can change what constitutes an independently selectable method. Such a transfer is therefore an empirical task, not a title change. The present results establish no effect frequency for Python, C, or another language.

Choosing Java permits continuity across the local responses, the executable libraries, and the external archive. This supports detailed within-setting checks. It also bounds the conclusion: the practical reporting questions may be useful elsewhere, while the particular reversals, transition rates, and admission failures belong to these Java materials. The title states the evaluation problem, and the abstract and design state the evidence domain.

## 6 Threats to Validity

### 6.1 Construct validity

Our response-position cap and the archive's declaration-order prefix are different constructs. The archive cannot recover where a method originally appeared in a model response. Its results therefore provide a related but distinct external check, not a direct replication of response-position attribution. Similarly, a cap per response and a quota per validated suite differ in both unit and admission behavior. We report those policies separately and do not interpret their difference as a pure count effect.

Mutation detection is a proxy for test effectiveness. Fixed catalogs and original/reference checks improve interpretability but do not turn artificial faults into real defects or guarantee the absence of equivalent mutants. Small catalogs make one additional kill a large percentage change, and class-level Codec catalogs include behavior outside an individual entry point. The paper reports denominators, exact counts, and sensitivity margins so these effects are visible. The present analysis makes no claim about naturally occurring defect detection.

A strict reversal is an operational comparison of integer counts. It is not automatically a practically significant effect. Likewise, disappearance under a tie margin does not prove equivalence. The absolute and relative margins are post hoc diagnostic thresholds, and the paper does not select a favorable one as a final definition of success.

### 6.2 Internal validity

Replay retains the responses and their generation histories, which controls generation differences between replay conditions. However, those histories may already depend on the four-position admission policy. Our eight-position result therefore concerns admitting more of an existing output, not a trajectory generated using eight-position feedback. The separate experiment in Section 4.5 changes the cap during generation and confirms that the two interventions can yield different comparisons in the selected cases. It changes retained context and permitted diagnostics together, so it cannot isolate their individual causal contributions.

Extraction, reference bindings, and input-domain checks can affect which tests are admitted. These checks are preserved in the artifacts, and rejection states remain distinguishable. They still represent the contracts we implemented rather than exhaustive correctness proofs. Granite's later format recovery was prompted by the observed failures; it remains an explicitly post hoc sensitivity check and cannot replace the unfavorable original admission results.

Test–mutant matrix scoring assumes that the outcome attributable to a retained method remains stable when other methods are removed. Agreement with 413 executed subsets supports that assumption in the checked cases. It cannot rule out all fixture interactions or order-dependent behavior among unexecuted subsets. Original-program checks, fixed catalogs, and resource-status exclusions also do not eliminate every source of nondeterministic execution.

### 6.3 External validity

The local sample contains small functions and selected library APIs, two local model families, original saved greedy-decoding trajectories, and a targeted three-repeat stochastic follow-up with Qwen. HumanEval-Java and the library code are public. Prior exposure during model training could affect which tests were generated and where they appeared. We did not measure training-set overlap. Replay holds any such exposure fixed within a trajectory, but cannot show how retention would behave on previously unseen code. The follow-up provides fresh generation repetitions on only three deliberately chosen targets. It adds neither a newer model, a cross-language replication, nor broad repository-level sampling. The external archive expands provenance and model/prompt combinations, but eligibility and timeout exclusions restrict its scope. The primary requirement of eight methods per side selects longer suites, while the shorter panel has a different class/model composition.

Targets, response groups, and rounds are not independent observations. Codec interfaces share catalogs; local response groups share seed responses; external rounds sometimes contain identical normalized source. The 26 primary pairs come from ten classes rather than 26 unrelated systems. Class weighting offers a descriptive alternative but does not resolve those dependencies or turn the sample into a representative population.

### 6.4 Conclusion validity and exploratory analyses

The study emphasizes exact within-pool comparisons and traceability. The 300 draws describe subset selection, not uncertainty over independently generated outputs. We therefore avoid significance claims about general generator superiority and do not interpret draw percentiles as confidence intervals for recurrence. Lack of a strict reversal in these panels is a descriptive result, not proof that a reversal is impossible elsewhere.

Several checks followed inspection of earlier results: format recovery, tie margins, the 300-draw extension, and alternative weighting and catalog diagnostics. Their post hoc status is retained rather than presenting them as one preregistered factorial experiment. The five RQs organize the accumulated evidence; they do not imply that every stage and threshold was specified before the original exploratory observations. The fresh-generation protocol was fixed before its own calls but was motivated by the earlier findings. Complete target tables and exclusions reduce selective presentation, but cannot remove the need for future independent confirmation of broader claims.

## 7 Conclusion

Paired post-generation replay makes it possible to determine which saved tests change an observed evaluation while holding model responses fixed. In our Java corpora, late methods explain local strict reversals, and same-sized selections can yield different paired detection results. These examples establish that the admission unit and selected subset can matter even when the generator is unchanged.

The broader evidence limits that conclusion. Most Qwen extension interfaces gain no detections at the wider cap. The external declaration-order panels contain no strict reversal, and their smaller-suite transitions vanish under a one-mutant margin. The primary prefix count lies within the conditional random-selection distribution. These outcomes support reporting retention as an explicit part of the evaluated workflow, with admitted counts, fixed denominators, and separate treatment of strict reversals and ties. They do not support a general claim that ordered retention is unusually unstable or that one feedback source is universally better.

The fresh-generation follow-up adds three repeats on selected targets: native cap changes produced three tie transitions and no strict reversal, while fixed-trajectory replay produced two. Wider independent-generation and cross-language studies would still be needed to estimate recurrence and transfer. The present contribution is the attributable evidence and its boundaries: what changed in these fixed pools, which methods account for it, and which apparent comparison changes are too small or too conditional to carry a broader conclusion.

## Statements and Declarations

**Funding.** This work was supported by the National Natural Science Foundation of China (Grant No. 62467005).

**Competing interests.** The authors declare no competing interests.

**Ethics approval and consent.** The study involved no human participants. Ethics approval and participant consent were not applicable.

**AI-assisted manuscript preparation.** As described in Section 3.8, the authors used OpenAI Codex to draft, restructure, and revise the English manuscript based on the recorded experimental results. The authors take responsibility for the full text.

**CRediT authorship contribution statement.** **Wei Zheng:** Funding acquisition, Resources, Supervision, Writing – review & editing. **Shuhuan Lv:** Methodology, Investigation, Formal analysis, Writing – original draft. **Xin Fan:** Data curation, Software, Validation. **Hao Pan:** Data curation, Software, Supervision, Validation. **Fengyu Yang:** Data curation, Software, Validation. **Peng Xiao:** Software, Validation.

## Data Availability

Online Resource 2 (ESM_2.zip) is available to reviewers in the submission files and is intended for publication with the article upon acceptance. It contains saved responses, validation records, mutant catalogs, PIT reports, pair inclusions and exclusions, test–mutant matrices, and offline reanalysis code. The package reconstructs Tables 6, 8, 10, and 12 from recorded outcomes and includes historical and six-API verification entries. It does not rerun model inference or Java validation. The fresh-generation evidence additionally includes the actual prompts and their focal Commons Codec source excerpts, with the source license and notice. Full production source trees, earlier full source-containing prompts, model weights, and runtime binaries are excluded; provenance is documented. The third-party Java archive remains available via its Zenodo record [16].

**Online Resource 1.** Extended protocols, detailed supporting results, and sensitivity analyses (ESM_1.pdf).

**Online Resource 2.** Saved evidence and offline reproduction code, with a file manifest, SHA-256 checksums, source provenance, and verification instructions (ESM_2.zip).

## References

References are generated from the accompanying BibTeX database using the Springer author–year style.
