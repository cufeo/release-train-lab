# release-train-lab

A working model of the release process under evaluation, plus a side-by-side
comparison of three CI defects and their fixes. Everything here runs for real in
GitHub Actions. No cluster is contacted; the deploy job prints what it would apply.

The application is deliberately tiny, but the failure it reproduces is exact: the
package constructs an `Environment` at import time, and every settings module outside
a small allow-list unpacks a JSON blob from an environment variable that is absent
from the checked-in example env file.

## What each demonstration proves

| # | Run this | Watch for |
|---|---|---|
| 1 | PR touching only `README.md` | `changes (proposed)` selects backend, `changes (corrected)` does not |
| 2 | PR touching only `app/vendor/thirdparty.py` | the exclusion works only in the corrected filter |
| 3 | Any PR touching `app/` | `smoke (proposed)` fails with `JSONDecodeError`, `smoke (corrected)` passes |
| 4 | PR titled `... [break-changes]` | **`broken-gate` reports success having gated nothing**; `fixed-gate` fails closed |
| 5 | `Cut release` → `Promote release` | the release tag is minted at the candidate's own commit, asserted in-pipeline |
| 6 | `Ancestry report` | every consecutive tag transition is an ancestor relation |
| 7 | A red PR against a protected `main` | the merge button is blocked by the required check |

## The three defects, precisely

**The path filter never excludes anything.** `dorny/paths-filter` defaults to
`predicate-quantifier: some` and compiles each list entry into its own matcher. A
leading `!` therefore matches every path that is *not* the excluded one, so
`!app/vendor/**` returns true for `README.md`. Separately, `ci-*.ya?ml` matches
neither extension — in picomatch `?` is exactly one character, so it matches
`ci-xxx.yaXml`. The correction puts the exclusion inside a single extglob and spells
both extensions out.

Note that `some_with_excludes` is **not** the fix on v3 — that value only exists in
v4, spelled `some-with-excludes`, and v3 raises on an unrecognised value.

**The smoke test cannot pass.** Three blockers in sequence: the missing secrets blob,
then a cache connection in a ready hook, then a credentials lookup in the database
engine. The correction supplies a placeholder and applies overrides that already
existed for this exact purpose, while still executing the whole import chain.

One detail deliberately *not* reproduced: the real example env file carries a stray
unmatched quote on a base64 line. `docker run --env-file` tolerates it, because it
does no shell parsing — but this lab loads the file with `source`, which aborts on
it. Keeping it made the smoke job fail for the wrong reason and would have made the
demonstration dishonest, so the quote is removed here. It is harmless in the real
pipeline for the same reason: nothing shell-sources that file.

**The gate fails open.** `if: always()` runs the aggregator even when the run was
cancelled or the `changes` job failed. In both cases its output interpolates to an
empty string, which is not `"true"`, so the gate takes its early-out and reports
success having run nothing. As the sole required check, that turns a cancelled run
into a green merge authorisation. The correction refuses to run on cancellation and
asserts the `changes` job actually succeeded before trusting its output.

## Found by running it, not by reading it

**A release created with the default token does not trigger `release:` workflows.**
GitHub suppresses that to prevent recursive runs. Proven here: three releases
published, zero deploy runs. A pipeline that automates release creation *and*
deploys on the release event will silently stop deploying — no error, no failed
run, simply nothing. The fix in this repo is to call the deploy through
`workflow_call` instead of depending on the event. A token from a GitHub App or a
PAT would also work, at the cost of managing a credential.

**Skipping the back-merge loses the fix, immediately.** The first pass through this
lab cut `v0.1.0`, fixed a defect on the release branch during the soak, shipped it —
and then cut `v0.2.0` from trunk, which never received the fix. The ancestry report
caught it as a non-ancestor transition, and `git show v0.2.0:app/config.py` confirms
the fix is absent. One release, one regression. After back-merging with a true merge
commit, the next transition is an ancestor relation again.

**Nothing blocks a red pull request.** PR 1 reports `mergeable=MERGEABLE,
mergeStateStatus=UNSTABLE` — failing checks, merge permitted — because no required
check exists. Installing one needs GitHub Pro on a private repository; both the
rulesets API and classic branch protection return
`403 Upgrade to GitHub Pro or make this repository public`. That is the only
demonstration in this repo that cannot currently be run.

## The fail-open gate, as a merge authorisation

A ruleset on `main` requires exactly one check. With everything else held constant —
same pull request, same code, same check results — swapping which gate is required
changes whether the merge is allowed:

| Required check | PR "application change [break-changes]" |
|---|---|
| `fixed-gate` | `mergeStateStatus=BLOCKED` |
| `broken-gate` | `mergeStateStatus=UNSTABLE` — merge permitted |

On that pull request the `changes` job failed and no application job ran at all.
`broken-gate` reported success anyway, and as the required check it turned that into
permission to merge. This is the difference between a gate that fails closed and one
that fails open, expressed as the only thing that matters: whether the button works.

## A conflicted pull request gets no checks at all

Not a defect, but worth knowing before requiring a check. If GitHub cannot compute
the merge ref, it runs no `pull_request` workflows — the required check is never
reported, and the pull request sits waiting forever. "No checks reported" is not the
same as "checks passed", and the fix is to rebase or recreate the branch, because a
retarget alone does not re-run anything.

## The release train

```
main ──┬─────────────────────────────────────────────►
       │
       └── release/v0.1.0 ──●──────●
                         rc1    rc2 ──► v0.1.0
                                        same commit as rc2
```

`Promote release` resolves the candidate with `git rev-parse <rc>^{commit}` and tags
the release there, then asserts equality and ancestry before publishing. The rule
"ship the commit you validated" stops depending on anyone remembering it.

Tags are annotated throughout. A lightweight tag is a mutable pointer with no author
and no date; it can be deleted and recreated on different code leaving no trace, and
it sorts by commit date rather than tag date, which silently produces the wrong
release order in any audit.


<!-- A documentation-only change. It touches no application code. -->
