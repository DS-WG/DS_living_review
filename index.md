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

.paper-content ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.paper-content li {
  margin-bottom: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-left: 3px solid #0366d6;
  border-radius: 3px;
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

h2.section-header {
  margin-top: 2em;
  border-bottom: 2px solid #e1e4e8;
  padding-bottom: 10px;
}
</style>

# Dark Showers Papers - Living Review

*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. They connect different areas of theoretical physics with each other and arise from well motivated theoretical scenarios. Below is a list of papers concerning dark showers.*

<div class="stats-box">
<strong>Purpose:</strong> Collect and categorize dark showers references automatically<br>
<strong>Last updated:</strong> {{ site.time | date: "%B %d, %Y at %H:%M UTC" }}<br>
<strong>Repository:</strong> <a href="https://github.com/ds-wg/DS_living_review">ds-wg/DS_living_review</a>
</div>

**Navigation:** [View Plots & Visualizations]({{ "/plots" | relative_url }})


---
## Paper Categories

<div id="papers-container">
<p><em>Loading papers...</em></p>
</div>

<script>
function parseMarkdownLine(line) {
  // Convert **bold** to <strong>
  line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Convert [text](url) to <a>
  line = line.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
  return line;
}

fetch('{{ "/results/papers.txt" | relative_url }}')
  .then(response => {
    if (!response.ok) {
      throw new Error('README not found');
    }
    return response.text();
  })
  .then(markdown => {
    const lines = markdown.split('\n');
    let html = '';
    let currentSection = null;
    let currentCategory = null;
    let paperItems = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Skip header metadata
      if (line.startsWith('# **A Living Review') || 
          line.startsWith('*Dark showers sit') ||
          line.startsWith('The purpose of this note') ||
          line.startsWith('**Last updated:') ||
          line.startsWith('**Search period:') ||
          line.startsWith('**Total papers found:') ||
          line.startsWith('**Search categories:')) {
        continue;
      }
      
      // Skip empty lines
      if (line.trim() === '') {
        continue;
      }
      
      // H1 sections (like "# General")
      //if (line.match(/^# [^*]/) && !line.startsWith('# **')) {
        // Close previous category
      //  if (currentCategory && paperItems.length > 0) {
      //    html += '<ul>\n' + paperItems.join('\n') + '\n</ul>\n';
      //    html += '</div></details>\n\n';
      //    paperItems = [];
      //    currentCategory = null;
      //  }
        
        const sectionTitle = line.substring(2).trim();
        html += `<h2 class="section-header">${sectionTitle}</h2>\n\n`;
        currentSection = sectionTitle;
        continue;
      }
      
      // H2 categories (like "## Model Building - SU(N) (5 papers)")
      if (line.startsWith('## ')) {
        // Close previous category
        if (currentCategory && paperItems.length > 0) {
          html += '<ul>\n' + paperItems.join('\n') + '\n</ul>\n';
          html += '</div></details>\n\n';
          paperItems = [];
        }
        
        const categoryTitle = line.substring(3).trim();
        html += `<details>\n<summary>${categoryTitle}</summary>\n<div class="paper-content">\n`;
        currentCategory = categoryTitle;
        continue;
      }
      
      // Paper entries (bullets starting with *)
      if (line.trim().startsWith('* ') && currentCategory) {
        const paperContent = line.trim().substring(2); // Remove "* "
        const parsedContent = parseMarkdownLine(paperContent);
        paperItems.push(`<li>${parsedContent}</li>`);
      }
    }
    
    // Close last category
    if (currentCategory && paperItems.length > 0) {
      html += '<ul>\n' + paperItems.join('\n') + '\n</ul>\n';
      html += '</div></details>\n\n';
    }
    
    document.getElementById('papers-container').innerHTML = html || 
      '<p><strong>No papers found in README.</strong></p>';
  })
  .catch(error => {
    console.error('Error loading papers:', error);
    document.getElementById('papers-container').innerHTML = 
      '<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 16px; border-radius: 6px;">' +
      '<strong>Unable to load papers.</strong><br>' +
      'Error: ' + error.message + '<br><br>' +
      'Make sure:<br>' +
      '1. <code>results/README.md</code> exists in your repository<br>' +
      '2. <code>_config.yml</code> includes the results folder<br>' +
      '3. Wait 2-3 minutes after pushing changes for GitHub Pages to rebuild' +
      '</div>';
  });
</script>