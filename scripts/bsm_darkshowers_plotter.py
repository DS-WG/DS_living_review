"""
Script to analyze and plot BSM dark showers paper publication trends
Focuses on Beyond Standard Model physics with refined search criteria
"""

import json
import os
from datetime import date, datetime
from collections import defaultdict, Counter
import argparse

import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dateutil import parser   # add at top if you want robust parsing


class BSMDarkShowersAnalyzer:
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        
        # Focus on theory and phenomenology categories for BSM physics
        self.categories = ['hep-ph', 'hep-th','hep-lat', 'hep-ex']

        #self.keywords = [
        #    'dark shower', 'dark showers',
        #    'hidden valley', 'hidden valleys',
        #    'dark pion', 'dark pions',
        #    'dark baryon', 'dark baryons',
        #    'SUEP',
        #    'soft-bomb', 'soft-bombs', 'soft bomb', 'soft bombs',
        #    'dark hadron', 'dark hadrons',
        #    'dark QCD',
        #    'confining dark sector',
        #    'semi-visible jets',
        #    'emerging jets',
        #    'soft unclustered energy',
        #    'dark meson', 'dark mesons',
        #    'composite dark matter',
        #    'dark confinement'
        #]
        self.keywords = [
            'dark showers', 'dark shower','darkshowers', 'darkshower',
            'hidden valley', 'hidden valleys',
            'dark pion', 'dark pions', 'dark baryons', 'SUEP', 'soft-bombs',
            'soft bombs', 'soft-bomb', 'soft bomb',
            'dark hadron', 'dark hadrons', 'dark QCD', 'confining dark sector',
            'semi-visible jets', 'emerging jets', 'soft unclustered energy',
            'dark mesons', 'composite dark matter', 'dark confinement',
            'SIMP', 'SIMPs', 'Quirks', 'Quirk', 'dark glueball', 'dark glueballs',
            'hidden glueball', 'hidden glueballs','strongly coupled dark matter', 'semi visible jets'
        ]

        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store data
        self.all_papers = []
        self.papers_by_year = defaultdict(list)
        self.papers_by_keyword = defaultdict(list)

    def normalize_keyword(self, keyword):
        """Normalize keywords to combine singular/plural forms"""
        # Remove trailing 's' for plurals, normalize spacing
        normalized = keyword.lower().strip()

        # Specific normalizations
        normalizations = {
            'dark showers': 'dark shower',
            'darkshowers': 'dark shower',
            'darkshower': 'dark shower',
            'hidden valleys': 'hidden valley',
            'dark pions': 'dark pion',
            'dark baryons': 'dark baryon',
            'dark hadrons': 'dark hadron',
            'dark mesons': 'dark meson',
            'soft bombs': 'SUEP',
            'soft bomb': 'SUEP',
            'soft-bombs': 'SUEP',
            'soft-bomb': 'SUEP',
            'soft unclustered energy': 'SUEP',
            'SIMPs': 'SIMP',
            'Quirks': 'Quirk',
            'dark glueballs': 'dark glueballs',
            'hidden glueballs':'dark glueball',
            'hidden glueball':'dark glueball'
        }

        return normalizations.get(normalized, normalized)

    def build_search_query(self, start_year=2010):
        """Build comprehensive search query for dark showers"""
        # Main dark showers keywords
        main_keywords = ' OR '.join([f'"{keyword}"' for keyword in self.keywords])
        
        # Date constraint
        date_constraint = f"de >= {start_year}"
        
        # Combine: (main keywords) AND (date)
        query = f"({main_keywords}) AND {date_constraint}"
        
        return query

    def search_all_papers(self, start_year=2010, end_year=None):
        """Search for all BSM dark showers papers across categories"""
        if end_year is None:
            end_year = date.today().strftime("%d-%m-%y")
            
        print(f"Searching for BSM dark showers papers from {start_year} to {end_year}")
        print(f"Categories: {self.categories}")
        print(f"Keywords: {self.keywords[:5]}... (and {len(self.keywords)-5} more)")
        
        all_papers = []
        
        # Build search query
        base_query = self.build_search_query(start_year)
        
        for category in self.categories:
            print(f"\nSearching category: {category}")
            
            # Add category constraint
            query = f"primarch {category} AND {base_query}"
            
            # URL encode the query
            encoded_query = requests.utils.quote(query)
            
            # Build API URL
            api_url = f"https://inspirehep.net/api/literature?sort=mostrecent&size=1000&q={encoded_query}"
            
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                total_hits = data['hits']['total']
                if total_hits > 1000:
                    print(f"WARNING: Found {total_hits} hits for {category}! Only processing first 1000.")
                
                print(f"Found {total_hits} papers in {category}")
                
                for hit in data['hits']['hits']:
                    paper_info = self.extract_paper_info(hit, category)
                    if paper_info and start_year <= paper_info['year'] <= end_year:
                        all_papers.append(paper_info)
                        
            except requests.RequestException as e:
                print(f"Error searching {category}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error in {category}: {e}")
                continue
        
        # Remove duplicates based on arXiv ID or inspire ID
        seen_ids = set()
        unique_papers = []
        
        for paper in all_papers:
            paper_id = paper.get('arxiv_id') or paper.get('inspire_id')
            if paper_id and paper_id not in seen_ids:
                unique_papers.append(paper)
                seen_ids.add(paper_id)
        
        self.all_papers = sorted(unique_papers, key=lambda x: x['year'])
        
        print(f"\nTotal unique papers found: {len(self.all_papers)}")
        return self.all_papers

    def extract_paper_info(self, hit, category):
        """Extract relevant information from a paper hit"""
        try:
            metadata = hit['metadata']
            
            # Extract basic info
            title = metadata['titles'][0]['title']

            if 'earliest_date' in metadata:
                try:
                    year = parser.parse(metadata['earliest_date']).year
                except Exception:
                    year = int(metadata['earliest_date'][:4])
            elif 'created' in hit:
                try:
                    year = parser.parse(hit['created']).year
                except Exception:
                    year = int(hit['created'][:4])
            
            # Extract arXiv ID
            arxiv_id = None
            if 'arxiv_eprints' in metadata and metadata['arxiv_eprints']:
                arxiv_id = metadata['arxiv_eprints'][0]['value']
            
            # Extract authors
            authors = []
            if 'authors' in metadata:
                for author in metadata['authors'][:3]:  # First 3 authors
                    if 'full_name' in author:
                        authors.append(author['full_name'])
            
            # Check which keywords this paper matches
            title_lower = title.lower()
            abstract_lower = ""
            if 'abstracts' in metadata and metadata['abstracts']:
                abstract_lower = metadata['abstracts'][0].get('value', '').lower()
            
            text_to_search = f"{title_lower} {abstract_lower}"

            matched_keywords = []
            matched_normalized = set()  # Track normalized versions to avoid duplicates

            for keyword in self.keywords:
                if keyword.lower() in text_to_search:
                    normalized = self.normalize_keyword(keyword)
                    if normalized not in matched_normalized:
                        matched_keywords.append(normalized)
                        matched_normalized.add(normalized)
            
            return {
                'title': title,
                'arxiv_id': arxiv_id,
                'inspire_id': hit['id'],
                'year': year,
                'category': category,
                'authors': authors,
                'matched_keywords': matched_keywords,
                'inspire_url': f"https://inspirehep.net/literature/{hit['id']}"
            }
            
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error extracting paper info: {e}")
            return None

    def analyze_trends(self):
        """Analyze publication trends"""
        # Clear existing data first
        self.papers_by_year.clear()
        self.papers_by_keyword.clear()

        # Group papers by year
        for paper in self.all_papers:
            year = paper['year']
            self.papers_by_year[year].append(paper)

            # Group by matched keywords (normalized)
            for keyword in paper['matched_keywords']:
                normalized_keyword = self.normalize_keyword(keyword)
                self.papers_by_keyword[normalized_keyword].append(paper)
        
        # Create summary statistics
        years = sorted(self.papers_by_year.keys())
        yearly_counts = [len(self.papers_by_year[year]) for year in years]
        
        print(f"\nPublication trends analysis:")
        print(f"Years covered: {min(years)} - {max(years)}")
        print(f"Peak year: {years[yearly_counts.index(max(yearly_counts))]} ({max(yearly_counts)} papers)")
        print(f"Average papers per year: {np.mean(yearly_counts):.1f}")
        
        # Most common keywords
        keyword_counts = {k: len(v) for k, v in self.papers_by_keyword.items()}
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\nTop keywords by paper count:")
        for keyword, count in top_keywords:
            print(f"  {keyword}: {count} papers")
        
        return years, yearly_counts

    def plot_single_chart(self, start_year=2010, end_year=None):
        """Create a single clean chart matching HEP-ML style"""
        if end_year is None:
            end_year = datetime.now().year
        
        if not self.all_papers:
            print("No papers loaded. Run search_all_papers() first.")
            return
        
        years, yearly_counts = self.analyze_trends()
        
        # Create figure with specific size and styling
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create bars with HEP-ML style
        bars = ax.bar(years, yearly_counts, color='steelblue', alpha=0.8, 
                     edgecolor='black', linewidth=0.5, width=0.8)
        
        # Styling to match the reference plot
        ax.set_title('Number of Dark Showers Papers by Year', fontsize=20, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=18, fontweight='bold')
        ax.set_ylabel('Number of Papers', fontsize=18, fontweight='bold')
        
        # Grid styling
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set axis limits and ticks
        ax.set_xlim(min(years) - 0.5, max(years) + 0.5)
        ax.set_ylim(0, max(yearly_counts) * 1.1)
        
        # Format x-axis to show all years
        ax.set_xticks(years)
        ax.set_xticklabels([str(year) for year in years], rotation=45)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%d.%m.%Y')
        ax.text(0.02, 0.98, f'As of {timestamp}', transform=ax.transAxes, 
                fontsize=16, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.output_dir, 'darkshowers_papers_by_year.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Single chart saved to {plot_path}")

        return fig

    def plot_publication_trends(self, start_year=2010, end_year=None):
        """Create plots showing publication trends"""
        if end_year is None:
            end_year = datetime.now().year

        if not self.all_papers:
            print("No papers loaded. Run search_all_papers() first.")
            return

        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dark Showers Publication Trends Analysis', fontsize=18, fontweight='bold')

        # Plot 1: Total papers per year
        years, yearly_counts = self.analyze_trends()

        axes[0, 0].bar(years, yearly_counts, color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.5)
        axes[0, 0].set_title('Total Papers per Year', fontweight='bold')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Number of Papers')
        axes[0, 0].grid(True, alpha=0.3)

        # Add trend line
        #if len(years) > 1:
        #    z = np.polyfit(years, yearly_counts, 1)
        #    p = np.poly1d(z)
        #    axes[0, 0].plot(years, p(years), "r--", alpha=0.8, linewidth=2, label=f'Trend')
        #    axes[0, 0].legend()

        # Plot 2: Cumulative papers over time
        cumulative_counts = np.cumsum(yearly_counts)
        axes[0, 1].plot(years, cumulative_counts, marker='o', linewidth=2, markersize=4, color='darkgreen')
        axes[0, 1].set_title('Cumulative Papers Over Time', fontweight='bold')
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Cumulative Number of Papers')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].fill_between(years, cumulative_counts, alpha=0.3, color='darkgreen')

        # Plot 3: Top keywords distribution
        keyword_counts = {k: len(v) for k, v in self.papers_by_keyword.items()}
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        keywords, counts = zip(*top_keywords)
        colors = plt.cm.Set3(np.linspace(0, 1, len(keywords)))

        bars = axes[1, 0].barh(keywords, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        axes[1, 0].set_title('Most Common Keywords (non-unique counting)', fontweight='bold')
        axes[1, 0].set_xlabel('Number of Papers')
        axes[1, 0].grid(True, alpha=0.3, axis='x')

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            axes[1, 0].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                           str(count), ha='left', va='center', fontweight='bold')

        # Plot 4: Papers by arXiv category
        category_counts = Counter(paper['category'] for paper in self.all_papers)
        categories, cat_counts = zip(*category_counts.most_common())

        wedges, texts, autotexts = axes[1, 1].pie(cat_counts, autopct='%1.1f%%',colors=plt.cm.Pastel1(np.linspace(0, 1, len(categories))))
        axes[1, 1].legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        axes[1, 1].set_title('Distribution by arXiv Category', fontweight='bold')

        plt.tight_layout()

        # Save plot
        plot_path = os.path.join(self.output_dir, 'darkshowers_publication_trends.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {plot_path}")

        return fig

    def plot_yearly_papers(self, start_year=2010, end_year=None):
        """Plot 1: Total papers per year"""
        if end_year is None:
            end_year = datetime.now().year

        years, yearly_counts = list(self.papers_by_year.keys()), [len(v) for v in self.papers_by_year.values()]
        years, yearly_counts = zip(*sorted(zip(years, yearly_counts)))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(years, yearly_counts, color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.set_title('Total Dark Showers Papers per Year', fontweight='bold', fontsize=20)
        ax.set_xlabel('Year', fontsize=18)
        ax.set_ylabel('Number of Papers', fontsize=18)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, 'darkshowers_yearly_papers.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Yearly papers plot saved to {plot_path}")
        return fig

    def plot_cumulative_papers(self, start_year=2010, end_year=None):
        """Plot 2: Cumulative papers over time"""
        if end_year is None:
            end_year = datetime.now().year

        years, yearly_counts = list(self.papers_by_year.keys()), [len(v) for v in self.papers_by_year.values()]
        years, yearly_counts = zip(*sorted(zip(years, yearly_counts)))
        cumulative_counts = np.cumsum(yearly_counts)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, cumulative_counts, marker='o', linewidth=2, markersize=4, color='darkgreen')
        ax.set_title('Cumulative Dark Showers Papers Over Time', fontweight='bold', fontsize=20)
        ax.set_xlabel('Year', fontsize=18)
        ax.set_ylabel('Cumulative Number of Papers', fontsize=18)
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        ax.grid(True, alpha=0.3)
        ax.fill_between(years, cumulative_counts, alpha=0.3, color='darkgreen')

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, 'darkshowers_cumulative_papers.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Cumulative papers plot saved to {plot_path}")
        return fig

    def plot_keyword_distribution(self):
        """Plot 3: Top keywords distribution"""
        keyword_counts = {k: len(v) for k, v in self.papers_by_keyword.items()}
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        keywords, counts = zip(*top_keywords)
        colors = plt.cm.Set3(np.linspace(0, 1, len(keywords)))

        # Add this before creating the plot
        keyword_display_names = {
            'dark baryon': 'Dark baryon',
            'dark pion': 'Dark pion',
            'dark glueball': 'Dark glueball',
            'simp': 'SIMP',
            'hidden valley': 'Hidden Valley',
            'quirk': 'Quirk',
            'suep': 'SUEP',
            'dark qcd': 'Dark QCD',
            'composite dark matter': 'Composite DM'
        }

        # Then when creating keywords list for plotting:
        display_keywords = [keyword_display_names.get(kw, kw.title()) for kw in keywords]

        fig, ax = plt.subplots(figsize=(10, 6))
        #bars = ax.barh(keywords, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        bars = ax.barh(display_keywords, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        ax.set_title('Most Common Keywords', fontweight='bold', fontsize=20)
        ax.set_xlabel('Number of Papers', fontsize=18)
        ax.grid(True, alpha=0.3, axis='x')
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)

        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                    str(count), ha='left', va='center', fontweight='bold', fontsize=16)

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, 'darkshowers_keyword_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Keyword distribution plot saved to {plot_path}")
        return fig

    def plot_category_distribution(self):
        """Plot 4: Papers by arXiv category"""
        category_counts = Counter(paper['category'] for paper in self.all_papers)
        categories, cat_counts = zip(*category_counts.most_common())

        fig, ax = plt.subplots(figsize=(8, 8))

        # Add labels directly to pie()
        wedges, texts, autotexts = ax.pie(cat_counts,
                                          labels=categories,  # ← ADD THIS
                                          autopct='%1.1f%%',
                                          colors=plt.cm.Pastel1(np.linspace(0, 1, len(categories))))

        # Increase font sizes
        for text in texts:
            text.set_fontsize(14)  # Category name font size
            #text.set_fontweight('bold')

        for autotext in autotexts:
            autotext.set_fontsize(14)  # Percentage font size
            #autotext.set_fontweight('bold')

        # Remove legend since labels are on the pie
        # ax.legend(...)  # Comment this out

        ax.set_title('Distribution by arXiv Category', fontweight='bold', fontsize=20)

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, 'darkshowers_category_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Category distribution plot saved to {plot_path}")
        return fig

    def plot_keyword_trends(self, top_n=6):
        """Plot trends for individual keywords over time"""
        if not self.papers_by_keyword:
            print("No keyword data. Run analyze_trends() first.")
            return
        
        # Get top keywords
        keyword_counts = {k: len(v) for k, v in self.papers_by_keyword.items()}
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.tab10(np.linspace(0, 1, len(top_keywords)))
        
        for i, (keyword, _) in enumerate(top_keywords):
            papers = self.papers_by_keyword[keyword]
            
            # Count papers per year for this keyword
            yearly_counts = Counter(paper['year'] for paper in papers)
            years = sorted(yearly_counts.keys())
            counts = [yearly_counts[year] for year in years]
            
            ax.plot(years, counts, marker='o', linewidth=2, markersize=4, 
                   label=keyword, color=colors[i])
        
        ax.set_title('Publication Trends by Keyword', fontsize=20, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Papers')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.output_dir, 'darkshowers_keyword_trends.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Keyword trends plot saved to {plot_path}")

        return fig

    def export_data(self, filename="darkshowers_analysis.json"):
        """Export analysis data to JSON"""
        output_path = os.path.join(self.output_dir, filename)
        
        # Prepare data for export
        export_data = {
            'search_parameters': {
                'categories': self.categories,
                'keywords': self.keywords,
                'generated_on': datetime.now().isoformat()
            },
            'summary_statistics': {
                'total_papers': len(self.all_papers),
                'years_covered': f"{min(p['year'] for p in self.all_papers)} - {max(p['year'] for p in self.all_papers)}",
                'papers_by_year': {str(year): len(papers) for year, papers in self.papers_by_year.items()},
                'keyword_counts': {k: len(v) for k, v in self.papers_by_keyword.items()}
            },
            'papers': self.all_papers
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Analysis data exported to {output_path}")
        return output_path

    def generate_summary_report(self, filename="darkshowers_summary.txt"):
        """Generate a text summary report"""
        output_path = os.path.join(self.output_dir, filename)
        
        years, yearly_counts = self.analyze_trends()
        keyword_counts = {k: len(v) for k, v in self.papers_by_keyword.items()}
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        with open(output_path, 'w') as f:
            f.write("Dark Showers Publication Analysis Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total papers analyzed: {len(self.all_papers)}\n")
            f.write(f"Years covered: {min(years)} - {max(years)}\n\n")
            
            f.write("Publication Statistics:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Peak year: {years[yearly_counts.index(max(yearly_counts))]} ({max(yearly_counts)} papers)\n")
            f.write(f"Average papers per year: {np.mean(yearly_counts):.1f}\n")
            f.write(f"Total citations needed: {len(self.all_papers)}\n\n")
            
            f.write("Top Keywords:\n")
            f.write("-" * 15 + "\n")
            for keyword, count in top_keywords:
                f.write(f"{keyword}: {count} papers\n")
            f.write("\n")
            
            f.write("Papers by Year:\n")
            f.write("-" * 16 + "\n")
            for year, count in zip(years, yearly_counts):
                f.write(f"{year}: {count} papers\n")
        
        print(f"Summary report saved to {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Analyze dark showers publication trends")
    parser.add_argument("-d", "--date", type=str, help="Starting date (dd-mm-yy)")
    parser.add_argument("-e", "--end-date", type=str, default=date.today().strftime("%d-%m-%y"),
                        help="Ending date in dd-mm-yy format (default: today)")
    parser.add_argument("-o", "--output", type=str, default="results",
                        help="Output directory")
    parser.add_argument("--single-plot", action="store_true",
                        help="Generate single clean plot only")
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip generating plots")
    parser.add_argument("--export-only", action="store_true",
                        help="Only export data, don't generate plots")

    args = parser.parse_args()

    # Parse starting and ending dates in dd-mm-yy format
    try:
        start_date = datetime.strptime(args.date, "%d-%m-%y").date() if args.date else None
        end_date = datetime.strptime(args.end_date, "%d-%m-%y").date()
    except ValueError:
        print("Invalid date format. Use dd-mm-yy")
        return

    # Create analyzer
    analyzer = BSMDarkShowersAnalyzer(output_dir=args.output)

    # Search for papers
    print("Searching for dark showers papers...")
    papers = analyzer.search_all_papers(start_year=start_date.year if start_date else 2010,
                                        end_year=end_date.year)

    if not papers:
        print("No papers found!")
        return

    # Analyze trends
    analyzer.analyze_trends()

    # Generate outputs
    if args.single_plot:
        print("\nGenerating single clean plot...")
        analyzer.plot_single_chart(start_year=start_date.year if start_date else 2010,
                                   end_year=end_date.year)
    elif not args.export_only and not args.no_plots:
        print("\nGenerating individual plots...")
        analyzer.plot_yearly_papers(start_year=start_date.year if start_date else 2010,
                                    end_year=end_date.year)
        analyzer.plot_cumulative_papers(start_year=start_date.year if start_date else 2010,
                                        end_year=end_date.year)
        analyzer.plot_keyword_distribution()
        analyzer.plot_category_distribution()
        analyzer.plot_keyword_trends()
        analyzer.plot_single_chart(start_year=start_date.year if start_date else 2010,
                                   end_year=end_date.year)

    print("\nExporting data...")
    analyzer.export_data()

    print("Generating summary report...")
    analyzer.generate_summary_report()

    print(f"\nAnalysis complete! Check '{args.output}' directory for results.")


if __name__ == "__main__":
    main()