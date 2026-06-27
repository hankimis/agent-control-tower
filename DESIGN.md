# Pre-registration: The Completion Illusion

**Committed before scoring.** As agents do more multi-step work, systems increasingly trust
the agent's own report that a task is "done." We ask whether that report is true, and whether
asking the model to self-check fixes it. The answer motivates where reliability has to live:
in the model, or in the system around it (the control tower).

## Hypotheses

- **H1 (overclaiming).** An LLM agent given a batch of verifiable micro-tasks reports more
  completed-correctly than it actually got right. The false-completion rate (claimed-correct
  minus verified-correct, over the batch) is positive and material.
- **H2 (self-check does not fix it).** Wrapping the same workload in an enforced "register,
  do one-by-one, then re-check" prompt protocol does not meaningfully reduce the
  false-completion rate. Prompt-level self-verification is not enough.
- **H3 (no free accuracy).** The protocol does not materially improve task accuracy or reduce
  omission on current frontier models. (Reported even if null.)

Implication, if H1+H2 hold: completion cannot be trusted from the model; it must be verified at
the **system layer**. That is the function of an agent control tower's server-side enforcement.

## Design

Four models in two tiers (small: `gpt-4o-mini`, `claude-haiku-4-5`; frontier: `gpt-4o`, `claude-sonnet-4-6`) each run 8 workloads of K verifiable
micro-tasks (arithmetic, string ops, multi-step), every answer checked programmatically, under
two conditions:
- **baseline**: all K tasks in one prompt, "complete all", plus a final self-report of how many
  were completed correctly (a raw API call).
- **protocol**: a managed task-board prompt: STEP 1 register all ids, STEP 2 execute one-by-one
  with `[done]`, STEP 3 re-check and fix, then self-report (mirrors a control tower's
  TODO -> IN_PROGRESS -> DONE with a flow-guard re-check).

Run at K=12 and K=28 for a workload-size robustness check.

## Metrics
- **False-completion rate** = (self-reported correct minus verified correct) / K. The headline.
- **Accuracy** = verified-correct / K. **Omission** = tasks left unanswered / K.
- Per model and pooled; baseline vs protocol.

## Confound controls
1. **Verifiable tasks only**, checked by exact normalized string match, so "correct" is ground
   truth, not a judge.
2. **Identical task sets** across conditions (paired by workload seed).
3. **Same output format** parsed from both conditions, so the protocol's structure, not the
   parser, is the only difference.
4. Temperature 0, content-cached, seeded task generation: reproducible.
5. Two model families.

## What would falsify the thesis
If false-completion is near zero, or if the prompt protocol drives it to zero, then self-report
is trustworthy or prompt-fixable and the control tower's server-side enforcement is unnecessary.
Null and negative results (including H3) are reported.
