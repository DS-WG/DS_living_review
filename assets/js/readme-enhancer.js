document.addEventListener('DOMContentLoaded', function() {
    // Initialize the README enhancer
    const enhancer = new ReadmeEnhancer();
    enhancer.init();
});

class ReadmeEnhancer {
    constructor() {
        this.sections = [];
        this.expandAllBtn = null;
        this.collapseAllBtn = null;
    }

    init() {
        this.setupButtons();
        this.setupSections();
        this.bindEvents();
        this.restoreState();
    }

    setupButtons() {
        this.expandAllBtn = document.getElementById('expand-all');
        this.collapseAllBtn = document.getElementById('collapse-all');
    }

    setupSections() {
        // Find all h2 elements (main sections)
        const headings = document.querySelectorAll('h2');
        
        headings.forEach((heading, index) => {
            // Skip the first element if it's not actually a section header
            const headingText = heading.textContent.toLowerCase();
            if (headingText.includes('living review') || headingText.includes('dark showers')) {
                return;
            }

            // Create section wrapper
            const section = this.createSection(heading, index);
            this.sections.push(section);
        });
    }

    createSection(heading, index) {
        // Create wrapper for section content
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'section-content';
        contentWrapper.id = `section-${index}`;

        // Find all elements until the next h2 or end of document
        let nextElement = heading.nextElementSibling;
        const elementsToWrap = [];

        while (nextElement && nextElement.tagName !== 'H2') {
            elementsToWrap.push(nextElement);
            nextElement = nextElement.nextElementSibling;
        }

        // Move elements into wrapper
        elementsToWrap.forEach(element => {
            contentWrapper.appendChild(element);
        });

        // Insert wrapper after heading
        heading.parentNode.insertBefore(contentWrapper, heading.nextSibling);

        // Make heading clickable
        heading.style.cursor = 'pointer';
        heading.addEventListener('click', () => this.toggleSection(index));

        return {
            heading: heading,
            content: contentWrapper,
            index: index,
            isCollapsed: false
        };
    }

    bindEvents() {
        if (this.expandAllBtn) {
            this.expandAllBtn.addEventListener('click', () => this.expandAll());
        }
        
        if (this.collapseAllBtn) {
            this.collapseAllBtn.addEventListener('click', () => this.collapseAll());
        }

        // Save state when page is unloaded
        window.addEventListener('beforeunload', () => this.saveState());
    }

    toggleSection(index) {
        const section = this.sections[index];
        if (!section) return;

        const isCurrentlyCollapsed = section.content.classList.contains('collapsed');
        
        if (isCurrentlyCollapsed) {
            this.expandSection(index);
        } else {
            this.collapseSection(index);
        }
    }

    expandSection(index) {
        const section = this.sections[index];
        if (!section) return;

        section.content.classList.remove('collapsed');
        section.heading.classList.remove('collapsed');
        section.isCollapsed = false;

        // Animate expansion
        section.content.style.maxHeight = section.content.scrollHeight + 'px';
        section.content.style.opacity = '1';
        section.content.style.marginTop = '';
        section.content.style.marginBottom = '';
        
        setTimeout(() => {
            section.content.style.maxHeight = '';
        }, 400);
    }

    collapseSection(index) {
        const section = this.sections[index];
        if (!section) return;

        // Set initial height for animation
        section.content.style.maxHeight = section.content.scrollHeight + 'px';
        
        // Force reflow
        section.content.offsetHeight;
        
        section.content.classList.add('collapsed');
        section.heading.classList.add('collapsed');
        section.isCollapsed = true;

        // Animate collapse
        section.content.style.maxHeight = '0';
        section.content.style.opacity = '0';
        section.content.style.marginTop = '0';
        section.content.style.marginBottom = '0';
    }

    expandAll() {
        this.sections.forEach((section, index) => {
            if (section.isCollapsed) {
                this.expandSection(index);
            }
        });
    }

    collapseAll() {
        this.sections.forEach((section, index) => {
            if (!section.isCollapsed) {
                this.collapseSection(index);
            }
        });
    }

    saveState() {
        const state = this.sections.map(section => ({
            index: section.index,
            isCollapsed: section.isCollapsed
        }));
        
        sessionStorage.setItem('readme-sections-state', JSON.stringify(state));
    }

    restoreState() {
        const savedState = sessionStorage.getItem('readme-sections-state');
        if (!savedState) return;

        try {
            const state = JSON.parse(savedState);
            state.forEach(sectionState => {
                if (sectionState.isCollapsed) {
                    // Use setTimeout to ensure DOM is ready
                    setTimeout(() => {
                        this.collapseSection(sectionState.index);
                    }, 100);
                }
            });
        } catch (e) {
            console.warn('Could not restore section states:', e);
        }
    }
}
