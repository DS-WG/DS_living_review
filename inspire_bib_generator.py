"""
Combined script to search Inspire HEP for papers and generate bibliography files
"""

import json
import os
import re
import datetime
from datetime import date
import requests
import argparse


class InspireBibGenerator:
    def __init__(self, starting_date=None, output_dir="results"):
        self.starting_date = starting_date or date.today().replace(year=date.today().year - 1)
        self.output_dir = output_dir
        self.categories = ['hep-ph', 'hep-ex']
        self.keywords = ['dark showers', 'Hidden valley', 'dark pion', 'strongly-interacting']
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

    def search_papers(self):
        """Search for papers using the Inspire API"""
        print(f"Looking at arXiv categories: {self.categories}")
        print(f"Scanning papers with keywords: {self.keywords}")
        
        # Format keywords for URL
        keyword_str = f'("{self.keywords}")'.replace("', '", '"%20OR%20"').replace("['", '').replace("']", "")
        keyword_str = keyword_str.replace(" ", "%20")
        
        all_papers = []
        
        for category in self.categories:
            print(f"\nSearching category: {category}")
            
            # Build the Inspire API query
            query_url = (f'https://inspirehep.net/api/literature?sort=leastrecent&size=1000&'
                        f'q=primarch%20{category}%20AND%20{keyword_str}%20AND%20de%20>=%20{self.starting_date}')
            
            try:
                response = requests.get(query_url)
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
        
        # Remove duplicates based on arXiv ID
        seen_arxiv = set()
        self.papers = []
        for paper in all_papers:
            if paper['arxiv_id'] not in seen_arxiv:
                self.papers.append(paper)
                seen_arxiv.add(paper['arxiv_id'])
        
        # Sort by date (newest first)
        self.papers.sort(key=lambda x: x['date_created'], reverse=True)
        
        print(f"\nTotal unique papers found: {len(self.papers)}")
        return self.papers

    def extract_paper_info(self, hit, category):
        """Extract relevant information from a paper hit"""
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
            
            if not arxiv_id:
                return None
                
            return {
                'title': title,
                'arxiv_id': arxiv_id,
                'cite_key': cite_key,
                'date_created': date_created,
                'category': category,
                'inspire_url': f"https://inspirehep.net/literature/{hit['id']}"
            }
            
        except (KeyError, IndexError) as e:
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

    def categorize_papers(self):
        """Categorize papers based on keywords and metadata"""
        categories = {
            'reviews': [],
            'model_building': [],
            'dark_matter': [],
            'experimental': [],
            'machine_learning': [],
            'new_signatures': [],
            'reinterpretation': [],
            'low_energy': [],
            'lepton_colliders': []
        }
        
        for paper in self.papers:
            title_lower = paper['title'].lower()
            
            # Simple keyword-based categorization
            if any(word in title_lower for word in ['review', 'survey']):
                categories['reviews'].append(paper)
            elif any(word in title_lower for word in ['atlas', 'cms', 'lhcb', 'search', 'measurement']):
                categories['experimental'].append(paper)
            elif any(word in title_lower for word in ['dark matter', 'wimp', 'relic']):
                categories['dark_matter'].append(paper)
            elif any(word in title_lower for word in ['machine learning', 'neural', 'deep learning']):
                categories['machine_learning'].append(paper)
            elif any(word in title_lower for word in ['model', 'theory', 'composite']):
                categories['model_building'].append(paper)
            else:
                categories['new_signatures'].append(paper)
        
        return categories

    def generate_readme(self, filename="README.md"):
        """Generate a README file similar to the provided example"""
        output_path = os.path.join(self.output_dir, filename)
        categories = self.categorize_papers()
        
        with open(output_path, 'w') as f:
            f.write("# **A Living Review of Dark Showers**\n\n")
            f.write("*Dark showers sit at a rich intersection of theory, phenomenology and experimental efforts. ")
            f.write("They connect different areas of theoretical physics with each other and arise from well motivated ")
            f.write("theoretical scenarios. Below is a list of papers concerning dark showers.*\n\n")
            
            f.write("The purpose of this note is to collect references for dark showers. A minimal number of categories ")
            f.write("is chosen in order to be as useful as possible. Note that papers may be referenced in more than one ")
            f.write("category.\n\n")
            
            f.write(f"**Last updated:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**Search period:** {self.starting_date} to present\n")
            f.write(f"**Total papers found:** {len(self.papers)}\n\n")
            
            # Write categorized papers
            for category_key, papers in categories.items():
                if not papers:
                    continue
                
                category_title = category_key.replace('_', ' ').title()
                f.write(f"## {category_title}\n\n")
                
                for paper in papers:
                    f.write(f"* [{paper['title']}]({paper['inspire_url']})\n")
                    f.write(f"  * arXiv:{paper['arxiv_id']} | {paper['date_created']} | {paper['category']}\n")
                
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
                       default="./")
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
