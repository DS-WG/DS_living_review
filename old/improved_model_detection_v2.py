# Replace the category_keywords section in your InspireBibGenerator class with this improved version:

# Also replace the calculate_category_score method with this improved version:


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
                 'ilc', 'clic', 'fcc-ee', 'cepc','$e^+e^-$'],
        'abstract': ['lepton collider', 'electron collider', 'muon collider', 'e+e- collider',
                   'future collider', 'ilc', 'clic', 'fcc-ee', 'cepc', 'linear collider'],
        'patterns': [r'e\+e\- \w+', r'lepton collider \w+', r'future collider \w+'],
        'exclusions': []
    }
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
        # Check for collaboration names in authors
        collab_bonus = sum(2.0 for collab in self.experimental_collaborations 
                         if collab.lower() in text_data['authors'])
        score += collab_bonus
        
        # Check arXiv category
        if paper.get('category') == 'hep-ex':
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