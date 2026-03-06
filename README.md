# muwenbo.github.io

Personal website of Wenbo Mu — bioinformatician, traveler, snowboarder.

Live at **[muwenbo.github.io](https://muwenbo.github.io)**

## Stack

- [Jekyll](https://jekyllrb.com/) with the [tale](https://github.com/chesterhow/tale) remote theme
- Hosted on GitHub Pages

## Local development

```bash
bundle install
bundle exec jekyll serve
```

Open [http://localhost:4000](http://localhost:4000).

## Writing a new post

Add a file to `_posts/` following the naming convention:

```
_posts/YYYY-MM-DD-your-post-title.md
```

Minimal front matter:

```yaml
---
layout: post
title: "Your Post Title"
date: YYYY-MM-DD
---
```

Place images under `assets/images/`. The first image in a post is used as the thumbnail on the blog listing page.

## Structure

```
_includes/       # navigation and footer overrides
_posts/          # blog posts
assets/          # images, favicons
blog/            # blog listing page
index.md         # home page
_config.yml      # site settings
```

## Deployment

Push to `main` — GitHub Pages builds and deploys automatically.
