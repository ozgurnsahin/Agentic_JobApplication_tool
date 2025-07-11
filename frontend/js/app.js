// Main Application
class JobAppAI {
    constructor() {
        this.agentStatusInterval = null;
        this.statsInterval = null;
        
        this.init();
    }
    
    init() {
        // Initialize router routes
        this.setupRoutes();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start periodic updates
        this.startPeriodicUpdates();
        
        // Initial agent status check
        this.updateAgentStatus();
    }
    
    setupRoutes() {
        // Dashboard route
        router.addRoute('dashboard', () => this.loadDashboard());
        
        // Jobs route
        router.addRoute('jobs', () => this.loadJobs());
        
        // CVs route
        router.addRoute('cvs', () => this.loadCVs());
        
        // Agent control route
        router.addRoute('agent', () => this.loadAgentControl());
    }
    
    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = e.target.closest('.nav-link').getAttribute('href');
                router.navigate(route);
            });
        });
        
        // Start agent button
        const startAgentBtn = document.getElementById('startAgentBtn');
        if (startAgentBtn) {
            startAgentBtn.addEventListener('click', () => this.startAgent());
        }
        
        // Modal close button
        const modalClose = document.getElementById('modalClose');
        if (modalClose) {
            modalClose.addEventListener('click', hideModal);
        }
        
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hideModal();
            }
        });
    }
    
    startPeriodicUpdates() {
        // Update agent status every 5 seconds
        this.agentStatusInterval = setInterval(() => {
            this.updateAgentStatus();
        }, 5000);
        
        // Update stats every 30 seconds
        this.statsInterval = setInterval(() => {
            if (router.getCurrentRoute() === 'dashboard') {
                this.loadDashboardStats();
            }
        }, 30000);
    }
    
    // Dashboard Page
    async loadDashboard() {
        const contentBody = document.getElementById('contentBody');
        
        contentBody.innerHTML = `
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">System Overview</h3>
                    <p class="card-subtitle">Real-time status of your AI job discovery system</p>
                </div>
                <div class="card-body">
                    <div class="progress-container">
                        <div class="progress-label">System Health</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%" id="healthProgress"></div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <span id="lastUpdated">Last updated: Never</span>
                    <button class="btn btn-secondary btn-sm" onclick="jobApp.loadDashboardStats()">
                        Refresh
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Quick Actions</h3>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                        <button class="btn btn-primary" onclick="jobApp.startAgent()">
                            Start Job Discovery
                        </button>
                        <button class="btn btn-secondary" onclick="router.navigate('jobs')">
                            View All Jobs
                        </button>
                        <button class="btn btn-secondary" onclick="router.navigate('cvs')">
                            View CVs
                        </button>
                        <button class="btn btn-secondary" onclick="router.navigate('agent')">
                            Agent Control
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        await this.loadDashboardStats();
    }
    
    async loadDashboardStats() {
        try {
            const stats = await api.getStats();
            const health = await api.healthCheck();
            
            if (stats && stats.data) {
                this.updateStatsDisplay(stats.data);
            }
            
            if (health) {
                this.updateHealthDisplay(health);
            }
            
            document.getElementById('lastUpdated').textContent = 
                `Last updated: ${new Date().toLocaleTimeString()}`;
                
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
            showToast('Failed to load dashboard statistics', 'error');
        }
    }
    
    updateStatsDisplay(stats) {
        const statsGrid = document.getElementById('statsGrid');
        if (!statsGrid) return;
        
        const {
            total_jobs = 0,
            processed_jobs = 0,
            total_cvs = 0,
            avg_match_score = 0
        } = stats;
        
        statsGrid.innerHTML = `
            ${createStatCard(formatNumber(total_jobs), 'Total Jobs Found')}
            ${createStatCard(formatNumber(processed_jobs), 'Jobs Processed')}
            ${createStatCard(formatNumber(total_cvs), 'CVs Generated')}
            ${createStatCard(avg_match_score ? Math.round(avg_match_score) + '%' : '0%', 'Avg Match Score')}
        `;
    }
    
    updateHealthDisplay(health) {
        const healthProgress = document.getElementById('healthProgress');
        if (!healthProgress) return;
        
        const isHealthy = health.status === 'healthy';
        const percentage = isHealthy ? 100 : 0;
        
        healthProgress.style.width = `${percentage}%`;
        healthProgress.style.background = isHealthy ? 
            'var(--gradient-primary)' : 'var(--error-color)';
    }
    
    // Jobs Page
    async loadJobs() {
        const contentBody = document.getElementById('contentBody');
        
        contentBody.innerHTML = `
            <div class="filters-container">
                <div class="filters-grid">
                    <div class="form-group">
                        <label class="form-label">Company</label>
                        <input type="text" class="form-input" id="companyFilter" placeholder="Filter by company...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-input" id="titleFilter" placeholder="Filter by title...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Source</label>
                        <select class="form-select" id="sourceFilter">
                            <option value="">All Sources</option>
                            <option value="linkedin">LinkedIn</option>
                            <option value="kariyer">Kariyer.net</option>
                            <option value="indeed">Indeed</option>
                        </select>
                    </div>
                    <div class="form-group" style="display: flex; align-items: end;">
                        <button class="btn btn-primary" onclick="jobApp.filterJobs()">
                            Apply Filters
                        </button>
                    </div>
                </div>
            </div>
            
            <div id="jobsContainer">
                ${createEmptyState('Loading Jobs', 'Please wait while we fetch your job listings...')}
            </div>
        `;
        
        await this.loadJobsList();
        this.setupJobsFilters();
    }
    
    async loadJobsList(filters = {}) {
        try {
            const response = await api.getJobs(filters);
            const container = document.getElementById('jobsContainer');
            
            if (response && response.jobs && response.jobs.length > 0) {
                const tableHeaders = ['Title', 'Company', 'Source', 'Date', 'Status', 'Actions'];
                const tableRows = response.jobs.map(job => [
                    `<strong>${escapeHtml(job.title)}</strong>`,
                    escapeHtml(job.company || 'N/A'),
                    createBadge(job.source || 'unknown', 'info'),
                    formatDate(job.scraped_date),
                    job.is_processed ? 
                        createBadge('Processed', 'success') : 
                        createBadge('Pending', 'warning'),
                    `
                        <button class="btn btn-sm btn-secondary" onclick="jobApp.viewJobDetails(${job.job_id})">
                            View
                        </button>
                        <a href="${job.link}" target="_blank" class="btn btn-sm btn-primary">
                            Open
                        </a>
                    `
                ]);
                
                container.innerHTML = createTable(tableHeaders, tableRows);
            } else {
                container.innerHTML = createEmptyState(
                    'No Jobs Found', 
                    'No job listings match your current filters.',
                    '<button class="btn btn-primary" onclick="jobApp.startAgent()">Start Job Discovery</button>'
                );
            }
        } catch (error) {
            console.error('Failed to load jobs:', error);
            showToast('Failed to load jobs', 'error');
        }
    }
    
    setupJobsFilters() {
        const companyFilter = document.getElementById('companyFilter');
        const titleFilter = document.getElementById('titleFilter');
        
        const debouncedFilter = debounce(() => this.filterJobs(), 500);
        
        if (companyFilter) companyFilter.addEventListener('input', debouncedFilter);
        if (titleFilter) titleFilter.addEventListener('input', debouncedFilter);
    }
    
    filterJobs() {
        const filters = {
            company: document.getElementById('companyFilter')?.value || '',
            title: document.getElementById('titleFilter')?.value || '',
            source: document.getElementById('sourceFilter')?.value || ''
        };
        
        this.loadJobsList(filters);
    }
    
    async viewJobDetails(jobId) {
        try {
            const response = await api.getJobs();
            const job = response.jobs.find(j => j.job_id === jobId);
            
            if (job) {
                const content = `
                    <div class="form-group">
                        <label class="form-label">Title</label>
                        <p>${escapeHtml(job.title)}</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Company</label>
                        <p>${escapeHtml(job.company || 'N/A')}</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <div style="max-height: 200px; overflow-y: auto; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md);">
                            ${escapeHtml(job.descript || 'No description available')}
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Source</label>
                        <p>${job.source || 'Unknown'}</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Posted Date</label>
                        <p>${formatDate(job.scraped_date)}</p>
                    </div>
                `;
                
                const footer = `
                    <button class="btn btn-secondary" onclick="hideModal()">Close</button>
                    <a href="${job.link}" target="_blank" class="btn btn-primary">View Original</a>
                `;
                
                showModal('Job Details', content, footer);
            }
        } catch (error) {
            showToast('Failed to load job details', 'error');
        }
    }
    
    // CVs Page
    async loadCVs() {
        const contentBody = document.getElementById('contentBody');
        
        contentBody.innerHTML = `
            <div id="cvsContainer">
                ${createEmptyState('Loading CVs', 'Please wait while we fetch your optimized CVs...')}
            </div>
        `;
        
        // Note: CV endpoint not fully implemented in backend, showing placeholder
        setTimeout(() => {
            const container = document.getElementById('cvsContainer');
            container.innerHTML = createEmptyState(
                'CV Manager Coming Soon', 
                'CV management features will be available once CVs are generated by the agent.',
                '<button class="btn btn-primary" onclick="jobApp.startAgent()">Generate CVs</button>'
            );
        }, 1000);
    }
    
    // Agent Control Page
    async loadAgentControl() {
        const contentBody = document.getElementById('contentBody');
        
        contentBody.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Agent Status</h3>
                    <p class="card-subtitle">Monitor and control your AI job discovery agent</p>
                </div>
                <div class="card-body">
                    <div id="agentStatusDisplay">
                        <div class="stat-card">
                            <div class="stat-value" id="agentStatusValue">-</div>
                            <div class="stat-label">Current Status</div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary" onclick="jobApp.startAgent()" id="startAgentControlBtn">
                        Start Agent
                    </button>
                    <button class="btn btn-secondary" onclick="jobApp.updateAgentStatus()">
                        Refresh Status
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Agent Configuration</h3>
                </div>
                <div class="card-body">
                    <p>Agent configuration and advanced controls will be available in future updates.</p>
                </div>
            </div>
        `;
        
        await this.updateAgentStatus();
    }
    
    // Agent methods
    async startAgent() {
        try {
            showLoading(true);
            const response = await api.startAgent();
            showLoading(false);
            
            if (response) {
                showToast('Agent started successfully', 'success');
                this.updateAgentStatus();
            }
        } catch (error) {
            showLoading(false);
            showToast('Failed to start agent', 'error');
        }
    }
    
    async updateAgentStatus() {
        try {
            const status = await api.getAgentStatus();
            this.displayAgentStatus(status);
        } catch (error) {
            console.error('Failed to get agent status:', error);
            this.displayAgentStatus({ status: 'error', message: 'Connection failed' });
        }
    }
    
    displayAgentStatus(status) {
        // Update sidebar status
        const statusDot = document.getElementById('agentStatusDot');
        const statusText = document.getElementById('agentStatusText');
        
        if (statusDot && statusText) {
            statusDot.className = `status-dot ${status.status}`;
            statusText.textContent = status.message || status.status || 'Unknown';
        }
        
        // Update agent control page if open
        const agentStatusValue = document.getElementById('agentStatusValue');
        if (agentStatusValue) {
            agentStatusValue.textContent = (status.status || 'Unknown').toUpperCase();
        }
        
        // Update start button text
        const startBtn = document.getElementById('startAgentBtn');
        const startControlBtn = document.getElementById('startAgentControlBtn');
        
        const buttonText = status.status === 'running' ? 'Agent Running' : 'Start Agent';
        const isDisabled = status.status === 'running';
        
        if (startBtn) {
            startBtn.textContent = buttonText;
            startBtn.disabled = isDisabled;
        }
        
        if (startControlBtn) {
            startControlBtn.textContent = buttonText;
            startControlBtn.disabled = isDisabled;
        }
    }
    
    // Cleanup
    destroy() {
        if (this.agentStatusInterval) {
            clearInterval(this.agentStatusInterval);
        }
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jobApp = new JobAppAI();
});