# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a minimalist personal website for Wenbo Mu, hosted on GitHub Pages and built with Jekyll using the [tale](https://github.com/chesterhow/tale) remote theme.

## Commands

**Local development:**
```bash
bundle install          # Install Ruby dependencies
bundle exec jekyll serve  # Serve locally at http://localhost:4000
bundle exec jekyll build  # Build static site to _site/
```

**Dependencies:** Ruby + Bundler required. The site uses `github-pages` gem which pins Jekyll and plugin versions to match GitHub Pages.

## Architecture

- **`_config.yml`** — Site metadata, remote theme (`chesterhow/tale`), and plugin configuration.
- **`index.md`** — Single homepage with front matter `layout: default`. Content is Markdown with inline HTML/CSS.
- **`_includes/`** — Overrides for the tale theme: `navigation.html` (site header/nav) and `footer.html` (custom footer text).
- **`assets/`** — Favicon files (SVG, PNG variants).
- **`banner.jpg`** — Hero image referenced directly in `index.md`.

## Theme

The remote theme (`chesterhow/tale`) controls all layouts, base CSS, and page structure. To customize beyond what `_includes` overrides allow, you would need to copy theme files locally (e.g., `_layouts/`, `_sass/`). The site currently overrides only `navigation.html` and `footer.html`.

## Deployment

Pushing to the `main` branch automatically deploys via GitHub Pages. No CI/CD configuration needed — GitHub Pages handles the Jekyll build.
