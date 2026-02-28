document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (!themeToggle) return;

    themeToggle.addEventListener('click', (e) => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const nextTheme = isDark ? 'light' : 'dark';

        // Save to local storage
        localStorage.setItem('theme', nextTheme);

        // Fallback for browsers that don't support view transitions
        if (!document.startViewTransition) {
            document.documentElement.setAttribute('data-theme', nextTheme);
            return;
        }

        // Get click coordinates for the circle expansion center
        const x = e.clientX;
        const y = e.clientY;

        // Calculate maximum radius for the clip-path
        const endRadius = Math.hypot(
            Math.max(x, window.innerWidth - x),
            Math.max(y, window.innerHeight - y)
        );

        // Start the cross-document view transition
        const transition = document.startViewTransition(() => {
            document.documentElement.setAttribute('data-theme', nextTheme);
        });

        // Add the custom circular clip-path animation
        transition.ready.then(() => {
            document.documentElement.animate(
                {
                    clipPath: [
                        `circle(0px at ${x}px ${y}px)`,
                        `circle(${endRadius}px at ${x}px ${y}px)`
                    ]
                },
                {
                    duration: 600,
                    easing: 'ease-in-out',
                    pseudoElement: '::view-transition-new(root)',
                }
            );
        });
    });
});
