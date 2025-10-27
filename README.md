# Dark Showers Living Review

This repository hosts the **Dark Showers Living Review**, an evolving, community-maintained overview of research related to **dark shower phenomenology**, spanning both theoretical and experimental developments. It is part of the **Dark Showers Task Force**, a transversal effort across the BSM working groups at the **LHC Physics Centre at CERN (LPCC)**.

Website: [https://ds-taskforce.github.io/DS_living_review/](https://ds-taskforce.github.io/DS_living_review/)

---

## Purpose

The Dark Showers Living Review aims to collect, categorize, and visualize publications relevant to dark shower physics and related hidden-sector phenomena. By maintaining a continuously updated reference, the project provides an accessible resource for researchers studying:

- Hidden Valley models and confining dark sectors  
- Semi-visible and emerging jet signatures  
- Mediator topologies and long-lived particle phenomenology  
- Experimental searches and reinterpretations at the LHC  
- Monte Carlo and reconstruction developments for dark sectors  

---

## Repository Structure

DS_living_review/
├── index.md # Main overview page
├── contributions.md # Instructions for contributors
├── citation.md # Citation guidelines
├── plots.md # Figures and summary plots
├── scripts/ # Analysis and plotting scripts
│ ├── inspire_bib_generator.py
│ └── bsm_darkshowers_plotter.py
├── results/ # Generated plots, bibliographic data, summaries
│ ├── darkshowers_analysis.json
│ ├── papers_data.json
│ ├── darkshowers_summary.txt
│ ├── papers.txt
│ └── darkshowers_*.png
└── _config.yml # Jekyll site configuration


---

## How to Contribute

Contributions from both theory and experiment communities are welcome. 

Detailed contribution guidelines are available in [`contributions.md`](contributions.md).

---

## Scripts

Two Python utilities assist with data handling and visualization:

- `inspire_bib_generator.py`  
  Parses Inspire-HEP bibliographic data and generates reference files.  

- `bsm_darkshowers_plotter.py`  
  Produces keyword distributions, yearly trends, and category breakdowns from the bibliographic data.  

Generated outputs are stored in the `results/` directory.

---

## Building the Website

The living review is built using **Jekyll**. To build locally:

```bash
# Clone repository
git clone https://github.com/DS-taskforce/DS_living_review.git
cd DS_living_review

# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

