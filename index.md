---
layout: default
title: Dark Showers Papers - Living Review
---

<style>
details {
  margin: 20px 0;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 0;
}

summary {
  cursor: pointer;
  font-weight: bold;
  font-size: 1.3em;
  padding: 16px;
  background-color: #f6f8fa;
  border-radius: 6px;
  user-select: none;
  list-style: none;
}

summary::-webkit-details-marker {
  display: none;
}

summary:before {
  content: "▶ ";
  display: inline-block;
  transition: transform 0.2s;
}

details[open] summary:before {
  transform: rotate(90deg);
}

summary:hover {
  background-color: #e1e4e8;
}

details[open] summary {
  border-bottom: 2px solid #e1e4e8;
  border-radius: 6px 6px 0 0;
}

.paper-content {
  padding: 16px;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 20px auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  background: white;
}

.stats-box {
  background-color: #f6f8fa;
  border-left: 4px solid #0366d6;
  padding: 16px;
  margin: 20px 0;
  border-radius: 6px;
}

.no-papers {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 16px;
  margin: 20px 0;
  border-radius: 6px;
}
</style>

# Dark Showers Papers - Living Review

*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. They connect different areas of theoretical physics with each other and arise from well motivated theoretical scenarios. Below is a list of papers concerning dark showers.*

<div class="stats-box">
<strong>Purpose:</strong> Collect and categorize dark showers references automatically<br>
<strong>Last updated:</strong> {{ site.time | date: "%B %d, %Y at %H:%M UTC" }}<br>
<strong>Repository:</strong> <a href="https://github.com/ds-wg/DS_living_review">ds-wg/DS_living_review</a>
</div>

---

## Plots & Visualizations

{% assign plots = site.static_files | where_exp: "file", "file.path contains 'results'" | where_exp: "file", "file.extname == '.png'" %}
{% if plots.size > 0 %}
{% for plot in plots %}
<h3>{{ plot.name | remove: ".png" | replace: "_", " " | replace: "-", " " | capitalize }}</h3>
![{{ plot.name }}]({{ plot.path | relative_url }})
{% endfor %}
{% else %}
<div class="no-papers">
<strong>No plots available yet.</strong> Run the workflow or scripts locally to generate visualizations.
</div>
{% endif %}

---

## Paper Categories

<div id="papers-container">
<p><em>Loading papers...</em></p>
</div>

<script>
// Fetch and parse the README
fetch('{{ "/results/README.md" | relative_url }}')
  .then(response => {
    if (!response.ok) {
      throw new Error('README not found at: {{ "/results/README.md" | relative_url }}');
    }
    return response.text();
  })
  .then(markdown => {
    const container = document.getElementById('papers-container');
    
    // Split by H1 and H2 headers
    const lines = markdown.split('\n');
    let html = '';
    let inCategory = false;
    let categoryContent = '';
    let currentCategory = '';
    
    lines.forEach(line => {
      // Skip the title and metadata at the beginning
      if (line.startsWith('# **A Living Review')) return;
      if (line.startsWith('*Dark showers sit')) return;
      if (line.startsWith('The purpose of this note')) return;
      if (line.startsWith('**Last updated:')) return;
      if (line.startsWith('**Search period:')) return;
      if (line.startsWith('**Total papers found:')) return;
      if (line.startsWith('**Search categories:')) return;
      
      // Detect major sections (H1)
      if (line.match(/^# [^*]/)) {
        if (inCategory && categoryContent) {
          html += `</div></details>`;
        }
        const sectionTitle = line.replace(/^# /, '');
        html += `<h2 style="margin-top: 2em; border-bottom: 2px solid #e1e4e8; padding-bottom: 10px;">${sectionTitle}</h2>`;
        inCategory = false;
        return;
      }
      
      // Detect category headers (H2)
      if (line.match(/^## /)) {
        // Close previous category if open
        if (inCategory && categoryContent) {
          html += categoryContent + `</div></details>`;
        }
        
        // Extract category name and paper count
        currentCategory = line.replace(/^## /, '');
        html += `<details open><summary>${currentCategory}</summary><div class="paper-content">`;
        categoryContent = '';
        inCategory = true;
        return;
      }
      
      // Add content to current category
      if (inCategory) {
        categoryContent += line + '\n';
      }
    });
    
    // Close last category
    if (inCategory && categoryContent) {
      html += categoryContent + `</div></details>`;
    }
    
    // Process the categoryContent for each section
    html = html.replace(/<div class="paper-content">([\s\S]*?)<\/div>/g, function(match, content) {
      // Split into lines
      let lines = content.split('\n');
      let processedLines = [];
      let inList = false;
      
      lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        // Check if line starts with bullet point
        if (line.startsWith('* ')) {
          if (!inList) {
            processedLines.push('<ul style="list-style: none; padding-left: 0; margin: 10px 0;">');
            inList = true;
          }
          
          // Remove the bullet and process markdown
          let content = line.substring(2);
          
          // Convert markdown bold
          content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          
          // Convert markdown links
          content = content.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
          
          processedLines.push('<li style="margin-bottom: 8px; padding: 8px; background: #f9f9f9; border-left: 3px solid #0366d6;">' + content + '</li>');
        } else {
          if (inList) {
            processedLines.push('</ul>');
            inList = false;
          }
          processedLines.push('<p>' + line + '</p>');
        }
      });
      
      if (inList) {
        processedLines.push('</ul>');
      }
      
      return '<div class="paper-content">' + processedLines.join('\n') + '</div>';
    });
    
    container.innerHTML = html || '<div class="no-papers"><strong>No papers found.</strong> Run the update workflow to populate the paper database.</div>';
  })
  .catch(error => {
    console.error('Error loading papers:', error);
    document.getElementById('papers-container').innerHTML = 
      `<div class="no-papers">
        <strong>Unable to load paper data.</strong><br>
        Error: ${error.message}<br><br>
        <strong>Next steps:</strong>
        <ol>
          <li>Verify that <code>results/README.md</code> exists in your repository</li>
          <li>Check that <code>_config.yml</code> includes <code>results/</code> folder</li>
          <li>Run the update workflow from <a href="https://github.com/ds-wg/DS_living_review/actions">GitHub Actions</a></li>
        </ol>
      </div>`;
  });
</script>