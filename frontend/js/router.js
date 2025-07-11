// Client-side Router
class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.defaultRoute = 'dashboard';
        
        // Bind methods
        this.navigate = this.navigate.bind(this);
        this.handleHashChange = this.handleHashChange.bind(this);
        
        // Listen for hash changes
        window.addEventListener('hashchange', this.handleHashChange);
        window.addEventListener('load', this.handleHashChange);
    }
    
    // Add a route
    addRoute(path, handler) {
        this.routes[path] = handler;
    }
    
    // Navigate to a route
    navigate(path) {
        if (path.startsWith('#/')) {
            path = path.substring(2);
        } else if (path.startsWith('/')) {
            path = path.substring(1);
        }
        
        window.location.hash = `#/${path}`;
    }
    
    // Handle hash changes
    handleHashChange() {
        let hash = window.location.hash.substring(1); // Remove #
        
        if (hash.startsWith('/')) {
            hash = hash.substring(1); // Remove /
        }
        
        if (!hash) {
            hash = this.defaultRoute;
        }
        
        this.currentRoute = hash;
        this.executeRoute(hash);
    }
    
    // Execute route handler
    executeRoute(path) {
        const handler = this.routes[path];
        
        if (handler) {
            // Update active navigation
            this.updateActiveNavigation(path);
            
            // Update page title
            this.updatePageTitle(path);
            
            // Execute route handler
            handler();
        } else {
            // Route not found, redirect to default
            this.navigate(this.defaultRoute);
        }
    }
    
    // Update active navigation item
    updateActiveNavigation(path) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.route === path) {
                link.classList.add('active');
            }
        });
    }
    
    // Update page title
    updatePageTitle(path) {
        const titles = {
            'dashboard': 'Dashboard',
            'jobs': 'Jobs Management',
            'cvs': 'CV Manager',
            'agent': 'Agent Control'
        };
        
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            pageTitle.textContent = titles[path] || 'JobApp AI Agent';
        }
        
        // Update document title
        document.title = `${titles[path] || 'JobApp AI Agent'} - JobApp AI Agent`;
    }
    
    // Get current route
    getCurrentRoute() {
        return this.currentRoute;
    }
}

// Create router instance
const router = new Router();