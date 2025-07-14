// ===========================================
// SIDEBAR TOGGLE FUNCTIONALITY
// ===========================================
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');

            // Close sidebar when clicking outside on mobile
            if (window.innerWidth <= 768) {
                document.addEventListener('click', function (e) {
                    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                        sidebar.classList.remove('active');
                    }
                });
            }
        });
    }

    // Handle window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});

// ===========================================
// SMOOTH ANIMATIONS
// ===========================================
function addSmoothAnimations() {
    // Add entrance animations to cards
    const cards = document.querySelectorAll('.book-card, .post-item');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    cards.forEach((card) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
}

// ===========================================
// SEARCH FUNCTIONALITY
// ===========================================
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', function () {
            const query = searchInput.value.trim();
            if (query) {
                // Implement search functionality
                console.log('Searching for:', query);
                // You can add AJAX search here
            }
        });

        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });
    }
}

// ===========================================
// BOOK CARD INTERACTIONS
// ===========================================
function initializeBookCards() {
    const bookCards = document.querySelectorAll('.book-card');

    bookCards.forEach((card) => {
        card.addEventListener('click', function () {
            const bookId = this.dataset.bookId;
            if (bookId) {
                // Navigate to book detail page
                window.location.href = `/book/${bookId}`;
            }
        });

        // Add hover effects
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// ===========================================
// POST INTERACTIONS
// ===========================================
function initializePostItems() {
    const postItems = document.querySelectorAll('.post-item');

    postItems.forEach((item) => {
        item.addEventListener('click', function () {
            const postId = this.dataset.postId;
            if (postId) {
                window.location.href = `/post/${postId}`;
            }
        });
    });
}

// ===========================================
// FILTER TABS
// ===========================================
function initializeFilterTabs() {
    const filterTabs = document.querySelectorAll('.filter-tab');

    filterTabs.forEach((tab) => {
        tab.addEventListener('click', function (e) {
            e.preventDefault();

            // Remove active class from all tabs
            filterTabs.forEach((t) => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Get filter value
            const filter = this.dataset.filter;

            // Filter books/posts based on category
            filterContent(filter);
        });
    });
}

function filterContent(filter) {
    const items = document.querySelectorAll('.book-card, .post-item');

    items.forEach((item) => {
        if (filter === 'all' || item.dataset.category === filter) {
            item.style.display = 'block';
            item.style.opacity = '1';
        } else {
            item.style.display = 'none';
            item.style.opacity = '0';
        }
    });
}

// ===========================================
// LOADING ANIMATIONS
// ===========================================
function showLoading() {
    const loadingHTML = `
        <div class="loading-spinner text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">로딩 중...</p>
        </div>
    `;

    return loadingHTML;
}

// ===========================================
// TOAST NOTIFICATIONS
// ===========================================
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();

    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        this.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}분 전`;
    }

    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}시간 전`;
    }

    // Less than 1 week
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days}일 전`;
    }

    // Default format
    return date.toLocaleDateString('ko-KR');
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// ===========================================
// INITIALIZE ALL FEATURES
// ===========================================
document.addEventListener('DOMContentLoaded', function () {
    addSmoothAnimations();
    initializeSearch();
    initializeBookCards();
    initializePostItems();
    initializeFilterTabs();

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>처리 중...';
                submitBtn.disabled = true;
            }
        });
    });

    console.log('🎨 New design system initialized successfully!');
});
