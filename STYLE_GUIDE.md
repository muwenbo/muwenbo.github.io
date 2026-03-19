# Blog Format Style Guide

Derived from analysis of existing posts in `_posts/`.

---

## Professional Posts (`_posts/`)

### Front Matter

```yaml
---
layout: post
title: "Chinese title with English technical terms preserved"
date: YYYY-MM-DD
category: professional
image: /assets/images/posts/YYYY-MM-DD-slug/cover.jpg
tags: [tag1, tag2, tag3]
excerpt: "One-sentence Chinese teaser that hooks the reader."
---
```

**Rules:**
- `category` is always `professional`
- `image` path must match the post slug exactly: `YYYY-MM-DD-post-slug`
- Cover image is either `.jpg` or `.png`
- `excerpt` should be a complete sentence, written in Chinese, that poses a question or states the core value proposition
- `tags` are lowercase English terms from the domain: `bioinformatics`, `AI`, `LLM`, `ACMG`, `evaluation`, `product`, etc.

### Post Structure

```
## 引言       — Why this matters, what problem was faced
## [方法/背景] — How the work was approached
## [实验/结果] — What was found, with evidence
## 总结        — Reflection, limitations, takeaways
```

Subsections use `###`. Avoid going deeper than `###`.

### Language

- Primary language is **Chinese**
- Technical terms remain in **English**: gene names (`SLC2A1`, `HNF1A`), database names (`OMIM`, `ClinVar`, `HPO`), tools (`LangChain`), model names (`GPT-4o`, `Claude-3-opus`), standards (`ACMG`, `VCEP`), abbreviations (`LLM`, `RAG`, `AI`)
- Gene names use italics: `*SLC2A1*` → *SLC2A1*
- First-person singular (`我`) for solo experiments; first-person plural (`我们`) for team/product work

### Emphasis and Formatting

- `**Bold**` for key findings, warnings, important conclusions, and named entities being introduced
- Avoid italics for Chinese text; reserve italics for gene names and scientific notation
- Numbered lists for sequential steps or ranked results
- Bulleted lists for unordered items, feature sets, or observations

### Code Blocks

Always specify the language:

````markdown
```python
from langchain.prompts import ChatPromptTemplate
```
````

Supported languages used in existing posts: `python`, `bash`, `yaml`, `markdown`

### Images

```markdown
![Alt text describing the image](/assets/images/posts/YYYY-MM-DD-slug/filename.png)
```

- Place images inline where they are first referenced in the text
- Alt text should describe the image content in English
- Caption can follow as a `*italicized line*` below the image if needed

### Blockquotes

Use blockquotes (`>`) for:
- Quoted output from LLMs being evaluated
- Excerpts from external sources or databases
- Example responses being compared

### Horizontal Rules

Use `---` to separate major thematic breaks within a section (used sparingly, primarily in product announcement posts).

---

## General Conventions

### Post Length

800–3,000 words. Longer posts cover multi-step experiments with code and results.

### Title Style

Start with a domain-specific noun or question. Often includes a colon or dash to separate subject from angle. Examples:
- `基因诊断中的大模型选择：国产大模型能胜任吗？`
- `为遗传学家烧 Token`

### Excerpt / Opening Hook

The first paragraph should establish:
1. The specific problem or situation
2. Why it matters to the target reader (genetics professionals / bioinformaticians)
3. A hint at what approach was taken

Avoid generic introductions. Ground the reader in a concrete scenario immediately.

### Tone

Analytical and personal. Share genuine opinions on model performance, tool limitations, and lessons learned. Acknowledge limitations of experiments openly.
