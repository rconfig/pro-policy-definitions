# CLAUDE.md

## What this repo is

Compliance policy definitions for rConfig Pro: hardening topic files, generated framework files,
operational standards and baselines, per vendor. Contribution format and checks are in
`CONTRIBUTING.md`.

## Verification

All three checks MUST pass before a change is reported complete or released. CI runs the same
commands on every push and pull request (`.github/workflows/lint.yml`).

```bash
python3 .tooling/scripts/test_lint.py
python3 .tooling/scripts/generate_frameworks.py --check
python3 .tooling/scripts/lint.py
```

## Releases and tagging

Adapted from the process in the rConfig-templates repository. Every release gets a version bump,
an annotated tag and a GitHub Release. All three are required, and a release is not finished
until the GitHub Release is published.

`main` is live. rConfig Pro's `rconfig:clone-templates --repo=policies` clones the default branch
with no pinned ref, so anything merged to `main` reaches customers on their next import. The tag
records what shipped and gives anyone who needs a fixed set of policies a ref that does not move.

### Version numbers

- **Annotated tags only, `vMAJOR.MINOR.PATCH`**, unprefixed, for example
  `git tag -a v1.5.0 -m "..."`. Never create a lightweight tag. `v1.0.0` to `v1.3.0` are
  lightweight; they are already pushed, so leave them as they are.
- **The version lives in two places, bumped together before tagging**: the root `VERSION` file
  (the bare number, for example `1.5.0`) and the newest dated heading in `CHANGELOG.md`
  (`## [1.5.0] - YYYY-MM-DD`). The tag, `VERSION` and the CHANGELOG heading MUST match.
- **Increment from the latest tag** (`git tag -l --sort=-v:refname | head -1`), not from memory.

### What each part of the version means

Semantic versioning applies to what a user imports and what result it gives.

- **MAJOR**: a published `.policy` file is renamed, moved or deleted, or the policy or
  `.meta.yaml` format changes so that a supported rConfig release can no longer read it.
- **MINOR**: a new vendor, policy file, rule or sample, or any change to a rule that changes a
  pass or fail result (new rule, removed rule, changed method or pattern). This includes
  regenerated framework files, because they change when their topic files do.
- **PATCH**: documentation, descriptions, comments, metadata that does not change results,
  tooling and CI. No `.tooling/expected/` result changes in a PATCH release.

When a release mixes changes, the highest level wins. Several vendors added on the same day go
out as one MINOR release, not one release per vendor, unless they are merged separately.

### CHANGELOG

- Work in progress goes under `## [Unreleased]` (see `CONTRIBUTING.md`). At release time, rename
  that heading to the new version with today's date and add a fresh empty `## [Unreleased]` above
  it.
- Use the Keep a Changelog headings (`Added`, `Changed`, `Removed`, `Fixed`).
- Any renamed or deleted policy file is listed under `Removed` or `Changed` with its old and new
  path, so a user can find it again.

### Release steps

1. Run the three verification commands. All must pass.
2. Decide the version from the rules above and the latest tag.
3. Update `VERSION` and the `CHANGELOG.md` heading. Commit as `Release vX.Y.Z`.
4. Create the annotated tag on that commit. The message is one line: the release title and the
   headline change, for example `rConfig Policy Definitions 1.5.0: Arista EOS and Palo Alto
   PAN-OS topic files`.
5. Push the commit and the tag: `git push origin main && git push origin vX.Y.Z`.
6. Write the release notes to a file in the scratchpad, then publish:
   `gh release create vX.Y.Z --title "rConfig Policy Definitions X.Y.Z" --notes-file <file> --verify-tag`.
7. Confirm with `gh release view vX.Y.Z` and report the release URL.

### Release notes

The release body is not the CHANGELOG entry pasted in. It is:

- An opening line on what a user must do, if anything. Lead with any renamed or deleted policy
  file, since a user who imported it must re-import it. If there is nothing to do, say so, for
  example "No policy files were renamed or removed."
- The minimum rConfig Pro version any new policy needs, if it is higher than before.
- Condensed one-line bullets under the Keep a Changelog headings that apply.
- The last line: `See CHANGELOG.md for detail.`

### Rules that do not bend

- **Never move, delete or re-point a pushed tag.** If a published release is wrong, leave it and
  fix it in the next release.
- **Never release with failing checks** or with uncommitted changes in the working tree that are
  meant for the release.
- **Commit, tag, push and publish only when Stephen asks for the release.** Approval for one
  release does not carry over to the next.
