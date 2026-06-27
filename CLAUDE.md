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
