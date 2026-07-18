// Sidebar Accordion + Active Link Highlighting
(function () {
    function getCurrentPath() {
        let path = window.location.pathname;
        // Remove trailing slash for consistent comparison
        if (path !== '/' && path.endsWith('/')) {
            path = path.slice(0, -1);
        }
        return path;
    }

    function normalizeUrl(url) {
        if (url === '#') return url;
        // Remove domain if present (use relative path)
        let path = url;
        try {
            const urlObj = new URL(url, window.location.origin);
            path = urlObj.pathname;
        } catch (e) { }
        if (path !== '/' && path.endsWith('/')) {
            path = path.slice(0, -1);
        }
        return path;
    }

    function initAccordion() {
        const groups = document.querySelectorAll('.sidebar-group');
        const currentPath = getCurrentPath();
        let activeGroupFound = false;

        groups.forEach(group => {
            const header = group.querySelector('.sidebar-group-header');
            const content = group.querySelector('.sidebar-group-content');
            const links = group.querySelectorAll('.sidebar-link:not(.locked)');
            let groupContainsActive = false;

            // Check if any link in this group matches the current path
            links.forEach(link => {
                const linkPath = normalizeUrl(link.getAttribute('data-url') || link.getAttribute('href'));
                if (linkPath === currentPath) {
                    groupContainsActive = true;
                    // Highlight the active link
                    link.classList.add('active', 'bg-blue-50', 'font-semibold');
                    const isRTL = document.documentElement.dir === 'rtl';
                    const borderClass = isRTL ? 'border-r-4' : 'border-l-4';
                    link.classList.add(borderClass, 'border-blue-500');
                } else {
                    link.classList.remove('active', 'bg-blue-50', 'border-l-4', 'border-r-4', 'border-blue-500', 'font-semibold');
                }
            });

            // Initially, expand only the group that contains the active link
            if (groupContainsActive) {
                content.style.display = 'block';
                header.querySelector('i').classList.remove('fa-chevron-right');
                header.querySelector('i').classList.add('fa-chevron-down');
                activeGroupFound = true;
            } else {
                content.style.display = 'none';
                header.querySelector('i').classList.remove('fa-chevron-down');
                header.querySelector('i').classList.add('fa-chevron-right');
            }

            // Toggle on header click
            header.removeEventListener('click', toggleHandler);
            header.addEventListener('click', toggleHandler);
        });

        // If no active group found (e.g., home page), optionally expand the first group or none.
        // We choose to expand none – user can click to open.
    }

    function toggleHandler(event) {
        const header = event.currentTarget;
        const group = header.closest('.sidebar-group');
        const content = group.querySelector('.sidebar-group-content');
        const icon = header.querySelector('i');
        const isOpen = content.style.display !== 'none';
        if (isOpen) {
            content.style.display = 'none';
            if (icon) {
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-right');
            }
        } else {
            content.style.display = 'block';
            if (icon) {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-down');
            }
        }
    }

    function reapplyActiveLink() {
        const currentPath = getCurrentPath();
        const links = document.querySelectorAll('.sidebar-link:not(.locked)');
        links.forEach(link => {
            const linkPath = normalizeUrl(link.getAttribute('data-url') || link.getAttribute('href'));
            if (linkPath === currentPath) {
                link.classList.add('active', 'bg-blue-50', 'font-semibold');
                const isRTL = document.documentElement.dir === 'rtl';
                const borderClass = isRTL ? 'border-r-4' : 'border-l-4';
                link.classList.add(borderClass, 'border-blue-500');
            } else {
                link.classList.remove('active', 'bg-blue-50', 'border-l-4', 'border-r-4', 'border-blue-500', 'font-semibold');
            }
        });
    }

    // Initial load
    document.addEventListener('DOMContentLoaded', () => {
        initAccordion();
        reapplyActiveLink();
    });

    // After HTMX swaps (the content area changes, but the sidebar stays)
    document.body.addEventListener('htmx:afterSwap', (evt) => {
        // Reapply active link highlighting – the URL may have changed
        reapplyActiveLink();
        // Note: the accordion groups remain as they were (user may have opened/closed some).
        // If you want to also re-collapse to only the new active group, call initAccordion() again.
        // But that would reset the user's manual toggles. Usually not desired.
        // We'll just reapply the active link style.
    });

    // Also handle when HTX pushes a new URL (without full page reload)
    window.addEventListener('popstate', () => {
        reapplyActiveLink();
    });
})();