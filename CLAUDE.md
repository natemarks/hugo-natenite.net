# natenite.net

Hugo static website for natenite.net.

## Stack

- **Hugo** (extended edition, min v0.55.0)
- **Theme**: hugo-serif-theme (git submodule in `themes/`)
- **Site URL**: https://natenite.net

## Project Structure

- `content/` — Hugo content (markdown files)
- `static/` — Static assets (images, etc.)
- `themes/hugo-serif-theme/` — Serif theme submodule
- `config.toml` — Hugo site configuration
- `public/` — Generated site output (git-ignored)
- `scripts/` — Build and deployment scripts

## Development

```bash
# Local dev server with drafts
hugo server -D

# Build site
hugo
```

Output goes to `public/`.

## Deployment

Run `make` for common checks, then upload `public/` to S3 bucket.

Scripts for deployment should be in `scripts/`.

## Configuration

- Base URL and theme set in `config.toml`
- Primary color: `#4682B4`
- Complementary color: `#B47846`
- Fonts: Playfair Display (headings), Source Sans Pro (body)

## Static Analysis & Testing Standards

The Python tooling in `scripts/` (currently `sync_calendar.py`, which regenerates `static/events.ics` from `data/events.json`) follows opinionated standards enforced by the `scaffold-project` skill:

1. **Pinned Dependencies**: all versions in `requirements.txt` are pinned to exact versions
2. **Static Analysis**: run `make static` before committing
3. **Pre-commit Hooks**: configured with gitleaks and `make static` (`pre-commit install` to enable)
4. **Dependabot**: configured for automated weekly updates (`pip` + `github-actions`)
5. **CI/CD**: GitHub Actions runs `make static-check` on PRs and `main` pushes

### Available Make Targets

Run `make help` to see all available targets. Key ones:

- `make static` — run all static analysis checks with auto-format (black, mypy, shellcheck, pylint, unit tests)
- `make static-check` — same, but check-only (no auto-format); what CI runs
- `make unit` — run unit tests (`tests/`, `pytest -m unit`)
- `make unit-update-golden` — update golden/snapshot files
- `make integration` — run integration tests (manual, requires credentials)
- `make sync-calendar` — regenerate `static/events.ics` from `data/events.json`

This project has no CDK or Packer components — those template sections don't apply here.
