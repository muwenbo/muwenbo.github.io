# Blog Category Tabs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Professional/Human category tabs to the blog page so visitors can filter posts by category.

**Architecture:** Client-side JS filtering on a single `/blog/` page. Posts declare their category in front matter. The blog page renders all posts with `data-category` attributes, and a small script toggles visibility based on the active tab.

**Tech Stack:** Jekyll (Liquid templates), vanilla HTML/CSS/JS. No plugins.

---

### Task 1: Add `category` front matter to all posts

**Files:**
- Modify: `_posts/2025-02-20-llm-model-selection.md:1-6`
- Modify: `_posts/2025-02-28-rag-for-phenotype-analysis.md:1-6`
- Modify: `_posts/2025-03-14-custom-evaluation-for-ai-tools.md:1-5`
- Modify: `_posts/2025-03-28-ai-workflow-for-variant-classification.md:1-5`
- Modify: `_posts/2025-04-10-building-pvs1-prompts-part1.md:1-5`
- Modify: `_posts/2025-04-21-building-pvs1-prompts-part2.md:1-5`
- Modify: `_posts/2025-05-12-pvs1-agent-evolution.md:1-6`
- Modify: `_posts/2025-05-19-chatgene-launch.md:1-6`
- Modify: `_posts/2026-01-13-controlled-variant-interpretation-workflow.md:1-5`
- Modify: `_posts/2026-02-17-burning-tokens-for-geneticists.md:1-6`
- Modify: `_posts/2026-02-21-hnf1a-variant-classification-report.md:1-6`
- Modify: `_posts/2026-02-27-my-first-post.md:1-5`

**Step 1: Add `category: professional` to all technical posts**

Add `category: professional` line after the `date:` line (before `image:` or `tags:`) in these 11 posts:
- `2025-02-20-llm-model-selection.md`
- `2025-02-28-rag-for-phenotype-analysis.md`
- `2025-03-14-custom-evaluation-for-ai-tools.md`
- `2025-03-28-ai-workflow-for-variant-classification.md`
- `2025-04-10-building-pvs1-prompts-part1.md`
- `2025-04-21-building-pvs1-prompts-part2.md`
- `2025-05-12-pvs1-agent-evolution.md`
- `2025-05-19-chatgene-launch.md`
- `2026-01-13-controlled-variant-interpretation-workflow.md`
- `2026-02-17-burning-tokens-for-geneticists.md`
- `2026-02-21-hnf1a-variant-classification-report.md`

**Step 2: Add `category: human` to the intro post**

Add `category: human` to `2026-02-27-my-first-post.md`.

**Step 3: Verify front matter**

Run: `grep -l "^category:" _posts/*.md | wc -l`
Expected: `12` (all posts)

**Step 4: Commit**

```bash
git add _posts/*.md
git commit -m "feat: add category front matter to all posts"
```

---

### Task 2: Add tab UI and filtering to blog page

**Files:**
- Modify: `blog/index.md`

**Step 1: Add tab CSS**

Add these styles inside the existing `<style>` block in `blog/index.md`, after the `.timeline-thumb` media query (before `</style>`):

```css
.blog-tabs {
  display: flex;
  gap: 1.8rem;
  margin: 1.5rem 0 0;
  padding: 0;
  list-style: none;
  border-bottom: 1px solid #eee;
}

.blog-tabs li {
  padding: 0.5rem 0;
  font-size: 0.88rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #999;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.2s, border-color 0.2s;
}

.blog-tabs li:hover {
  color: #555;
}

.blog-tabs li.active {
  color: #111;
  border-bottom-color: #111;
}
```

**Step 2: Add tab HTML**

Replace `## Blog` (line 6) with:

```html
## Blog

<ul class="blog-tabs">
  <li class="active" data-filter="all">All</li>
  <li data-filter="professional">Professional</li>
  <li data-filter="human">Human</li>
</ul>
```

**Step 3: Add `data-category` to timeline items**

Change line 106:
```html
  <li class="timeline-item">
```
to:
```html
  <li class="timeline-item" data-category="{{ post.category }}">
```

**Step 4: Add filtering script**

Add this at the very end of `blog/index.md`:

```html
<script>
document.querySelectorAll('.blog-tabs li').forEach(function(tab) {
  tab.addEventListener('click', function() {
    document.querySelector('.blog-tabs li.active').classList.remove('active');
    tab.classList.add('active');
    var filter = tab.getAttribute('data-filter');
    document.querySelectorAll('.timeline-item').forEach(function(item) {
      if (filter === 'all' || item.getAttribute('data-category') === filter) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });
});
</script>
```

**Step 5: Build and verify locally**

Run: `bundle exec jekyll serve`
- Visit `http://localhost:4000/blog/`
- Verify three tabs appear: All, Professional, Human
- Click "Professional" -> only professional posts visible
- Click "Human" -> only human post visible
- Click "All" -> all posts visible

**Step 6: Commit**

```bash
git add blog/index.md
git commit -m "feat: add category tabs to blog page"
```

---

### Task 3: Final verification

**Step 1: Full build check**

Run: `bundle exec jekyll build`
Expected: No errors, clean build.

**Step 2: Visual check**

Run: `bundle exec jekyll serve`
- Verify homepage `/` still links to `/blog/`
- Verify blog page tabs work
- Verify individual post pages still render correctly
- Verify mobile view (tabs should wrap, thumbnails hidden as before)
