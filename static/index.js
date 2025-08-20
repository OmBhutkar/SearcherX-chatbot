// Enhanced JavaScript for SenimSearcherX Bot
var mybut = document.getElementById("btn1");
const x = document.getElementById("myDIV");
const y = document.getElementById("nss");

// Enhanced button click handler with improved UX
mybut.addEventListener("click", function (e) {
    const Inputval = document.getElementById("pwd");
    const inputValue = Inputval.value.trim();
    
    console.log("Search button clicked");
    console.log("Loading display:", x.style.display);
    console.log("No search display:", y.style.display);
    console.log("Input value:", inputValue);

    if (inputValue === "") {
        // Enhanced empty input handling
        console.log("Empty Input - showing validation");
        
        // Add visual feedback for empty input
        Inputval.classList.add("error-shake");
        Inputval.focus();
        
        // Remove shake effect after animation
        setTimeout(() => {
            Inputval.classList.remove("error-shake");
        }, 600);
        
        // Prevent form submission
        e.preventDefault();
        return false;
    } else {
        // Valid input - show loading state
        console.log("Valid input - showing loading state");
        
        // Show loading animation
        if (x.style.display === "none") {
            x.style.display = "block";
            
            // Add fade-in effect
            x.style.opacity = "0";
            setTimeout(() => {
                x.style.opacity = "1";
            }, 10);
        }
        
        // Hide "no searches yet" message
        if (y.style.display === "block") {
            y.style.display = "none";
        }
        
        // Add loading class to button
        mybut.classList.add("loading");
        mybut.disabled = true;
        
        // Store original button text
        const originalText = mybut.innerHTML;
        mybut.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><strong>Searching...</strong>';
        
        // Smooth scroll to loading section
        setTimeout(() => {
            x.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }, 100);
    }
});

// Enhanced input handling with real-time validation
const searchInput = document.getElementById("pwd");

if (searchInput) {
    // Remove error styling when user starts typing
    searchInput.addEventListener("input", function() {
        this.classList.remove("error-shake");
        
        // Real-time character count (optional)
        const value = this.value.trim();
        if (value.length > 0) {
            this.classList.add("has-content");
        } else {
            this.classList.remove("has-content");
        }
    });
    
    // Handle Enter key press
    searchInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            mybut.click();
        }
    });
    
    // Enhanced focus/blur effects
    searchInput.addEventListener("focus", function() {
        this.parentElement.classList.add("input-focused");
    });
    
    searchInput.addEventListener("blur", function() {
        this.parentElement.classList.remove("input-focused");
    });
}

// Utility functions for enhanced user experience
function copyLink(link) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(link).then(() => {
            showToast("Link copied to clipboard!", "success");
        }).catch(() => {
            fallbackCopyText(link);
        });
    } else {
        fallbackCopyText(link);
    }
}

function fallbackCopyText(text) {
    // Fallback for older browsers
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast("Link copied to clipboard!", "success");
    } catch (err) {
        showToast("Failed to copy link", "error");
    }
    
    document.body.removeChild(textArea);
}

function shareResult(title, link) {
    if (navigator.share) {
        navigator.share({
            title: `${title} - Wikipedia`,
            text: `Check out this Wikipedia article: ${title}`,
            url: link
        }).then(() => {
            console.log('Successfully shared');
        }).catch((error) => {
            console.log('Error sharing:', error);
            copyLink(link);
        });
    } else {
        // Fallback to copying link
        copyLink(link);
    }
}

function showToast(message, type = "info") {
    // Create toast notification
    const toast = document.createElement("div");
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function getToastIcon(type) {
    switch (type) {
        case "success": return "fa-check-circle";
        case "error": return "fa-exclamation-circle";
        case "warning": return "fa-exclamation-triangle";
        default: return "fa-info-circle";
    }
}

// Enhanced loading state management
window.addEventListener("beforeunload", function() {
    // Reset button state if page is refreshed during loading
    if (mybut) {
        mybut.classList.remove("loading");
        mybut.disabled = false;
    }
});

// Smooth scrolling for result cards
function smoothScrollToResults() {
    const resultsSection = document.querySelector(".results-section");
    if (resultsSection) {
        resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// Intersection Observer for fade-in animations
if ('IntersectionObserver' in window) {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe result cards when they're added to the DOM
    document.addEventListener('DOMContentLoaded', () => {
        const resultCards = document.querySelectorAll('.result-card');
        resultCards.forEach(card => observer.observe(card));
    });
}

// Performance optimization: Debounce search input
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

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
    }
    
    // Escape to clear search
    if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        searchInput.blur();
    }
});

// Add CSS for enhanced interactions
const enhancedStyles = `
<style>
.error-shake {
    animation: shake 0.6s ease-in-out;
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.input-focused {
    transform: scale(1.02);
    transition: transform 0.2s ease;
}

.search-input.has-content {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.toast-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    border-left: 4px solid #3b82f6;
    z-index: 9999;
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: 350px;
}

.toast-notification.show {
    opacity: 1;
    transform: translateX(0);
}

.toast-success {
    border-left-color: #10b981;
}

.toast-error {
    border-left-color: #ef4444;
}

.toast-warning {
    border-left-color: #f59e0b;
}

.toast-content {
    display: flex;
    align-items: center;
    font-weight: 500;
    color: #374151;
}

.loading .btn-shine {
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    50% { left: 100%; }
    100% { left: 100%; }
}

.fade-in-visible {
    animation: fadeInUp 0.6s ease-out forwards;
}

/* Improved focus indicators */
.search-btn:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

.result-link:focus-visible,
.footer-link:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    border-radius: 4px;
}

/* Enhanced mobile interactions */
@media (max-width: 768px) {
    .toast-notification {
        right: 10px;
        left: 10px;
        max-width: none;
    }
}
</style>
`;

// Inject enhanced styles
document.head.insertAdjacentHTML('beforeend', enhancedStyles);

// Console welcome message
console.log(`
🚀 SenimSearcherX Bot Initialized!
📱 Enhanced UI/UX Features Loaded
🔍 Ready for Wikipedia searches
⌨️  Keyboard shortcuts: Ctrl+K (focus search), Escape (clear)
`);
