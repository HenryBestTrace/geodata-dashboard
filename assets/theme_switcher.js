
if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    applyTheme: function(themeData) {
        const theme = themeData.current_theme;
        const body = document.body;
        
        // Apply theme class to body
        if (theme === 'dark') {
            body.classList.add('dark-theme');
            body.classList.remove('light-theme');
        } else {
            body.classList.add('light-theme');
            body.classList.remove('dark-theme');
        }
        
        // Set data attribute for CSS targeting
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update color scheme meta tag for browser UI
        const metaTag = document.querySelector('meta[name="color-scheme"]');
        if (metaTag) {
            metaTag.setAttribute('content', theme);
        } else {
            const newMeta = document.createElement('meta');
            newMeta.name = 'color-scheme';
            newMeta.content = theme;
            document.head.appendChild(newMeta);
        }
        
        // Save theme preference in localStorage
        localStorage.setItem('dashboardTheme', theme);
        
        // Try to update iframes with theme preference
        try {
            const iframe = document.getElementById('dashboard-iframe');
            if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage({ type: 'themeChange', theme: theme }, '*');
            }
        } catch (e) {
            console.log('Could not communicate with iframe:', e);
        }
        
        return theme;
    },
    
    // Function to initialize theme from saved preference
    initTheme: function() {
        const savedTheme = localStorage.getItem('dashboardTheme') || 'light';
        
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        }
        
        return savedTheme;
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.dash_clientside.clientside.initTheme();
        
        // Initialize switch if already saved as dark
        const savedTheme = localStorage.getItem('dashboardTheme');
        if (savedTheme === 'dark') {
            const switches = document.querySelectorAll('#theme-switch input[type="checkbox"]');
            if (switches.length > 0) {
                switches[0].checked = true;
            }
        }
    }, 100);
});
            