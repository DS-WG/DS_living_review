---
layout: default
title: Dark Showers Papers - Living Review
---

<style>
details {
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
}

summary {
  cursor: pointer;
  font-weight: bold;
  font-size: 1.2em;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  user-select: none;
}

summary:hover {
  background-color: #e0e0e0;
}

details[open] summary {
  margin-bottom: 15px;
  border-bottom: 2px solid #ddd;
}

.paper-list {
  margin-left: 20px;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 20px auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
}

.stats-box {
  background-color: #f8f9fa;
  border-left: 4px solid #0366d6;
  padding: 15px;
  margin: 20px 0;
}
</style>

# Dark Showers Papers - Living Review

*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. They connect different areas of theoretical physics with each other and arise from well motivated theoretical scenarios. Below is a list of papers concerning dark showers.*

The purpose of this site is to collect references for dark showers. Papers are automatically categorized using keyword matching on titles and abstracts. Papers may appear in multiple categories if relevant.

<div class="stats-box">
<strong>Last updated:</strong> {{ site.time | date: "%B %d, %Y" }}<br>
<strong>Repository:</strong> <a href="https://github.com/ds-wg/DS_living_review">GitHub</a>
</div>

---

## Plots & Visualizations

{% assign image_files = site.static_files | where_exp: "file", "file.extname == '.png'" %}
{% if image_files.size > 0 %}
{% for image in image_files %}
### {{ image.basename | replace: "_", " " | replace: "-", " " | capitalize }}
![{{ image.basename }}]({{ image.path | relative_url }})
{% endfor %}
{% else %}
*Plots will appear here after the first data update runs.*
{% endif %}

---

## Paper Categories

{% capture readme_path %}{{ site.baseurl }}/results/README.md{% endcapture %}

<!-- Include README content directly -->
{% if site.data.readme %}
{{ site.data.readme }}
{% else %}

<!-- Fallback: Load from file using JavaScript -->
<div id="paper-content">
<p><em>Loading paper categories...</em></p>
</div>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
fetch('{{ site.baseurl }}/results/README.md')
  .then(response => {
    if (!response.ok) throw new Error('README not found');
    return response.text();
  })
  .then(text => {
    // Parse markdown
    const html = marked.parse(text);
    
    // Convert H2 headers to collapsible details/summary
    const modifiedHtml = html.replace(
      /<h2>(.*?)<\/h2>/g, 
      '</details><details open><summary>$1</summary>'
    );
    
    document.getElementById('paper-content').innerHTML = 
      modifiedHtml + '</details>';
    
    // Remove the first closing tag
    const content = document.getElementById('paper-content');
    if (content.firstChild && content.firstChild.tagName === 'DETAILS') {
      content.firstChild.remove();
    }
  })
  .catch(error => {
    console.error('Error loading papers:', error);
    document.getElementById('paper-content').innerHTML = 
      '<p><strong>No paper data available yet.</strong> Run the update workflow to generate paper listings.</p>' +
      '<p>Go to: <a href="https://github.com/ds-wg/DS_living_review/actions">Actions</a> → ' +
      'Update Dark Showers Papers → Run workflow</p>';
  });
</script>
{% endif %}