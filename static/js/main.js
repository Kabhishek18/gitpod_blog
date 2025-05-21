// static/js/main.js

/**
 * Portfolio Platform - Main JavaScript
 * Handles UI interactions, AJAX requests, and dynamic content
 */

class PortfolioPlatform {
    constructor() {
        this.config = {
            apiBaseUrl: '/api/',
            aiApiBaseUrl: '/ai/',
            loadingDelay: 300,
            notificationDuration: 5000
        };
        
        this.state = {
            isLoading: false,
            currentPage: 1,
            hasMorePosts: true
        };
        
        this.elements = {};
        this.init();
    }

    // =============================================================================
    // Initialization
    // =============================================================================

    init() {
        this.cacheElements();
        this.setupCSRF();
        this.bindEvents();
        this.initializeComponents();
        this.checkPendingNotifications();
        
        console.log('Portfolio Platform initialized successfully');
    }

    cacheElements() {
        this.elements = {
            loadingIndicator: document.getElementById('loading-indicator'),
            navbar: document.querySelector('.navbar'),
            body: document.body,
            searchForms: document.querySelectorAll('form[role="search"], .search-form'),
            newsletterForms: document.querySelectorAll('.newsletter-form'),
            contactForm: document.querySelector('#contact-form'),
            blogPosts: document.querySelector('.blog-posts'),
            loadMoreBtn: document.querySelector('#load-more-posts')
        };
    }

    setupCSRF() {
        const csrfToken = this.getCookie('csrftoken');
        
        this.defaultHeaders = {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        };
        
        // Setup for jQuery if available
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: (xhr, settings) => {
                    if (!settings.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                }
            });
        }
    }

    bindEvents() {
        // Navigation events
        this.bindNavigationEvents();
        
        // Form events
        this.bindFormEvents();
        
        // AI form events
        this.bindAIFormEvents();
        
        // Scroll events
        this.bindScrollEvents();
        
        // Click events
        this.bindClickEvents();
        
        // Dynamic content events
        this.bindDynamicEvents();
    }

    bindNavigationEvents() {
        // Navbar scroll effect
        if (this.elements.navbar) {
            window.addEventListener('scroll', this.throttle(() => {
                if (window.scrollY > 50) {
                    this.elements.navbar.classList.add('scrolled');
                } else {
                    this.elements.navbar.classList.remove('scrolled');
                }
            }, 100));
        }
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const targetId = anchor.getAttribute('href');
                if (targetId === '#' || targetId === '#top') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    this.smoothScrollTo(targetElement);
                }
            });
        });
    }

    bindFormEvents() {
        // Newsletter forms
        this.elements.newsletterForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleNewsletterSubmit(e));
        });
        
        // Search forms
        this.elements.searchForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleSearchSubmit(e));
        });
        
        // Contact form
        if (this.elements.contactForm) {
            this.elements.contactForm.addEventListener('submit', (e) => this.handleContactSubmit(e));
        }
    }

    bindAIFormEvents() {
        // AI blog draft generation
        this.bindAIForm('#ai-blog-draft-form', '/ai/blog/generate-draft/', this.handleBlogDraftResponse);
        
        // AI content improvement
        this.bindAIForm('#ai-improve-form', '/ai/blog/improve-content/', this.handleContentImprovementResponse);
        
        // AI title generation
        this.bindAIForm('#ai-title-form', '/ai/blog/generate-title/', this.handleTitleGenerationResponse);
        
        // AI SEO optimization
        this.bindAIForm('#ai-seo-form', '/ai/blog/seo-optimize/', this.handleSEOResponse);
        
        // AI tone analysis
        this.bindAIForm('#ai-tone-form', '/ai/blog/analyze-tone/', this.handleToneAnalysisResponse);
    }

    bindScrollEvents() {
        // Reading progress bar
        this.initReadingProgress();
        
        // Infinite scroll
        if (this.elements.blogPosts) {
            this.initInfiniteScroll();
        }
        
        // Fade in animation on scroll
        this.initScrollAnimations();
    }

    bindClickEvents() {
        // Copy to clipboard buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-copy]')) {
                const copyBtn = e.target.closest('[data-copy]');
                const textToCopy = copyBtn.getAttribute('data-copy');
                this.copyToClipboard(textToCopy);
            }
        });
        
        // Share buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.share-btn')) {
                this.handleShare(e);
            }
        });
        
        // Load more posts
        if (this.elements.loadMoreBtn) {
            this.elements.loadMoreBtn.addEventListener('click', () => this.loadMorePosts());
        }
    }

    bindDynamicEvents() {
        // Theme toggle
        const themeToggle = document.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Modal triggers
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-modal]')) {
                const modalId = e.target.closest('[data-modal]').getAttribute('data-modal');
                this.openModal(modalId);
            }
        });
    }

    initializeComponents() {
        // Initialize Bootstrap components if available
        if (typeof bootstrap !== 'undefined') {
            this.initBootstrapComponents();
        }
        
        // Initialize syntax highlighting
        this.initSyntaxHighlighting();
        
        // Initialize lazy loading
        this.initLazyLoading();
        
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize animations
        this.initAnimations();
    }

    // =============================================================================
    // Utility Functions
    // =============================================================================

    getCookie(name) {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='))
            ?.split('=')[1];
        return cookieValue || null;
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    debounce(func, wait) {
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

    smoothScrollTo(element, offset = 80) {
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    }

    formatTime(seconds) {
        if (seconds < 1) {
            return `${Math.round(seconds * 1000)}ms`;
        }
        return `${seconds.toFixed(1)}s`;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // =============================================================================
    // Loading & Notifications
    // =============================================================================

    showLoading() {
        if (this.state.isLoading) return;
        
        this.state.isLoading = true;
        
        setTimeout(() => {
            if (this.elements.loadingIndicator && this.state.isLoading) {
                this.elements.loadingIndicator.classList.remove('d-none');
            }
        }, this.config.loadingDelay);
    }

    hideLoading() {
        this.state.isLoading = false;
        
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.classList.add('d-none');
        }
    }

    showNotification(message, type = 'info', duration = this.config.notificationDuration) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const icon = iconMap[type] || iconMap.info;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add animation class
        setTimeout(() => notification.classList.add('fade-in'), 10);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('fade');
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
        
        return notification;
    }

    checkPendingNotifications() {
        const pendingNotification = sessionStorage.getItem('pendingNotification');
        if (pendingNotification) {
            try {
                const notification = JSON.parse(pendingNotification);
                this.showNotification(notification.message, notification.type);
                sessionStorage.removeItem('pendingNotification');
            } catch (e) {
                console.warn('Failed to parse pending notification:', e);
            }
        }
    }

    // =============================================================================
    // Form Handlers
    // =============================================================================

    async handleNewsletterSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const email = form.querySelector('input[type="email"]').value.trim();
        
        if (!email) {
            this.showNotification('Please enter your email address', 'warning');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showNotification('Please enter a valid email address', 'warning');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await this.apiCall('/newsletter/subscribe/', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            
            if (response.ok) {
                this.showNotification('Successfully subscribed to newsletter!', 'success');
                form.reset();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Subscription failed');
            }
        } catch (error) {
            this.showNotification(error.message || 'Failed to subscribe. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    handleSearchSubmit(e) {
        const form = e.target;
        const searchInput = form.querySelector('input[type="search"], input[name="search"]');
        
        if (searchInput && !searchInput.value.trim()) {
            e.preventDefault();
            this.showNotification('Please enter a search term', 'warning');
            searchInput.focus();
        }
    }

    async handleContactSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validate required fields
        const requiredFields = ['name', 'email', 'subject', 'message'];
        const missingFields = requiredFields.filter(field => !data[field]?.trim());
        
        if (missingFields.length > 0) {
            this.showNotification(`Please fill in: ${missingFields.join(', ')}`, 'warning');
            return;
        }
        
        if (!this.isValidEmail(data.email)) {
            this.showNotification('Please enter a valid email address', 'warning');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await this.apiCall('/contact/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(result.message || 'Message sent successfully!', 'success');
                form.reset();
            } else {
                throw new Error(result.error || 'Failed to send message');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // =============================================================================
    // AI Form Handlers
    // =============================================================================

    bindAIForm(selector, endpoint, responseHandler) {
        const form = document.querySelector(selector);
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Validate form data
            if (!this.validateAIFormData(data, form)) {
                return;
            }
            
            try {
                this.showLoading();
                
                const response = await this.apiCall(endpoint, {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    responseHandler.call(this, result, form);
                } else {
                    throw new Error(result.error || 'AI request failed');
                }
            } catch (error) {
                this.showNotification(error.message, 'error');
                console.error('AI Form Error:', error);
            } finally {
                this.hideLoading();
            }
        });
    }

    validateAIFormData(data, form) {
        const requiredFields = form.querySelectorAll('[required]');
        const missingFields = [];
        
        requiredFields.forEach(field => {
            if (!data[field.name]?.trim()) {
                missingFields.push(field.getAttribute('placeholder') || field.name);
            }
        });
        
        if (missingFields.length > 0) {
            this.showNotification(`Please fill in: ${missingFields.join(', ')}`, 'warning');
            return false;
        }
        
        return true;
    }

    // =============================================================================
    // AI Response Handlers
    // =============================================================================

    handleBlogDraftResponse(result, form) {
        const resultContainer = this.getOrCreateResultContainer();
        
        resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="fas fa-robot me-2"></i>Generated Blog Draft</h5>
                    <small class="text-muted">Processing time: ${this.formatTime(result.processing_time || 0)}</small>
                </div>
                
                <div class="mb-3">
                    <textarea class="form-control" rows="20" readonly>${result.draft || ''}</textarea>
                </div>
                
                <div class="d-flex gap-2 mb-3">
                    <button class="btn btn-primary" onclick="portfolio.copyToClipboard(\`${this.escapeText(result.draft)}\`)">
                        <i class="fas fa-copy me-1"></i>Copy Draft
                    </button>
                    <button class="btn btn-outline-secondary" onclick="portfolio.downloadText(\`${this.escapeText(result.draft)}\`, 'blog-draft.txt')">
                        <i class="fas fa-download me-1"></i>Download
                    </button>
                    <button class="btn btn-outline-info" onclick="portfolio.improveContent(\`${this.escapeText(result.draft)}\`)">
                        <i class="fas fa-magic me-1"></i>Improve Further
                    </button>
                </div>
                
                ${this.renderSuggestions(result.suggestions)}
            </div>
        `;
        
        this.scrollToResult(resultContainer);
        this.showNotification('Blog draft generated successfully!', 'success');
    }

    handleContentImprovementResponse(result, form) {
        const resultContainer = this.getOrCreateResultContainer();
        
        resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="fas fa-edit me-2"></i>Improved Content</h5>
                    <small class="text-muted">Processing time: ${this.formatTime(result.processing_time || 0)}</small>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6>Readability Score</h6>
                                <div class="h4 text-primary">${result.readability_score || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6>Word Count Change</h6>
                                <div class="h4 ${result.improvements_made?.word_count_change >= 0 ? 'text-success' : 'text-warning'}">
                                    ${result.improvements_made?.word_count_change >= 0 ? '+' : ''}${result.improvements_made?.word_count_change || 0}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <textarea class="form-control" rows="15" readonly>${result.improved_content || ''}</textarea>
                </div>
                
                <div class="d-flex gap-2 mb-3">
                    <button class="btn btn-primary" onclick="portfolio.copyToClipboard(\`${this.escapeText(result.improved_content)}\`)">
                        <i class="fas fa-copy me-1"></i>Copy Content
                    </button>
                    <button class="btn btn-outline-secondary" onclick="portfolio.downloadText(\`${this.escapeText(result.improved_content)}\`, 'improved-content.txt')">
                        <i class="fas fa-download me-1"></i>Download
                    </button>
                </div>
                
                ${this.renderImprovements(result.improvements_made)}
            </div>
        `;
        
        this.scrollToResult(resultContainer);
        this.showNotification('Content improved successfully!', 'success');
    }

    handleTitleGenerationResponse(result, form) {
        const resultContainer = this.getOrCreateResultContainer();
        
        const titlesHtml = (result.titles || []).map((title, index) => `
            <div class="border rounded p-3 mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="fw-medium">${title}</div>
                        ${result.seo_analysis?.[index] ? `
                            <small class="text-muted">
                                Length: ${result.seo_analysis[index].length} chars | 
                                SEO Score: ${result.seo_analysis[index].seo_score}/100
                                ${result.seo_analysis[index].has_keywords ? ' | <span class="text-success">✓ Keywords</span>' : ''}
                            </small>
                        ` : ''}
                    </div>
                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="portfolio.copyToClipboard(\`${this.escapeText(title)}\`)">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="fas fa-heading me-2"></i>Generated Titles</h5>
                    <small class="text-muted">Processing time: ${this.formatTime(result.processing_time || 0)}</small>
                </div>
                
                <div class="titles-container">
                    ${titlesHtml}
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-outline-primary" onclick="portfolio.copyAllTitles(${JSON.stringify(result.titles || [])})">
                        <i class="fas fa-copy me-1"></i>Copy All Titles
                    </button>
                </div>
            </div>
        `;
    }

    renderSEORecommendations(recommendations) {
        if (!recommendations?.length) return '';
        
        return `
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">SEO Recommendations</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
                        ${recommendations.map(rec => `
                            <li class="mb-2"><i class="fas fa-lightbulb text-warning me-2"></i>${rec}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // =============================================================================
    // Copy and Download Functions
    // =============================================================================

    async copyToClipboard(text) {
        if (!text) {
            this.showNotification('No text to copy', 'warning');
            return;
        }
        
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
            } else {
                this.fallbackCopyToClipboard(text);
            }
            this.showNotification('Copied to clipboard!', 'success', 2000);
        } catch (err) {
            console.warn('Copy failed:', err);
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.cssText = 'position:fixed;left:-9999px;top:-9999px;opacity:0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showNotification('Copied to clipboard!', 'success', 2000);
            } else {
                throw new Error('Copy command failed');
            }
        } catch (err) {
            this.showNotification('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    downloadText(content, filename) {
        if (!content) {
            this.showNotification('No content to download', 'warning');
            return;
        }
        
        try {
            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || 'download.txt';
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            this.showNotification('File downloaded!', 'success', 2000);
        } catch (err) {
            console.error('Download failed:', err);
            this.showNotification('Failed to download file', 'error');
        }
    }

    copyAllTitles(titles) {
        if (!titles?.length) {
            this.showNotification('No titles to copy', 'warning');
            return;
        }
        
        const allTitles = titles.map((title, index) => `${index + 1}. ${title}`).join('\n');
        this.copyToClipboard(allTitles);
    }

    // =============================================================================
    // Component Initialization
    // =============================================================================

    initBootstrapComponents() {
        // Initialize tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        popoverTriggerList.forEach(popoverTriggerEl => {
            new bootstrap.Popover(popoverTriggerEl);
        });

        // Initialize modals
        const modalList = document.querySelectorAll('.modal');
        modalList.forEach(modalEl => {
            new bootstrap.Modal(modalEl);
        });
    }

    initSyntaxHighlighting() {
        // Initialize Prism.js if available
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
        
        // Initialize highlight.js if available
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }
    }

    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.dataset.src || img.dataset.lazySrc;
                        if (src) {
                            img.src = src;
                            img.classList.remove('lazy');
                            img.classList.add('fade-in');
                            imageObserver.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            document.querySelectorAll('img[data-src], img[data-lazy-src], img.lazy').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    initTooltips() {
        // Initialize custom tooltips for elements that need them
        document.querySelectorAll('[title]:not([data-bs-toggle])').forEach(el => {
            if (typeof bootstrap !== 'undefined') {
                new bootstrap.Tooltip(el);
            }
        });
    }

    initAnimations() {
        // Intersection Observer for scroll animations
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                        animationObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                animationObserver.observe(el);
            });
        }
    }

    initReadingProgress() {
        const progressBar = document.querySelector('#reading-progress');
        if (!progressBar) return;

        const article = document.querySelector('.article-content, .blog-post');
        if (!article) return;

        const updateProgress = this.throttle(() => {
            const rect = article.getBoundingClientRect();
            const articleTop = rect.top + window.pageYOffset;
            const articleHeight = article.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollTop = window.pageYOffset;
            
            const progress = Math.min(
                Math.max((scrollTop - articleTop + windowHeight) / articleHeight, 0),
                1
            );
            
            progressBar.style.width = `${progress * 100}%`;
        }, 16);

        window.addEventListener('scroll', updateProgress);
        updateProgress(); // Initial call
    }

    initInfiniteScroll() {
        if (!this.elements.blogPosts) return;

        let loading = false;

        const loadMoreOnScroll = this.throttle(() => {
            if (loading || !this.state.hasMorePosts) return;
            
            const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
            
            if (scrollTop + clientHeight >= scrollHeight - 1000) {
                loading = true;
                this.loadMorePosts().finally(() => {
                    loading = false;
                });
            }
        }, 200);

        window.addEventListener('scroll', loadMoreOnScroll);
    }

    initScrollAnimations() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('slide-in-up');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -100px 0px'
            });

            document.querySelectorAll('.card, .blog-card').forEach(el => {
                observer.observe(el);
            });
        }
    }

    // =============================================================================
    // Dynamic Content Loading
    // =============================================================================

    async loadMorePosts() {
        if (!this.state.hasMorePosts) return;

        try {
            this.showLoading();
            
            const response = await this.apiCall(`/blog/?page=${this.state.currentPage + 1}`);
            const data = await response.json();
            
            if (response.ok && data.results?.length > 0) {
                data.results.forEach(post => {
                    const postElement = this.createPostElement(post);
                    this.elements.blogPosts.appendChild(postElement);
                });
                
                this.state.currentPage++;
                
                // Check if there are more posts
                if (!data.next) {
                    this.state.hasMorePosts = false;
                    if (this.elements.loadMoreBtn) {
                        this.elements.loadMoreBtn.style.display = 'none';
                    }
                }
            } else {
                this.state.hasMorePosts = false;
            }
        } catch (error) {
            this.showNotification('Failed to load more posts', 'error');
            console.error('Load more posts error:', error);
        } finally {
            this.hideLoading();
        }
    }

    createPostElement(post) {
        const article = document.createElement('article');
        article.className = 'card mb-4 border-0 shadow-sm blog-card';
        
        const featuredImage = post.featured_image_url ? `
            <div class="col-md-4">
                <a href="${post.url}">
                    <img src="${post.featured_image_url}" class="img-fluid h-100 object-cover" alt="${post.title}" loading="lazy">
                </a>
            </div>
            <div class="col-md-8">
        ` : '<div class="col-12">';
        
        const categories = post.categories ? post.categories.map(cat => `
            <span class="badge rounded-pill me-1" style="background-color: ${cat.color || '#6c757d'};">
                ${cat.name}
            </span>
        `).join('') : '';
        
        article.innerHTML = `
            <div class="row g-0">
                ${featuredImage}
                    <div class="card-body">
                        ${categories ? `<div class="mb-2">${categories}</div>` : ''}
                        
                        <h5 class="card-title">
                            <a href="${post.url}" class="text-decoration-none text-dark">
                                ${post.title}
                            </a>
                        </h5>
                        
                        <p class="card-text text-muted">${post.excerpt_text || ''}</p>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="text-muted small">
                                <i class="fas fa-user me-1"></i>${post.author?.full_name || post.author?.username || 'Anonymous'}
                                <span class="mx-2">•</span>
                                <i class="fas fa-calendar me-1"></i>${this.formatDate(post.publish_date)}
                                <span class="mx-2">•</span>
                                <i class="fas fa-clock me-1"></i>${post.reading_time || 0} min
                                <span class="mx-2">•</span>
                                <i class="fas fa-eye me-1"></i>${post.view_count || 0}
                            </div>
                            <a href="${post.url}" class="btn btn-outline-primary btn-sm">Read More</a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add animation class
        setTimeout(() => article.classList.add('fade-in'), 100);
        
        return article;
    }

    // =============================================================================
    // API Functions
    // =============================================================================

    async apiCall(endpoint, options = {}) {
        const url = endpoint.startsWith('/') ? endpoint : `${this.config.apiBaseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: { ...this.defaultHeaders },
        };
        
        // Merge options
        const mergedOptions = { ...defaultOptions, ...options };
        
        // Handle different content types
        if (options.headers?.['Content-Type'] === 'multipart/form-data') {
            delete mergedOptions.headers['Content-Type']; // Let browser set boundary
        }

        try {
            const response = await fetch(url, mergedOptions);
            return response;
        } catch (error) {
            console.error('API call failed:', error);
            throw new Error('Network error. Please check your connection.');
        }
    }

    // =============================================================================
    // Utility Methods
    // =============================================================================

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.showNotification(`Switched to ${newTheme} theme`, 'info', 2000);
    }

    handleShare(e) {
        e.preventDefault();
        
        const shareBtn = e.target.closest('.share-btn');
        const platform = shareBtn.dataset.platform;
        const url = shareBtn.dataset.url || window.location.href;
        const title = shareBtn.dataset.title || document.title;
        const text = shareBtn.dataset.text || '';
        
        const shareUrls = {
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
            email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(text + ' ' + url)}`,
            copy: url
        };
        
        if (platform === 'copy') {
            this.copyToClipboard(url);
        } else if (shareUrls[platform]) {
            window.open(shareUrls[platform], '_blank', 'width=600,height=400');
        } else if (navigator.share && platform === 'native') {
            navigator.share({
                title: title,
                text: text,
                url: url
            }).catch(err => console.log('Error sharing:', err));
        }
    }

    openModal(modalId) {
        const modal = document.querySelector(`#${modalId}`);
        if (modal && typeof bootstrap !== 'undefined') {
            const modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
            modalInstance.show();
        }
    }

    // Additional utility methods for specific AI features
    improveContent(content) {
        const form = document.querySelector('#ai-improve-form');
        if (form) {
            const textarea = form.querySelector('textarea[name="content"]');
            if (textarea) {
                textarea.value = content;
                form.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }

    // =============================================================================
    // Event Handler for window events
    // =============================================================================

    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden, pause any animations or polling
            this.pauseActivity();
        } else {
            // Page is visible, resume activity
            this.resumeActivity();
        }
    }

    pauseActivity() {
        // Pause any ongoing activities when page is hidden
        this.state.isPageVisible = false;
    }

    resumeActivity() {
        // Resume activities when page becomes visible
        this.state.isPageVisible = true;
    }
}

// =============================================================================
// Initialize on DOM Ready
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the main application
    window.portfolio = new PortfolioPlatform();
    
    // Set up global error handling
    window.addEventListener('error', (e) => {
        console.error('Global error:', e.error);
        if (window.portfolio) {
            window.portfolio.showNotification('An unexpected error occurred', 'error');
        }
    });
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (window.portfolio) {
            window.portfolio.handleVisibilityChange();
        }
    });
    
    // Handle online/offline status
    window.addEventListener('online', () => {
        if (window.portfolio) {
            window.portfolio.showNotification('Connection restored', 'success', 2000);
        }
    });
    
    window.addEventListener('offline', () => {
        if (window.portfolio) {
            window.portfolio.showNotification('Connection lost. Some features may not work.', 'warning', 5000);
        }
    });
});

// =============================================================================
// Service Worker Registration (Optional)
// =============================================================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// =============================================================================
// Global utility functions
// =============================================================================

// Make copyToClipboard available globally for onclick handlers
window.copyToClipboard = (text) => {
    if (window.portfolio) {
        window.portfolio.copyToClipboard(text);
    }
};

// Make downloadText available globally
window.downloadText = (content, filename) => {
    if (window.portfolio) {
        window.portfolio.downloadText(content, filename);
    }
};

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioPlatform;
}
        
        this.scrollToResult(resultContainer);
        this.showNotification('Titles generated successfully!', 'success');
    }

    handleSEOResponse(result, form) {
        const resultContainer = this.getOrCreateResultContainer();
        
        resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="fas fa-search me-2"></i>SEO Optimization Results</h5>
                    <small class="text-muted">Processing time: ${this.formatTime(result.processing_time || 0)}</small>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6>Current SEO Score</h6>
                                <div class="h3 mb-2">${result.current_seo_score || 0}/100</div>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${result.current_seo_score || 0}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h6>Quick Actions</h6>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-sm btn-outline-primary" onclick="portfolio.copyToClipboard(\`${this.escapeText(result.seo_optimizations?.meta_description || '')}\`)">
                                        Copy Meta Description
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="portfolio.copyToClipboard(\`${this.escapeText(result.seo_optimizations?.suggested_title || '')}\`)">
                                        Copy Title
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${this.renderSEOOptimizations(result.seo_optimizations)}
                ${this.renderSEORecommendations(result.recommendations)}
            </div>
        `;
        
        this.scrollToResult(resultContainer);
        this.showNotification('SEO analysis completed!', 'success');
    }

    handleToneAnalysisResponse(result, form) {
        const resultContainer = this.getOrCreateResultContainer();
        
        const toneData = result.tone || {};
        const suggestions = result.suggestions || [];
        
        resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="fas fa-microphone me-2"></i>Tone Analysis Results</h5>
                    <small class="text-muted">Processing time: ${this.formatTime(result.processing_time || 0)}</small>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h6>Primary Tone</h6>
                                <span class="badge bg-primary fs-6">${toneData.primary_tone || 'Unknown'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h6>Confidence</h6>
                                <div class="h5">${((toneData.confidence || 0) * 100).toFixed(1)}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h6>Readability</h6>
                                <div class="h5">${toneData.readability || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${suggestions.length > 0 ? `
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Tone Improvement Suggestions</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${suggestions.map(suggestion => `
                                    <li class="mb-2">
                                        <i class="fas fa-lightbulb text-warning me-2"></i>${suggestion}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        this.scrollToResult(resultContainer);
        this.showNotification('Tone analysis completed!', 'success');
    }

    // =============================================================================
    // Helper Methods for AI Results
    // =============================================================================

    getOrCreateResultContainer() {
        let container = document.querySelector('#ai-result');
        if (!container) {
            container = document.createElement('div');
            container.id = 'ai-result';
            
            // Find a good place to insert it
            const form = document.querySelector('form[id*="ai-"]');
            if (form) {
                form.parentNode.insertBefore(container, form.nextSibling);
            } else {
                document.querySelector('main, .container, body').appendChild(container);
            }
        }
        return container;
    }

    scrollToResult(container) {
        setTimeout(() => {
            this.smoothScrollTo(container, 100);
        }, 100);
    }

    escapeText(text) {
        if (!text) return '';
        return text.replace(/`/g, '\\`').replace(/\$/g, '\\);
    }

    renderSuggestions(suggestions) {
        if (!suggestions) return '';
        
        let html = '<div class="mt-4"><h6>AI Suggestions</h6>';
        
        if (suggestions.title_suggestions?.length) {
            html += `
                <div class="mb-3">
                    <strong>Title Suggestions:</strong>
                    <div class="mt-2">
                        ${suggestions.title_suggestions.map(title => `
                            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                                <span>${title}</span>
                                <button class="btn btn-sm btn-outline-primary" onclick="portfolio.copyToClipboard(\`${this.escapeText(title)}\`)">
                                    <i class="fas fa-copy"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        if (suggestions.tag_suggestions?.length) {
            html += `
                <div class="mb-3">
                    <strong>Tag Suggestions:</strong>
                    <div class="d-flex flex-wrap gap-2 mt-2">
                        ${suggestions.tag_suggestions.map(tag => `
                            <span class="badge bg-secondary cursor-pointer" onclick="portfolio.copyToClipboard('${tag}')">${tag}</span>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    renderImprovements(improvements) {
        if (!improvements) return '';
        
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6 class="mb-0">Improvements Made</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
                        <li><i class="fas fa-check text-success me-2"></i>Word count change: ${improvements.word_count_change > 0 ? '+' : ''}${improvements.word_count_change}</li>
                        ${(improvements.improvements || []).map(imp => `
                            <li><i class="fas fa-check text-success me-2"></i>${imp}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    renderSEOOptimizations(optimizations) {
        if (!optimizations) return '';
        
        return `
            <div class="card mb-3">
                <div class="card-header">
                    <h6 class="mb-0">SEO Optimizations</h6>
                </div>
                <div class="card-body">
                    ${optimizations.meta_description ? `
                        <div class="mb-3">
                            <strong>Meta Description:</strong>
                            <div class="border rounded p-2 bg-light mt-1">
                                <div class="d-flex justify-content-between align-items-start">
                                    <span class="flex-grow-1">${optimizations.meta_description}</span>
                                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="portfolio.copyToClipboard(\`${this.escapeText(optimizations.meta_description)}\`)">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                                <small class="text-muted">Length: ${optimizations.meta_description.length} characters</small>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${optimizations.suggested_title ? `
                        <div class="mb-3">
                            <strong>Suggested Title:</strong>
                            <div class="border rounded p-2 bg-light mt-1">
                                <div class="d-flex justify-content-between align-items-start">
                                    <span class="flex-grow-1">${optimizations.suggested_title}</span>
                                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="portfolio.copyToClipboard(\`${this.escapeText(optimizations.suggested_title)}\`)">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${optimizations.keywords?.length ? `
                        <div class="mb-3">
                            <strong>SEO Keywords:</strong>
                            <div class="d-flex flex-wrap gap-2 mt-2">
                                ${optimizations.keywords.map(keyword => `
                                    <span class="badge bg-info cursor-pointer" onclick="portfolio.copyToClipboard('${keyword}')">${keyword}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}