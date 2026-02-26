# Release Process

This document describes how to cut a new release of `logpilot`.

Releases are published to [PyPI](https://pypi.org/project/logpilot/) and a
corresponding [GitHub Release](https://github.com/colinmakerofthings/logpilot-cli/releases)
is created automatically by the [release workflow](.github/workflows/release.yml).

---

## Prerequisites (one-time setup)

These steps only need to be done once before the very first release.

### 1. Configure PyPI Trusted Publishing

`logpilot` uses [OIDC Trusted Publishing](https://docs.pypi.org/trusted-publishers/) —
no PyPI API token is required.

1. Log in to [pypi.org](https://pypi.org) and go to your account's
   *Publishing* settings (or the project page once it exists).
2. Click **Add a new publisher** and fill in:
   | Field | Value |
   |---|---|
   | Owner | `colinmakerofthings` |
   | Repository | `logpilot-cli` |
   | Workflow filename | `release.yml` |
   | Environment name | `pypi` |
3. Save. No secrets need to be added to GitHub.

### 2. Create the `pypi` GitHub environment

1. In the GitHub repo go to **Settings → Environments → New environment**.
2. Name it `pypi`.
3. Optionally add a required reviewer for an extra approval gate before
   publishing.

---

## Release checklist

Work through these steps in order every time you release a new version.

### Step 1 — Decide the new version number

Follow [Semantic Versioning](https://semver.org/):

| Change type | Example bump |
|---|---|
| Bug fixes only | `0.1.0 → 0.1.1` |
| New backwards-compatible features | `0.1.0 → 0.2.0` |
| Breaking changes | `0.1.0 → 1.0.0` |
| Pre-release / release candidate | `0.2.0-rc1` |

### Step 2 — Update `pyproject.toml`

Bump the `version` field:

```toml
[project]
name = "logpilot"
version = "0.2.0"   # ← new version
```

### Step 3 — Update `CHANGELOG.md`

1. Add a new version section under `## [Unreleased]`, using today's date:

   ```markdown
   ## [0.2.0] - YYYY-MM-DD

   ### Added
   - …

   ### Fixed
   - …

   ### Changed
   - …
   ```

2. Leave `## [Unreleased]` empty above it (for the next cycle).

3. Add a comparison link at the bottom of the file:

   ```markdown
   [0.2.0]: https://github.com/colinmakerofthings/logpilot-cli/compare/v0.1.0...v0.2.0
   ```

   And update the `[Unreleased]` link:

   ```markdown
   [Unreleased]: https://github.com/colinmakerofthings/logpilot-cli/compare/v0.2.0...HEAD
   ```

### Step 4 — Commit and tag

```sh
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.2.0"

git tag v0.2.0
git push origin main
git push origin v0.2.0
```

> Pushing the tag triggers the release workflow. The version tag **must**
> match the `version` field in `pyproject.toml` exactly (prefixed with `v`).

---

## What the release workflow does

The [`.github/workflows/release.yml`](.github/workflows/release.yml) pipeline
runs automatically when a `v*.*.*` tag is pushed. It has four sequential jobs:

```
test  →  build  →  publish-pypi  →  github-release
```

| Job | What it does |
|---|---|
| **test** | Runs the full pytest suite across Python 3.11/3.12/3.13 on Ubuntu, Windows, and macOS. A failure here aborts the release. |
| **build** | Builds the sdist (`*.tar.gz`) and wheel (`*.whl`) using `python -m build`. Artifacts are uploaded for the subsequent jobs. |
| **publish-pypi** | Publishes the distribution to PyPI using OIDC trusted publishing (no API token required). Runs inside the `pypi` GitHub environment. |
| **github-release** | Creates a GitHub Release for the tag, attaches the sdist and wheel, and auto-generates release notes from merged PRs / commits since the last tag. Tags containing a hyphen (e.g. `v1.0.0-rc1`) are automatically marked as pre-releases. |

---

## Pre-releases

To publish a release candidate or alpha without marking it as the latest stable
release on PyPI, use a version number with a hyphen suffix:

```sh
# pyproject.toml → version = "0.2.0-rc1"
git tag v0.2.0-rc1
git push origin v0.2.0-rc1
```

The workflow detects the hyphen and sets `prerelease: true` on the GitHub
Release automatically. PyPI also treats `rc`, `a`, `b` suffixes as
pre-releases and will not serve them to users who run `pip install logpilot`
without `--pre`.

---

## Verifying the release

After the workflow completes:

1. Check the [GitHub Release](https://github.com/colinmakerofthings/logpilot-cli/releases)
   page — the sdist and wheel should be attached.
2. Check [PyPI](https://pypi.org/project/logpilot/) — the new version should
   be visible within a few minutes.
3. Smoke-test in a clean environment:

   ```sh
   pip install logpilot==0.2.0
   logpilot --version
   ```

---

## Troubleshooting

| Problem | Resolution |
|---|---|
| `publish-pypi` fails with a 403 | Check that the Trusted Publisher on PyPI is configured exactly as described in the prerequisites. |
| Tests fail on the tag push | Fix the failing tests on `main`, delete the tag (`git tag -d v0.x.x && git push origin :refs/tags/v0.x.x`), and re-tag after merging the fix. |
| Wrong version shown by `logpilot --version` | Ensure the `version` in `pyproject.toml` and the git tag match, and that the package was reinstalled after the bump. |
