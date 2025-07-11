// UI Components and Utilities

// Loading overlay management
function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }
}

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    toast.innerHTML = `
        <div class="toast-header">
            <h4 class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</h4>
            <button class="toast-close">&times;</button>
        </div>
        <p class="toast-message">${message}</p>
    `;
    
    container.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove
    const autoRemove = setTimeout(() => removeToast(toast), duration);
    
    // Manual close
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        clearTimeout(autoRemove);
        removeToast(toast);
    });
}

function removeToast(toast) {
    toast.classList.remove('show');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Modal management
function showModal(title, content, footer = '') {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('modal');
    const titleEl = document.getElementById('modalTitle');
    const bodyEl = document.getElementById('modalBody');
    const footerEl = document.getElementById('modalFooter');
    
    if (!overlay || !modal) return;
    
    titleEl.textContent = title;
    bodyEl.innerHTML = content;
    footerEl.innerHTML = footer;
    
    overlay.classList.add('active');
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            hideModal();
        }
    });
}

function hideModal() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Statistics card component
function createStatCard(value, label, icon = null) {
    return `
        <div class="stat-card">
            ${icon ? `<img src="${icon}" alt="${label}" class="stat-icon">` : ''}
            <div class="stat-value">${value}</div>
            <div class="stat-label">${label}</div>
        </div>
    `;
}

// Progress bar component
function createProgressBar(percentage, label = '') {
    return `
        <div class="progress-container">
            ${label ? `<div class="progress-label">${label}</div>` : ''}
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

// Badge component
function createBadge(text, type = 'secondary') {
    return `<span class="badge badge-${type}">${text}</span>`;
}

// Table component
function createTable(headers, rows, options = {}) {
    const { hoverable = true, striped = false } = options;
    
    let tableClass = 'table';
    if (hoverable) tableClass += ' table-hover';
    if (striped) tableClass += ' table-striped';
    
    const headerRow = headers.map(header => `<th>${header}</th>`).join('');
    const bodyRows = rows.map(row => 
        `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
    ).join('');
    
    return `
        <div class="table-container">
            <table class="${tableClass}">
                <thead>
                    <tr>${headerRow}</tr>
                </thead>
                <tbody>
                    ${bodyRows}
                </tbody>
            </table>
        </div>
    `;
}

// Form components
function createFormGroup(label, input, required = false) {
    return `
        <div class="form-group">
            <label class="form-label">
                ${label}
                ${required ? '<span class="text-error">*</span>' : ''}
            </label>
            ${input}
        </div>
    `;
}

function createInput(type, name, placeholder = '', value = '', required = false) {
    return `
        <input 
            type="${type}" 
            name="${name}" 
            class="form-input" 
            placeholder="${placeholder}"
            value="${value}"
            ${required ? 'required' : ''}
        >
    `;
}

function createSelect(name, options, selected = '', required = false) {
    const optionElements = options.map(option => {
        const value = typeof option === 'object' ? option.value : option;
        const text = typeof option === 'object' ? option.text : option;
        const isSelected = value === selected ? 'selected' : '';
        return `<option value="${value}" ${isSelected}>${text}</option>`;
    }).join('');
    
    return `
        <select name="${name}" class="form-select" ${required ? 'required' : ''}>
            <option value="">Select an option...</option>
            ${optionElements}
        </select>
    `;
}

// Format utilities
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(number) {
    if (typeof number !== 'number') return '0';
    return number.toLocaleString();
}

function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text || '';
    return text.substring(0, maxLength) + '...';
}

// Empty state component
function createEmptyState(title, message, actionButton = null) {
    return `
        <div class="empty-state">
            <div class="empty-state-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 6v6l4 2"></path>
                </svg>
            </div>
            <h3 class="empty-state-title">${title}</h3>
            <p class="empty-state-message">${message}</p>
            ${actionButton || ''}
        </div>
    `;
}

// Debounce utility for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Download utility
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Copy to clipboard utility
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success', 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy to clipboard', 'error');
    }
}

// Escape HTML utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}