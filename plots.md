---
layout: default
title: Plots & Visualizations
---
<nav class="nav-tabs">
  <a href="{{ '/' | relative_url }}" class="nav-tab">📚 Papers</a>
  <a href="{{ '/plots' | relative_url }}" class="nav-tab active">📊 Plots</a>
</nav>

# Plots & Visualizations

{% assign plots = site.static_files | where_exp: "file", "file.path contains 'results'" | where_exp: "file", "file.extname == '.png'" %}
{% for plot in plots %}
## {{ plot.name | remove: ".png" | replace: "_", " " | replace: "-", " " | capitalize }}
![{{ plot.name }}]({{ plot.path | relative_url }})
{% endfor %}
