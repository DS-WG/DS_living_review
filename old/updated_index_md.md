---
layout: default
title: Home
---

# A Living Review of Dark Showers

*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. They connect different areas of theoretical physics with each other and arise from well motivated theoretical scenarios.*

## About This Review

This living review automatically collects and categorizes papers related to dark showers from the arXiv. Papers are organized by theoretical approach, experimental method, and phenomenological application.

**Last updated:** {{ site.data.papers.last_updated | date: "%Y-%m-%d" }}

---

## Quick Navigation

- [📚 **All Papers by Category**](#papers-by-category)
- [🔬 **Experimental Papers**](#experimental--phenomenology)
- [🏗️ **Model Building**](#model-building)
- [🌌 **Dark Matter**](#dark-matter)
- [⚛️ **Lattice QCD**](#lattice-qcd)

---

<div class="stats-box" markdown="1">
**Repository Statistics:**
- 📄 Total papers: {{ site.data.papers.total_papers | default: "Loading..." }}
- 📅 Date range: {{ site.data.stats.date_range | default: "2023-present" }}
- 🏷️ Categories: {{ site.data.stats.categories | default: "14" }}
- 🔄 Last update: {{ site.data.stats.last_update | default: "Updating..." }}
</div>

---

## Papers by Category

{% include paper-list.html %}

---

## Contributing

This review is automatically updated. If you notice missing papers or categorization issues, please:
- 🐛 [Open an issue]({{ site.github.repository_url }}/issues)
- 🔧 [Submit a pull request]({{ site.github.repository_url }}/pulls)

## Citation

If you find this review useful, please cite:
```
@misc{darkshowers-living-review,
  title={A Living Review of Dark Showers},
  author={Dark Showers Working Group},
  year={2025},
  url={https://your-username.github.io/your-repo-name}
}
```

<style>
.stats-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  text-align: center;
}

.stats-box strong {
  color: #fff;
}
</style>