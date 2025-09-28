"""
Script to analyze why a paper was included in the dark showers bibliography
Takes arXiv IDs as input and shows the matching criteria
"""

import json
import os
import re
import requests
import datetime
from collections import defaultdict
import argparse


class PaperAnalyzer:
    def __init__(self, results_dir="results"):
        self.results_dir = results_dir
        self.papers_data = None
        
        # Load the same keywords and categories as the original script
        self.keywords = [
            'dark showers', 'dark shower', 'hidden valley', 'hidden valleys',
            'dark pion', 'dark pions', 'dark baryons', 'SUEP','soft-bombs',
            'soft bombs','soft-bomb','soft bomb',
            'dark hadron', 'dark hadrons', 'dark QCD', 'confining dark sector',
            'semi-visible jets', 'emerging jets', 'soft unclustered energy',
            'dark mesons', 'composite dark matter', 'dark confinement'
        ]
        
        # Same category keywords as original script
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
                    'lhc', 'atlas', 'cms', 'search for', 'constraints on', 'bounds on',
                    'exclusion', 'discovery potential', 'collider', 'experimental',
                    'measurement', 'observation', 'upper limit', 'cross section',
                    'branching ratio', 'decay rate', 'production rate',
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
                    'lhc', 'atlas', 'cms', 'lhcb', 'alice', 'tevatron', 'search for',
                    'constraints on', 'bounds on', 'exclusion', 'discovery potential',
                    'collider phenomenology', 'experimental signature', 'collider signature',
                    'measurement', 'observation', 'upper limit', 'cross section',
                    'branching ratio', 'decay rate', 'production rate', 'final state',
                    'dark matter detection', 'direct detection', 'indirect detection',
                    'relic abundance', 'thermal relic', 'freeze-out', 'cosmological constraint',
                    'cmb', 'big bang nucleosynthesis', 'bbn',
                    'reinterpret', 'recast', 'existing searches', 'previous searches',
                    'existing constraints', 'existing limits', 'current bounds',
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

            'phenomenology': {
                'title': ['phenomenology', 'phenomenological', 'collider physics', 'lhc physics',
                          'signature', 'signatures', 'production', 'decay', 'constraints'],
                'abstract': ['phenomenology', 'phenomenological study', 'collider phenomenology',
                             'experimental signature', 'production mechanism', 'decay channel',
                             'final state', 'signal', 'background', 'discovery potential',
                             'constraints on', 'bounds on', 'exclusion limits'],
                'patterns': [r'phenomenology of \w+', r'signature of \w+', r'production of \w+',
                             r'constraints on \w+', r'bounds on \w+'],
                'exclusions': [
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

        # Experimental collaborations for scoring
        self.experimental_collaborations = [
            'ATLAS', 'CMS', 'LHCb', 'ALICE', 'H1', 'ZEUS', 'D0', 'CDF', 'Belle', 'Belle-II', 'BESIII',
            'BaBar', 'LHCb', 'COMPASS', 'KLOE', 'DELPHI', 'L3', 'ALEPH', 'OPAL'
        ]

    def load_papers_data(self):
        """Load the papers data from JSON file"""
        json_path = os.path.join(self.results_dir, "papers_data.json")
        if not os.path.exists(json_path):
            print(f"Papers data file not found at {json_path}")
            print("Make sure you've run the main script first to generate the data.")
            return False
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.papers_data = data['papers']
        
        print(f"Loaded {len(self.papers_data)} papers from {json_path}")
        return True

    def get_paper_by_arxiv_id(self, arxiv_id):
        """Find paper by arXiv ID"""
        if not self.papers_data:
            return None
        
        for paper in self.papers_data:
            if paper.get('arxiv_id') == arxiv_id:
                return paper
        return None

    def get_paper_text(self, paper):
        """Extract searchable text from paper metadata (same as original)"""
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        authors = paper.get('authors', [])
        author_text = ' '.join(authors).lower() if authors else ''
        
        return {
            'title': title,
            'abstract': abstract,
            'authors': author_text,
            'combined': f"{title} {abstract} {author_text}"
        }

    def check_initial_keywords(self, paper):
        """Check which dark shower keywords matched"""
        text_data = self.get_paper_text(paper)
        combined_text = text_data['combined']
        
        matched_keywords = []
        for keyword in self.keywords:
            if keyword.lower() in combined_text:
                matched_keywords.append(keyword)
        
        return matched_keywords

    def analyze_category_matching(self, paper, category):
        """Analyze why a paper matches (or doesn't match) a specific category"""
        if category not in self.category_keywords:
            return None

        text_data = self.get_paper_text(paper)
        keywords = self.category_keywords[category]
        
        analysis = {
            'category': category,
            'total_score': 0.0,
            'exclusions_triggered': [],
            'title_matches': [],
            'abstract_matches': [],
            'pattern_matches': [],
            'special_bonuses': [],
            'special_penalties': []
        }

        # Check exclusions first
        exclusions = keywords.get('exclusions', [])
        for exclusion in exclusions:
            if exclusion in text_data['combined']:
                analysis['exclusions_triggered'].append(exclusion)
        
        if analysis['exclusions_triggered']:
            analysis['total_score'] = 0.0
            analysis['excluded'] = True
            return analysis
        
        analysis['excluded'] = False

        # Title matches (weight: 3.0)
        for keyword in keywords.get('title', []):
            if keyword in text_data['title']:
                analysis['title_matches'].append(keyword)
                analysis['total_score'] += 3.0

        # Abstract matches (weight: 2.0)
        for keyword in keywords.get('abstract', []):
            if keyword in text_data['abstract']:
                analysis['abstract_matches'].append(keyword)
                analysis['total_score'] += 2.0

        # Pattern matches (weight: 4.0)
        for pattern in keywords.get('patterns', []):
            matches = re.findall(pattern, text_data['combined'])
            if matches:
                analysis['pattern_matches'].extend([(pattern, match) for match in matches])
                analysis['total_score'] += len(matches) * 4.0

        # Special handling for different categories
        if category.startswith('model_building'):
            if paper.get('category') in ['hep-th', 'hep-ph']:
                analysis['special_bonuses'].append(('theory_paper_bonus', 2.0))
                analysis['total_score'] += 2.0

            strong_indicators = [
                'we propose a new model', 'we construct a model', 'we introduce a model',
                'model construction', 'theoretical construction', 'new gauge theory',
                'gauge extension', 'extended gauge theory'
            ]
            strong_matches = [ind for ind in strong_indicators if ind in text_data['combined']]
            if strong_matches:
                bonus = len(strong_matches) * 5.0
                analysis['special_bonuses'].append(('strong_model_building', bonus, strong_matches))
                analysis['total_score'] += bonus

            experimental_indicators = [
                'lhc', 'collider', 'experimental', 'measurement', 'search',
                'constraint', 'bound', 'limit', 'exclusion'
            ]
            exp_matches = [ind for ind in experimental_indicators if ind in text_data['combined']]
            if exp_matches:
                penalty = len(exp_matches) * 1.0
                analysis['special_penalties'].append(('experimental_indicators', penalty, exp_matches))
                analysis['total_score'] -= penalty

        elif category == 'experimental':
            if paper.get('category') != 'hep-ex':
                analysis['exclusions_triggered'].append('not_hep_ex_category')
                analysis['total_score'] = 0.0
                analysis['excluded'] = True
                return analysis

            collab_matches = [collab for collab in self.experimental_collaborations
                            if collab.lower() in text_data['authors']]
            if collab_matches:
                bonus = len(collab_matches) * 2.0
                analysis['special_bonuses'].append(('collaboration_bonus', bonus, collab_matches))
                analysis['total_score'] += bonus

            analysis['special_bonuses'].append(('hep_ex_bonus', 5.0))
            analysis['total_score'] += 5.0

        elif category == 'phenomenology':
            if paper.get('category') in ['hep-ph', 'hep-ex']:
                analysis['special_bonuses'].append(('pheno_category_bonus', 3.0))
                analysis['total_score'] += 3.0

            pheno_indicators = [
                'phenomenological study', 'collider phenomenology', 'experimental signature',
                'production mechanism', 'decay channel', 'discovery potential'
            ]
            pheno_matches = [ind for ind in pheno_indicators if ind in text_data['combined']]
            if pheno_matches:
                bonus = len(pheno_matches) * 4.0
                analysis['special_bonuses'].append(('strong_phenomenology', bonus, pheno_matches))
                analysis['total_score'] += bonus

        elif category == 'lattice':
            if paper.get('category') == 'hep-lat':
                analysis['special_bonuses'].append(('hep_lat_bonus', 5.0))
                analysis['total_score'] += 5.0

        # Ensure non-negative score
        analysis['total_score'] = max(0.0, analysis['total_score'])
        
        return analysis

    def analyze_paper(self, arxiv_id, min_score=1.0):
        """Complete analysis of why a paper was included"""
        if not self.papers_data and not self.load_papers_data():
            return None

        paper = self.get_paper_by_arxiv_id(arxiv_id)
        if not paper:
            print(f"Paper with arXiv ID '{arxiv_id}' not found in the dataset.")
            return None

        print(f"\n{'='*80}")
        print(f"ANALYSIS FOR arXiv:{arxiv_id}")
        print(f"{'='*80}")
        print(f"Title: {paper['title']}")
        print(f"Date: {paper['date_created']}")
        print(f"Category: {paper['category']}")
        print(f"Abstract: {paper.get('abstract', 'N/A')[:200]}...")
        
        print(f"\n{'Initial Keyword Matching:':-<50}")
        matched_keywords = self.check_initial_keywords(paper)
        if matched_keywords:
            print(f"✓ Matched {len(matched_keywords)} dark shower keywords:")
            for kw in matched_keywords:
                print(f"  - '{kw}'")
        else:
            print("✗ No dark shower keywords found (this shouldn't happen!)")

        print(f"\n{'Category Analysis:':-<50}")
        category_analyses = {}
        qualifying_categories = []

        for category in self.category_keywords.keys():
            analysis = self.analyze_category_matching(paper, category)
            category_analyses[category] = analysis
            
            if analysis['total_score'] >= min_score:
                qualifying_categories.append((category, analysis['total_score']))

        # Sort by score
        qualifying_categories.sort(key=lambda x: x[1], reverse=True)

        if qualifying_categories:
            print(f"✓ Paper qualifies for {len(qualifying_categories)} categories:")
            for category, score in qualifying_categories:
                print(f"  - {category}: {score:.1f} points")
        else:
            print("✗ Paper does not qualify for any categories (score < 1.0)")

        print(f"\n{'Detailed Category Breakdown:':-<50}")
        for category, score in qualifying_categories:
            analysis = category_analyses[category]
            print(f"\n{category.upper()} (Score: {score:.1f})")
            
            if analysis['excluded']:
                print("  ✗ EXCLUDED due to exclusion rules:")
                for excl in analysis['exclusions_triggered']:
                    print(f"    - {excl}")
                continue

            if analysis['title_matches']:
                print(f"  Title matches (+3.0 each): {analysis['title_matches']}")
            
            if analysis['abstract_matches']:
                print(f"  Abstract matches (+2.0 each): {analysis['abstract_matches']}")
            
            if analysis['pattern_matches']:
                print(f"  Pattern matches (+4.0 each):")
                for pattern, match in analysis['pattern_matches']:
                    print(f"    - Pattern '{pattern}' → '{match}'")
            
            if analysis['special_bonuses']:
                print(f"  Special bonuses:")
                for bonus in analysis['special_bonuses']:
                    if len(bonus) == 2:
                        bonus_type, points = bonus
                        print(f"    - {bonus_type}: +{points:.1f}")
                    else:
                        bonus_type, points, matches = bonus
                        print(f"    - {bonus_type}: +{points:.1f} (matches: {matches})")
            
            if analysis['special_penalties']:
                print(f"  Special penalties:")
                for penalty in analysis['special_penalties']:
                    penalty_type, points, matches = penalty
                    print(f"    - {penalty_type}: -{points:.1f} (matches: {matches})")

        # Show non-qualifying categories with scores > 0
        print(f"\n{'Non-qualifying Categories (score > 0):':-<50}")
        non_qualifying = [(cat, analysis['total_score']) for cat, analysis in category_analyses.items()
                         if 0 < analysis['total_score'] < min_score]
        non_qualifying.sort(key=lambda x: x[1], reverse=True)
        
        if non_qualifying:
            for category, score in non_qualifying:
                print(f"  - {category}: {score:.1f} points (below threshold)")
        else:
            print("  None")

        return {
            'paper': paper,
            'matched_keywords': matched_keywords,
            'category_analyses': category_analyses,
            'qualifying_categories': qualifying_categories
        }

    def batch_analyze(self, arxiv_ids, min_score=1.0):
        """Analyze multiple papers"""
        if not self.papers_data and not self.load_papers_data():
            return None

        results = {}
        for arxiv_id in arxiv_ids:
            print(f"\nAnalyzing {arxiv_id}...")
            result = self.analyze_paper(arxiv_id, min_score)
            if result:
                results[arxiv_id] = result
            else:
                print(f"Could not analyze {arxiv_id}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Analyze why papers were included in dark showers bibliography")
    parser.add_argument("arxiv_ids", nargs="+", help="arXiv IDs to analyze (e.g., 2301.12345)")
    parser.add_argument("-d", "--data-dir", default="results", help="Directory containing papers_data.json")
    parser.add_argument("-s", "--min-score", type=float, default=1.0, help="Minimum score threshold")
    parser.add_argument("-o", "--output", help="Save analysis to file")
    
    args = parser.parse_args()

    analyzer = PaperAnalyzer(results_dir=args.data_dir)
    
    if len(args.arxiv_ids) == 1:
        result = analyzer.analyze_paper(args.arxiv_ids[0], args.min_score)
    else:
        result = analyzer.batch_analyze(args.arxiv_ids, args.min_score)

    if args.output and result:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nAnalysis saved to {args.output}")


if __name__ == "__main__":
    main()