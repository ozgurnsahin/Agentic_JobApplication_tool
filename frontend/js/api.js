// API Communication Layer
class API {
    constructor() {
        this.baseURL = '/api';
        this.timeout = 30000; // 30 seconds
    }
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: this.timeout,
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...finalOptions,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.blob();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
    
    // Health check
    async healthCheck() {
        try {
            const response = await this.request('/health', { method: 'GET' });
            return response;
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }
    
    // Agent API methods
    async startAgent() {
        return this.post('/agent/start', {});
    }
    
    async getAgentStatus() {
        return this.get('/agent/status');
    }
    
    // Jobs API methods
    async getJobs(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.company) params.append('company', filters.company);
        if (filters.title) params.append('title', filters.title);
        if (filters.source) params.append('source', filters.source);
        
        const queryString = params.toString();
        const endpoint = queryString ? `/jobs?${queryString}` : '/jobs';
        
        return this.get(endpoint);
    }
    
    // CVs API methods
    async downloadCV(cvId) {
        const endpoint = `/cvs/${cvId}/download`;
        return this.request(endpoint, {
            method: 'GET',
            headers: {} // Remove Content-Type for blob responses
        });
    }
    
    // Stats API methods
    async getStats() {
        return this.get('/stats');
    }
}

// Utility functions for API responses
class APIUtils {
    static handleError(error, context = '') {
        console.error(`${context} error:`, error);
        
        let message = 'An unexpected error occurred';
        
        if (error.name === 'AbortError') {
            message = 'Request timed out';
        } else if (error.message.includes('Failed to fetch')) {
            message = 'Unable to connect to server';
        } else if (error.message.includes('HTTP error')) {
            message = 'Server error occurred';
        }
        
        showToast(message, 'error');
        return null;
    }
    
    static async safeApiCall(apiCall, context = '') {
        try {
            showLoading(true);
            const result = await apiCall();
            showLoading(false);
            return result;
        } catch (error) {
            showLoading(false);
            return this.handleError(error, context);
        }
    }
}

// Create API instance
const api = new API();