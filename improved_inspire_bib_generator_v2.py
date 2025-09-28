"""
Combined script to search Inspire HEP for papers and generate bibliography files
Enhanced with improved search queries and classification system
"""

import json
import os
import re
import datetime
from datetime import date
from collections import defaultdict, Counter
import requests
import argparse


class InspireBibGenerator:
    def __init__(self, starting_date=None, output_dir="results"):
        self.starting_date = starting_date or date.today().replace(year=date.today().year - 1)
        self.output_dir = output_dir
        self.categories = ['hep-ph', 'hep-ex', 'hep-th', 'hep-lat']  # Added missing categories
        self.keywords = [
            'dark showers', 'dark shower', 'hidden valley', 'hidden valleys',
            'dark pion', 'dark pions', 'dark baryons', 'SUEP','soft-bombs',
            'soft bombs','soft-bomb','soft bomb',
            'dark hadron', 'dark hadrons', 'dark QCD', 'confining dark sector',
            'semi-visible jets', 'emerging jets', 'soft unclustered energy',
            'dark mesons', 'composite dark matter', 'dark confinement'
        ]
        self.papers = []
        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Collaboration names for BibTeX formatting
        self.collab_names = {
            'ATLAS': 'ATLAS Collaboration',
            'CMS': 'CMS Collaboration',
            'LHCb': 'LHCb Collaboration',
            'ALICE': 'ALICE Collaboration',
            'H1': 'H1 Collaboration',
            'IceCube': 'IceCube Collaboration',
            'NNPDF': 'NNPDF Collaboration',
            'Belle-II': "Belle-II Collaboration",
            'Belle II': "Belle-II Collaboration",
            'BESIII': "BESIII Collaboration",
            'DARWIN': "DARWIN Collaboration",
            'MODE': "MODE Collaboration",
            'DUNE': "DUNE Collaboration",
            'MAP': "MAP Collaboration",
            'QUEST-DMC': "QUEST-DMC Collaboration",
            'JETSCAPE': "JETSCAPE Collaboration",
            'Hyper-Kamiokande': "Hyper-Kamiokande Collaboration"
        }

        def generate_jekyll_data(self):
            """Generate data files for Jekyll site"""
            # Create papers data for Jekyll
            categories = self.categorize_papers()

            # Generate YAML data file
            output_path = os.path.join(self.output_dir, 'papers.yml')
            with open(output_path, 'w') as f:
                f.write("# Auto-generated paper data\n")
                f.write(f"last_updated: '{datetime.datetime.now().isoformat()}'\n")
                f.write(f"total_papers: {len(self.papers)}\n")
                f.write("categories:\n")

                for category, papers in categories.items():
                    if papers:
                        f.write(f"  {category}:\n")
                        for paper in papers:
                            title = paper['title'].replace("'", "''")  # Escape quotes
                            year = paper['date_created'].year
                            f.write(f"    - title: '{title}'\n")
                            f.write(f"      arxiv_id: '{paper.get('arxiv_id', '')}'\n")
                            f.write(f"      year: {year}\n")
                            f.write(f"      category: '{paper['category']}'\n")
                            f.write(f"      inspire_url: '{paper['inspire_url']}'\n")

        self.category_keywords = {
            'reviews': {
                'title': ['review', 'survey', 'overview', 'progress', 'status', 'comprehensive', 'systematic'],
                'abstract': ['review', 'survey', 'we review', 'overview', 'comprehensive', 'recent progress',
                             'recent developments', 'current status', 'we summarize', 'we discuss recent'],
                'patterns': [r'review of \w+', r'survey of \w+', r'overview of \w+'],
                'exclusions': []
            },

            'lattice': {
                'title': ['lattice', 'lattice qcd', 'monte carlo', 'numerical simulation', 'discretized',
                          'wilson', 'staggered', 'domain wall', 'overlap'],
                'abstract': ['lattice', 'lattice qcd', 'monte carlo', 'numerical simulation', 'discretization',
                             'wilson fermions', 'staggered fermions', 'lattice gauge theory', 'euclidean',
                             'path integral', 'monte carlo simulation', 'lattice calculation'],
                'patterns': [r'lattice \w+', r'monte carlo \w+', r'numerical \w+'],
                'exclusions': []
            },

            'model_building_sun': {
                'title': ['su(', 'su(2)', 'su(3)', 'su(4)', 'su(5)', 'su(6)', 'su(n)', 'unitary group',
                          'special unitary', 'gauge extension', 'extended gauge', 'new gauge group'],
                'abstract': ['su(', 'su(2)', 'su(3)', 'su(4)', 'su(5)', 'su(6)', 'su(n)', 'unitary group',
                             'special unitary', 'gauge group su', 'sun gauge', 'we propose a model',
                             'we construct a model', 'new gauge theory', 'extended gauge theory',
                             'gauge extension', 'new su(', 'extended su(', 'gauge group extension'],
                'patterns': [r'su\(\d+\)', r'su\(n\)', r'special unitary', r'unitary group',
                             r'we propose.*su\(', r'we construct.*su\(', r'new.*su\(\d+\)',
                             r'extended.*su\(\d+\)', r'gauge.*su\(\d+\).*model'],
                'exclusions': [
                    # Phenomenology exclusions
                    'lhc', 'atlas', 'cms', 'search for', 'constraints on', 'bounds on',
                    'exclusion', 'discovery potential', 'collider', 'experimental',
                    'measurement', 'observation', 'upper limit', 'cross section',
                    'branching ratio', 'decay rate', 'production rate',
                    # Application exclusions
                    'dark matter detection', 'direct detection', 'indirect detection',
                    'relic abundance', 'thermal relic', 'freeze-out', 'cosmological constraint',
                    'reinterpret', 'recast', 'existing searches', 'previous searches'
                ]
            },

            'model_building_non_sun': {
                'title': ['so(', 'sp(', 'usp(', 'orthogonal', 'symplectic', 'exceptional', 'e6', 'e7', 'e8',
                          'f4', 'g2', 'non-abelian gauge', 'abelian gauge extension'],
                'abstract': ['so(', 'sp(', 'usp(', 'orthogonal group', 'symplectic group', 'exceptional group',
                             'e6', 'e7', 'e8', 'f4', 'g2', 'lie group', 'lie algebra',
                             'we propose a model', 'we construct a model', 'new gauge theory',
                             'gauge group so(', 'gauge group sp(', 'exceptional gauge'],
                'patterns': [r'so\(\d+\)', r'sp\(\d+\)', r'usp\(\d+\)', r'exceptional group',
                             r'we propose.*so\(', r'we construct.*sp\(', r'new.*so\(\d+\)',
                             r'gauge.*so\(\d+\).*model', r'gauge.*sp\(\d+\).*model'],
                'exclusions': [
                    # Same phenomenology exclusions
                    'lhc', 'atlas', 'cms', 'search for', 'constraints on', 'bounds on',
                    'exclusion', 'discovery potential', 'collider', 'experimental',
                    'measurement', 'observation', 'upper limit', 'cross section',
                    'branching ratio', 'decay rate', 'production rate',
                    'dark matter detection', 'direct detection', 'indirect detection',
                    'relic abundance', 'thermal relic', 'freeze-out', 'cosmological constraint',
                    'reinterpret', 'recast', 'existing searches', 'previous searches'
                ]
            },

            'model_building_general': {
                'title': ['new model', 'novel model', 'extended model', 'gauge extension',
                          'theoretical framework', 'new theory', 'beyond standard model',
                          'bsm model', 'model construction', 'composite model',
                          'strongly coupled', 'confining', 'chiral symmetry breaking'],
                'abstract': ['we propose a new model', 'we construct a model', 'we introduce a model',
                             'new theoretical framework', 'theoretical construction', 'model building',
                             'gauge theory construction', 'beyond the standard model',
                             'extension of the standard model', 'bsm physics', 'new physics model',
                             'strongly coupled theory', 'confining theory', 'composite sector',
                             'hidden sector model', 'dark sector model', 'secluded sector'],
                'patterns': [r'we propose.*new.*model', r'we construct.*model', r'we introduce.*model',
                             r'new.*beyond.*standard.*model', r'extended.*standard.*model',
                             r'bsm.*model', r'strongly coupled.*sector', r'confining.*sector',
                             r'composite.*dark.*sector', r'hidden.*sector.*model'],
                'exclusions': [
                    # Strong phenomenology exclusions
                    'lhc', 'atlas', 'cms', 'lhcb', 'alice', 'tevatron', 'search for',
                    'constraints on', 'bounds on', 'exclusion', 'discovery potential',
                    'collider phenomenology', 'experimental signature', 'collider signature',
                    'measurement', 'observation', 'upper limit', 'cross section',
                    'branching ratio', 'decay rate', 'production rate', 'final state',
                    # Cosmology/DM phenomenology exclusions
                    'dark matter detection', 'direct detection', 'indirect detection',
                    'relic abundance', 'thermal relic', 'freeze-out', 'cosmological constraint',
                    'cmb', 'big bang nucleosynthesis', 'bbn',
                    # Reinterpretation exclusions
                    'reinterpret', 'recast', 'existing searches', 'previous searches',
                    'existing constraints', 'existing limits', 'current bounds',
                    # Precision/flavor exclusions
                    'flavor constraints', 'precision tests', 'electroweak precision',
                    'rare decays', 'flavor violation', 'fcnc'
                ]
            },

            'dark_matter_pion': {
                'title': ['dark pion', 'dark pions', 'pseudoscalar', 'chiral', 'goldstone', 'nambu-goldstone'],
                'abstract': ['dark pion', 'dark pions', 'pseudoscalar mesons', 'chiral symmetry', 'goldstone boson',
                             'nambu-goldstone', 'chiral perturbation', 'pseudoscalar dark'],
                'patterns': [r'dark pion\w*', r'pseudoscalar \w+', r'goldstone \w+'],
                'exclusions': []
            },

            'dark_matter_baryon': {
                'title': ['dark baryon', 'dark baryons', 'dark nucleon', 'dark nucleons', 'composite fermion'],
                'abstract': ['dark baryon', 'dark baryons', 'dark nucleon', 'dark nucleons', 'composite fermion',
                             'baryon dark matter', 'dark nuclear', 'fermionic composite'],
                'patterns': [r'dark baryon\w*', r'dark nucleon\w*', r'composite fermion\w*'],
                'exclusions': []
            },

            'dark_matter_other': {
                'title': ['dark matter', 'wimp', 'wimps', 'relic', 'relics', 'cosmology', 'cosmological',
                          'thermal', 'freeze', 'abundance', 'dm', 'dark meson', 'dark mesons'],
                'abstract': ['dark matter', 'relic abundance', 'thermal relic', 'freeze-out', 'cosmological',
                             'dm candidate', 'dark matter candidate', 'wimp', 'thermal production',
                             'cosmological constraints', 'relic density', 'dark meson', 'dark mesons'],
                'patterns': [r'dark matter \w+', r'dm \w+', r'relic \w+', r'dark meson\w*'],
                'exclusions': []
            },

            'experimental': {
                'title': ['atlas', 'cms', 'lhcb', 'alice', 'search', 'searches', 'measurement', 'measurements',
                          'observation', 'evidence', 'discovery', 'detector', 'collider', 'lhc', 'tevatron'],
                'abstract': ['we search', 'search for', 'measurement of', 'observed', 'no evidence',
                             'upper limit', 'cross section', 'branching ratio', 'detector', 'collision',
                             'data collected', 'fb-1', 'tev', 'gev', 'analysis'],
                'patterns': [r'search for \w+', r'measurement of \w+', r'evidence for \w+'],
                'exclusions': []
            },

            'phenomenology': {  # NEW CATEGORY
                'title': ['phenomenology', 'phenomenological', 'collider physics', 'lhc physics',
                          'signature', 'signatures', 'production', 'decay', 'constraints'],
                'abstract': ['phenomenology', 'phenomenological study', 'collider phenomenology',
                             'experimental signature', 'production mechanism', 'decay channel',
                             'final state', 'signal', 'background', 'discovery potential',
                             'constraints on', 'bounds on', 'exclusion limits'],
                'patterns': [r'phenomenology of \w+', r'signature of \w+', r'production of \w+',
                             r'constraints on \w+', r'bounds on \w+'],
                'exclusions': [
                    # Exclude pure model building
                    'we propose a new model', 'we construct a model', 'we introduce a model',
                    'model construction', 'theoretical construction', 'gauge extension'
                ]
            },

            'machine_learning': {
                'title': ['machine learning', 'ml', 'neural', 'deep learning', 'ai', 'artificial intelligence',
                          'algorithm', 'classification', 'regression', 'clustering', 'network'],
                'abstract': ['machine learning', 'neural network', 'deep learning', 'artificial intelligence',
                             'algorithm', 'training', 'classification', 'regression', 'feature',
                             'supervised', 'unsupervised', 'convolutional', 'transformer'],
                'patterns': [r'machine learning \w+', r'neural \w+', r'deep \w+'],
                'exclusions': []
            },

            'new_signatures': {
                'title': ['new signature', 'novel signature', 'distinctive signature', 'unique signature',
                          'new signal', 'novel signal', 'smoking gun'],
                'abstract': ['new signature', 'novel signature', 'distinctive signature',
                             'unique signature', 'smoking gun', 'characteristic signature',
                             'we propose a new signature', 'novel experimental signature'],
                'patterns': [r'new.*signature', r'novel.*signature', r'distinctive.*signature',
                             r'unique.*signature', r'smoking gun'],
                'exclusions': []
            },

            'reinterpretation': {
                'title': ['reinterpret', 'reinterpretation', 'recast', 'recasting', 'constraints', 'limit',
                          'limits', 'bound', 'bounds', 'exclusion'],
                'abstract': ['reinterpret', 'reinterpretation', 'recast', 'existing searches', 'constraints',
                             'exclusion limits', 'bounds', 'we derive', 'we obtain constraints',
                             'previous searches', 'existing limits'],
                'patterns': [r'reinterpret\w* \w+', r'recast\w* \w+', r'constraints on \w+'],
                'exclusions': []
            },

            'lepton_colliders': {
                'title': ['lepton collider', 'electron collider', 'muon collider', 'e+e-', 'future collider',
                          'ilc', 'clic', 'fcc-ee', 'cepc', '$e^+e^-$'],
                'abstract': ['lepton collider', 'electron collider', 'muon collider', 'e+e- collider',
                             'future collider', 'ilc', 'clic', 'fcc-ee', 'cepc', 'linear collider'],
                'patterns': [r'e\+e\- \w+', r'lepton collider \w+', r'future collider \w+'],
                'exclusions': []
            }
        }
        
        # Collaboration patterns for experimental classification
        self.experimental_collaborations = [
            'ATLAS', 'CMS', 'LHCb', 'ALICE', 'H1', 'ZEUS', 'D0', 'CDF', 'Belle', 'Belle-II', 'BESIII',
            'BaBar', 'LHCb', 'COMPASS', 'KLOE', 'DELPHI', 'L3', 'ALEPH', 'OPAL'
        ]

    def build_search_query(self, start_year=None):
        """Build comprehensive search query for dark showers (fixed version)"""
        if start_year is None:
            start_year = self.starting_date.year
            
        # Main dark showers keywords with proper boolean logic
        main_keywords = ' OR '.join([f'"{keyword}"' for keyword in self.keywords])
        
        # Date constraint
        date_constraint = f"de >= {start_year}"
        
        # Combine: (main keywords) AND (date)
        query = f"({main_keywords}) AND {date_constraint}"
        
        return query

    def search_papers(self):
        """Search for papers using the Inspire API (improved version)"""
        print(f"Looking at arXiv categories: {self.categories}")
        print(f"Scanning papers with keywords: {self.keywords}")
        
        all_papers = []
        
        # Build base query
        base_query = self.build_search_query()
        
        for category in self.categories:
            print(f"\nSearching category: {category}")
            
            # Add category constraint
            query = f"primarch {category} AND {base_query}"
            
            # URL encode the query properly
            encoded_query = requests.utils.quote(query)
            
            # Build API URL
            api_url = f"https://inspirehep.net/api/literature?sort=mostrecent&size=1000&q={encoded_query}"
            
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                total_hits = data['hits']['total']
                if total_hits > 1000:
                    print(f"WARNING: Found more than 1000 hits for {category}! Only first 1000 will be processed.")
                
                print(f"Found {total_hits} papers in {category}")
                
                for hit in data['hits']['hits']:
                    paper_info = self.extract_paper_info(hit, category)
                    if paper_info:
                        all_papers.append(paper_info)
                        
            except requests.RequestException as e:
                print(f"Error searching {category}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error in {category}: {e}")
                continue
        
        # Improved deduplication logic (like Script 1)
        seen_ids = set()
        self.papers = []
        
        for paper in all_papers:
            paper_id = paper.get('arxiv_id') or paper.get('inspire_id')
            if paper_id and paper_id not in seen_ids:
                self.papers.append(paper)
                seen_ids.add(paper_id)
        
        # Sort by date (newest first)
        self.papers.sort(key=lambda x: x['date_created'], reverse=True)
        
        print(f"\nTotal unique papers found: {len(self.papers)}")
        return self.papers

    def extract_paper_info(self, hit, category):
        """Extract relevant information from a paper hit (enhanced version)"""
        try:
            metadata = hit['metadata']
            
            # Extract basic info
            title = metadata['titles'][0]['title']
            date_created = datetime.datetime.fromisoformat(hit['created']).date()
            
            # Extract arXiv ID
            arxiv_id = None
            if 'arxiv_eprints' in metadata and metadata['arxiv_eprints']:
                arxiv_id = metadata['arxiv_eprints'][0]['value']
            
            # Extract Inspire cite key
            cite_key = None
            if 'texkeys' in metadata and metadata['texkeys']:
                cite_key = metadata['texkeys'][0]
            
            # Extract abstract (NEW)
            abstract = ""
            if 'abstracts' in metadata and metadata['abstracts']:
                abstract = metadata['abstracts'][0].get('value', '')
            
            # Extract authors (ENHANCED)
            authors = []
            if 'authors' in metadata:
                for author in metadata['authors']:
                    if 'full_name' in author:
                        authors.append(author['full_name'])
            
            # Get Inspire ID for fallback deduplication
            inspire_id = hit['id']
                
            return {
                'title': title,
                'arxiv_id': arxiv_id,
                'inspire_id': inspire_id,
                'cite_key': cite_key,
                'date_created': date_created,
                'category': category,
                'inspire_url': f"https://inspirehep.net/literature/{hit['id']}",
                'abstract': abstract,
                'authors': authors
            }
            
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error extracting paper info: {e}")
            return None

    def get_bibtex(self, arxiv_id):
        """Get BibTeX citation for a given arXiv ID"""
        url = f"https://inspirehep.net/api/literature?q=arxiv:{arxiv_id}&format=bibtex"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error getting BibTeX for {arxiv_id}: {e}")
            return None

    def replace_collaboration_author(self, bib_entry):
        """Replace collaboration author with collaboration name"""
        collab_field = re.search(r'collaboration\s+=.*\n\s+', bib_entry)
        
        if collab_field is None:
            return bib_entry
        
        collab_field_text = collab_field.group(0)
        
        # Find matching collaboration
        collab_name = None
        for exp in self.collab_names.keys():
            if exp in collab_field_text:
                collab_name = self.collab_names[exp]
                break
        
        if collab_name is not None:
            author_match = re.search(r'author\s+=(.*)', bib_entry)
            if author_match:
                author = author_match.group(1)
                bib_entry = bib_entry.replace(author, f' "{{{collab_name}}}",')
                bib_entry = bib_entry.replace(collab_field_text, '')
        
        return bib_entry

    def generate_bibtex_file(self, filename="darkshowers_bibliography.bib", replace_collab=True):
        """Generate a BibTeX file for all found papers"""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            f.write(f"% Dark Showers Bibliography\n")
            f.write(f"% Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"% Search date range: {self.starting_date} to present\n")
            f.write(f"% Keywords: {', '.join(self.keywords)}\n")
            f.write(f"% Categories: {', '.join(self.categories)}\n\n")
            
            for paper in self.papers:
                if paper.get('arxiv_id'):  # Only generate BibTeX for papers with arXiv IDs
                    bibtex = self.get_bibtex(paper['arxiv_id'])
                    if bibtex:
                        if replace_collab:
                            bibtex = self.replace_collaboration_author(bibtex)
                        
                        f.write(f"% {paper['date_created'].strftime('%B %d, %Y')} - {paper['category']}\n")
                        f.write(f"% {paper['title']}\n")
                        f.write(f"% arXiv:{paper['arxiv_id']}\n")
                        f.write(f"{bibtex}\n")
        
        print(f"Bibliography written to {output_path}")
        return output_path

    def get_paper_text(self, paper):
        """Extract searchable text from paper metadata"""
        # Get title
        title = paper.get('title', '').lower()
        
        # Get abstract
        abstract = paper.get('abstract', '').lower()
        
        # Get author information
        authors = paper.get('authors', [])
        author_text = ' '.join(authors).lower() if authors else ''
        
        return {
            'title': title,
            'abstract': abstract,
            'authors': author_text,
            'combined': f"{title} {abstract} {author_text}"
        }

    def calculate_category_score(self, paper, category):
        """Calculate relevance score for a paper in a specific category with exclusion logic"""
        if category not in self.category_keywords:
            return 0.0

        text_data = self.get_paper_text(paper)
        keywords = self.category_keywords[category]

        # First check for exclusions - if found, return 0
        exclusions = keywords.get('exclusions', [])
        for exclusion in exclusions:
            if exclusion in text_data['combined']:
                return 0.0

        score = 0.0

        # Title keywords (higher weight)
        title_matches = sum(1 for keyword in keywords.get('title', [])
                            if keyword in text_data['title'])
        score += title_matches * 3.0

        # Abstract keywords (medium weight)
        abstract_matches = sum(1 for keyword in keywords.get('abstract', [])
                               if keyword in text_data['abstract'])
        score += abstract_matches * 2.0

        # Pattern matching (highest weight for specific patterns)
        pattern_matches = 0
        for pattern in keywords.get('patterns', []):
            if re.search(pattern, text_data['combined']):
                pattern_matches += 1
        score += pattern_matches * 4.0

        # Special handling for model building categories
        if category.startswith('model_building'):
            # Bonus for theory papers
            if paper.get('category') in ['hep-th', 'hep-ph']:
                score += 2.0

            # Extra bonus for strong model-building indicators
            strong_indicators = [
                'we propose a new model', 'we construct a model', 'we introduce a model',
                'model construction', 'theoretical construction', 'new gauge theory',
                'gauge extension', 'extended gauge theory'
            ]
            strong_matches = sum(1 for indicator in strong_indicators
                                 if indicator in text_data['combined'])
            score += strong_matches * 5.0

            # Penalty for experimental keywords (even if not excluded)
            experimental_indicators = [
                'lhc', 'collider', 'experimental', 'measurement', 'search',
                'constraint', 'bound', 'limit', 'exclusion'
            ]
            experimental_matches = sum(1 for indicator in experimental_indicators
                                       if indicator in text_data['combined'])
            score -= experimental_matches * 1.0

        # Special handling for experimental papers
        elif category == 'experimental':
            # HARD REQUIREMENT: Only hep-ex papers can be experimental
            if paper.get('category') != 'hep-ex':
                return 0.0

            # Now proceed with normal scoring for hep-ex papers
            # Check for collaboration names in authors
            collab_bonus = sum(2.0 for collab in self.experimental_collaborations
                               if collab.lower() in text_data['authors'])
            score += collab_bonus

            # Extra bonus for being hep-ex (since it's required)
            score += 5.0


        # Special handling for phenomenology category
        elif category == 'phenomenology':
            # Bonus for phenomenology papers
            if paper.get('category') in ['hep-ph', 'hep-ex']:
                score += 3.0

            # Strong phenomenology indicators
            pheno_indicators = [
                'phenomenological study', 'collider phenomenology', 'experimental signature',
                'production mechanism', 'decay channel', 'discovery potential'
            ]
            pheno_matches = sum(1 for indicator in pheno_indicators
                                if indicator in text_data['combined'])
            score += pheno_matches * 4.0

        # Special handling for lattice papers
        elif category == 'lattice':
            if paper.get('category') == 'hep-lat':
                score += 5.0

        return max(0.0, score)  # Ensure non-negative score

    def categorize_papers(self, min_score=1.0, max_categories_per_paper=3):
        """Enhanced categorization with multi-category assignment and scoring"""
        categories = {
            'reviews': [],
            'lattice': [],
            'model_building_sun': [],
            'model_building_non_sun': [],
            'model_building_general': [],
            'dark_matter_pion': [],
            'dark_matter_baryon': [],
            'dark_matter_other': [],
            'experimental': [],
            'machine_learning': [],
            'new_signatures': [],
            'reinterpretation': [],
            'low_energy': [],
            'phenomenology': [],
            'lepton_colliders': []
        }
        
        # Store paper-category scores for analysis
        paper_scores = {}
        uncategorized_papers = []
        
        for paper in self.papers:
            paper_id = paper.get('arxiv_id', paper.get('cite_key', 'unknown'))
            scores = {}
            
            # Calculate scores for each category
            for category in categories.keys():
                score = self.calculate_category_score(paper, category)
                if score >= min_score:
                    scores[category] = score
            
            # Store scores for analysis
            paper_scores[paper_id] = scores
            
            if scores:
                # Sort categories by score and take top ones
                sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                top_categories = sorted_categories[:max_categories_per_paper]
                
                # Add paper to top scoring categories
                for category, score in top_categories:
                    categories[category].append(paper)
            else:
                uncategorized_papers.append(paper)
        
        # Print categorization summary
        print(f"\nCategorization Summary:")
        print(f"Total papers: {len(self.papers)}")
        print(f"Uncategorized papers: {len(uncategorized_papers)}")
        
        for category, papers in categories.items():
            if papers:
                print(f"{category}: {len(papers)} papers")
        
        return categories

    def generate_readme(self, filename="README.md"):
        """Generate a README file with improved categorization"""
        output_path = os.path.join(self.output_dir, filename)
        categories = self.categorize_papers()
        
        with open(output_path, 'w') as f:
            f.write("# **A Living Review of Dark Showers**\n\n")
            f.write("*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. ")
            f.write("They connect different areas of theoretical physics with each other and arise from well motivated ")
            f.write("theoretical scenarios. Below is a list of papers concerning dark showers.*\n\n")
            
            f.write("The purpose of this note is to collect references for dark showers. Papers are automatically ")
            f.write("categorized using keyword matching on titles and abstracts. Papers may appear in multiple ")
            f.write("categories if relevant.\n\n")
            
            f.write(f"**Last updated:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**Search period:** {self.starting_date} to present\n")
            f.write(f"**Total papers found:** {len(self.papers)}\n")
            f.write(f"**Search categories:** {', '.join(self.categories)}\n\n")
            
            # Group related categories for better presentation
            category_groups = {
                'General': ['reviews'],
                'Lattice QCD': ['lattice'],
                'Model Building': ['model_building_sun', 'model_building_non_sun', 'model_building_general'],
                'Dark Matter': ['dark_matter_pion', 'dark_matter_baryon', 'dark_matter_other'],
                'Experimental & Phenomenology': ['experimental', 'new_signatures', 'reinterpretation','phenomenology'],
                'Specialized': ['machine_learning', 'low_energy', 'lepton_colliders']
            }
            
            # Write categorized papers by groups
            for group_name, category_list in category_groups.items():
                # Check if any category in this group has papers
                group_has_papers = any(categories.get(cat, []) for cat in category_list)
                if not group_has_papers:
                    continue
                    
                f.write(f"# {group_name}\n\n")
                
                for category_key in category_list:
                    papers = categories.get(category_key, [])
                    if not papers:
                        continue
                    
                    # Format category title nicely
                    if category_key.startswith('model_building_'):
                        if 'sun' in category_key:
                            category_title = "Model Building - SU(N) Gauge Groups"
                        elif 'non_sun' in category_key:
                            category_title = "Model Building - Non-SU(N) Gauge Groups"
                        else:
                            category_title = "Model Building - General"
                    elif category_key.startswith('dark_matter_'):
                        subcategory = category_key.split('_')[-1].title()
                        category_title = f"Dark Matter - {subcategory}"
                    else:
                        category_title = category_key.replace('_', ' ').title()
                    
                    f.write(f"## {category_title} ({len(papers)} papers)\n\n")
                    
                    #for paper in papers:
                    #    f.write(f"* **{paper['title']}**\n")
                    #    if paper.get('arxiv_id'):
                    #        f.write(f"  * [arXiv:{paper['arxiv_id']}](https://arxiv.org/abs/{paper['arxiv_id']}) | ")
                    #    f.write(f"[Inspire]({paper['inspire_url']}) | {paper['date_created']} | {paper['category']}\n\n")
                    for paper in papers:
                        title = paper['title']
                        year = paper['date_created'].year
                        category = paper['category']

                        # Build the entry line
                        entry = f"* **{title}** ("

                        if paper.get('arxiv_id'):
                            entry += f"[arXiv:{paper['arxiv_id']}](https://arxiv.org/abs/{paper['arxiv_id']})"
                        else:
                            entry += f"[Inspire]({paper['inspire_url']})"

                        entry += f"), {year}, [{category}]\n\n"

                        f.write(entry)
                
                f.write("\n")
        
        print(f"README written to {output_path}")
        return output_path

    def save_paper_data(self, filename="papers_data.json"):
        """Save raw paper data as JSON for further processing"""
        output_path = os.path.join(self.output_dir, filename)
        
        # Convert dates to strings for JSON serialization
        papers_json = []
        for paper in self.papers:
            paper_copy = paper.copy()
            paper_copy['date_created'] = paper['date_created'].isoformat()
            papers_json.append(paper_copy)
        
        with open(output_path, 'w') as f:
            json.dump({
                'search_parameters': {
                    'starting_date': self.starting_date.isoformat(),
                    'keywords': self.keywords,
                    'categories': self.categories,
                    'generated_on': datetime.datetime.now().isoformat()
                },
                'papers': papers_json
            }, f, indent=2)
        
        print(f"Raw data saved to {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Search Inspire HEP and generate bibliography")
    parser.add_argument("-d", "--date", type=str, help="Starting date (YYYY-MM-DD)", 
                       default=None)
    parser.add_argument("-o", "--output", type=str, help="Output directory", 
                       default="results")
    parser.add_argument("--bib-file", type=str, help="Bibliography filename", 
                       default="darkshowers_bibliography.bib")
    parser.add_argument("--readme-file", type=str, help="README filename", 
                       default="README.md")
    parser.add_argument("--no-collab", action="store_true", 
                       help="Don't replace collaboration authors")
    
    args = parser.parse_args()
    
    # Parse starting date
    starting_date = None
    if args.date:
        try:
            starting_date = date.fromisoformat(args.date)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return
    
    # Create generator
    generator = InspireBibGenerator(starting_date=starting_date, output_dir=args.output)
    
    # Search for papers
    print("Searching for papers...")
    papers = generator.search_papers()
    
    if not papers:
        print("No papers found!")
        return
    
    # Generate outputs
    print("\nGenerating bibliography...")
    generator.generate_bibtex_file(args.bib_file, replace_collab=not args.no_collab)
    
    print("Generating README...")
    generator.generate_readme(args.readme_file)
    
    print("Saving raw data...")
    generator.save_paper_data()
    
    print(f"\nAll files generated in '{args.output}' directory")


if __name__ == "__main__":
    main()