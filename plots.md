---
layout: default
title: Plots & Visualizations
---

**Navigation:** [Back to Papers]({{ "/" | relative_url }})

---
# Plots & Visualizations

{% assign plots = site.static_files | where_exp: "file", "file.path contains 'results'" | where_exp: "file", "file.extname == '.png'" %}
{% for plot in plots %}
## {{ plot.name | remove: ".png" | replace: "_", " " | replace: "-", " " | capitalize }}
![{{ plot.name }}]({{ plot.path | relative_url }})
{% endfor %}
