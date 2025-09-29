---
layout: default
title: Dark Showers Papers - Living Review
---

# Dark Showers Papers - Living Review

*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. They connect different areas of theoretical physics with each other and arise from well motivated theoretical scenarios. Below is a list of papers concerning dark showers.*

The purpose of this site is to collect references for dark showers. Papers are automatically categorized using keyword matching on titles and abstracts. Papers may appear in multiple categories if relevant.

---

## Quick Navigation

- [Plots & Visualizations](#plots--visualizations)
- [Paper Categories](#paper-categories)
- [Statistics](#statistics)

---

## Plots & Visualizations

{% if site.static_files %}
{% assign plot_files = site.static_files | where: "extname", ".png" | where_exp: "file", "file.path contains 'results'" %}
{% for file in plot_files %}
### {{ file.basename | replace: "_", " " | replace: "-", " " | capitalize }}
![{{ file.basename }}]({{ file.path | relative_url }})
{% endfor %}
{% endif %}

---

## Paper Categories

{% assign readme_content = site.data.papers_content %}
{% if readme_content %}
{{ readme_content | markdownify }}
{% else %}
<!-- Papers will be populated from the generated data -->
Loading paper categories...

<script>
// Fallback: Load README.md content if data file is not available
fetch('{{ "/results/README.md" | relative_url }}')
  .then(response => response.text())
  .then(data => {
    document.getElementById('paper-content').innerHTML = marked.parse(data);
    addCollapsibleSections();
  })
  .catch(error => console.log('No README.md found in results/'));
</script>
{% endif %}

<div id="paper-content"></div>

---

## Statistics

Last updated: {{ site.data.stats.last_updated | default: "Unknown" }}  
Total papers: {{ site.data.stats.total_papers | default: "Loading..." }}  
Categories searched: hep-ph, hep-th, hep-lat, hep-ex  

<script>
// Add collapsible functionality to category sections
function addCollapsibleSections() {
  const headings = document.querySelectorAll('h2, h3');
  
  headings.forEach(heading => {
    if (heading.tagName === 'H2' && !heading.textContent.includes('Navigation') && 
        !heading.textContent.includes('Plots') && !heading.textContent.includes('Statistics')) {
      
      // Create collapsible wrapper
      const content = [];
      let sibling = heading.nextElementSibling;
      
      while (sibling && sibling.tagName !== 'H1' && sibling.tagName !== 'H2') {
        content.push(sibling);
        sibling = sibling.nextElementSibling;
      }
      
      if (content.length > 0) {
        // Make heading clickable
        heading.style.cursor = 'pointer';
        heading.innerHTML = '▼ ' + heading.innerHTML;
        
        // Wrap content in collapsible div
        const wrapper = document.createElement('div');
        wrapper.className = 'collapsible-content';
        wrapper.style.display = 'block';
        
        content.forEach(element => {
          wrapper.appendChild(element.cloneNode(true));
          element.remove();
        });
        
        heading.parentNode.insertBefore(wrapper, heading.nextSibling);
        
        // Add click handler
        heading.addEventListener('click', function() {
          const content = this.nextElementSibling;
          if (content.style.display === 'none') {
            content.style.display = 'block';
            this.innerHTML = this.innerHTML.replace('►', '▼');
          } else {
            content.style.display = 'none';
            this.innerHTML = this.innerHTML.replace('▼', '►');
          }
        });
      }
    }
  });
}

// Initialize collapsible sections when page loads
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(addCollapsibleSections, 1000);
});
</script>

<style>
.collapsible-content {
  margin-left: 20px;
  padding-left: 15px;
  border-left: 2px solid #e0e0e0;
}

h2:hover {
  color: #0366d6;
}

.category-header {
  cursor: pointer;
  user-select: none;
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
</style>