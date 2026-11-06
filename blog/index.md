---
layout: default
title: Blog
---

## Blog

<ul class="blog-tabs">
  <li class="active" data-filter="all">All</li>
  <li data-filter="professional">Professional</li>
  <li data-filter="human">Human</li>
</ul>

<style>
.timeline {
  list-style: none;
  padding: 0;
  margin: 2rem 0 0;
}

.timeline-item {
  margin-bottom: 2.8rem;
  padding-left: 0;
  border-left: 3px solid transparent;
  transition: border-color 0.2s ease, padding-left 0.2s ease;
}

.timeline-item:hover {
  border-left-color: var(--brand);
  padding-left: 0.9rem;
}

.timeline-date {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--stone);
  margin-bottom: 0.45rem;
}

.timeline-rule {
  border: none;
  border-top: 1px solid var(--near-black);
  margin: 0 0 1rem 0;
}

.timeline-row {
  display: flex;
  gap: 1.4rem;
  align-items: flex-start;
}

.timeline-content {
  flex: 1;
  min-width: 0;
}

.timeline-content h2 {
  margin: 0 0 0.45rem 0;
  font-size: 1.2rem;
  line-height: 1.35;
}

.timeline-content h2 a {
  text-decoration: none;
  color: inherit;
}

.timeline-content h2 a:hover {
  text-decoration: underline;
}

.timeline-excerpt {
  margin: 0;
  color: var(--olive);
  font-size: 0.93rem;
  line-height: 1.6;
}

.timeline-thumb {
  flex-shrink: 0;
  width: 148px;
}

.timeline-thumb img {
  width: 100%;
  height: 94px;
  object-fit: cover;
  display: block;
}

@media (max-width: 500px) {
  .timeline-thumb { display: none; }
}

.blog-tabs {
  display: flex;
  gap: 1.8rem;
  margin: 1.5rem 0 0;
  padding: 0;
  list-style: none;
  border-bottom: 1px solid var(--border);
}

.blog-tabs li {
  padding: 0.5rem 0;
  font-size: 0.88rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--stone);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.2s, border-color 0.2s;
}

.blog-tabs li:hover {
  color: var(--dark-warm);
}

.blog-tabs li.active {
  color: var(--brand);
  border-bottom-color: var(--brand);
}
</style>

<ul class="timeline">
{% for post in site.posts %}
  {% comment %} Extract first image src from rendered HTML content {% endcomment %}
  {% if post.image %}
    {% assign thumb = post.image %}
  {% else %}
    {% assign content_parts = post.content | split: 'src="' %}
    {% if content_parts.size > 1 %}
      {% assign thumb = content_parts[1] | split: '"' | first %}
    {% else %}
      {% assign thumb = nil %}
    {% endif %}
  {% endif %}

  <li class="timeline-item" data-category="{{ post.category }}">
    <div class="timeline-date">{{ post.date | date: "%B %-d, %Y" }}</div>
    <hr class="timeline-rule">
    <div class="timeline-row">
      <div class="timeline-content">
        <h2><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a></h2>
        <p class="timeline-excerpt">{{ post.excerpt | strip_html | truncatewords: 28 }}</p>
      </div>
      {% if thumb %}
      <div class="timeline-thumb">
        <a href="{{ post.url | prepend: site.baseurl }}">
          <img src="{{ thumb }}" alt="{{ post.title | escape }}">
        </a>
      </div>
      {% endif %}
    </div>
  </li>
{% endfor %}
</ul>

{% if site.posts.size == 0 %}
<p>No posts yet. Check back soon.</p>
{% endif %}

<script>
// Filter by category. Deep-linkable: /blog/#professional or /blog/#human
function applyFilter(filter) {
  var tab = document.querySelector('.blog-tabs li[data-filter="' + filter + '"]');
  if (!tab) { filter = 'all'; tab = document.querySelector('.blog-tabs li[data-filter="all"]'); }
  document.querySelector('.blog-tabs li.active').classList.remove('active');
  tab.classList.add('active');
  document.querySelectorAll('.timeline-item').forEach(function(item) {
    item.style.display = (filter === 'all' || item.getAttribute('data-category') === filter) ? '' : 'none';
  });
}
document.querySelectorAll('.blog-tabs li').forEach(function(tab) {
  tab.addEventListener('click', function() {
    var filter = tab.getAttribute('data-filter');
    history.replaceState(null, '', filter === 'all' ? location.pathname : '#' + filter);
    applyFilter(filter);
  });
});
applyFilter(location.hash.slice(1) || 'all');
window.addEventListener('hashchange', function() { applyFilter(location.hash.slice(1) || 'all'); });
</script>
