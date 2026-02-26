document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(toast => {
        // Wait 3 seconds (3000 milliseconds)
        setTimeout(() => {
            toast.classList.add('hide'); // Triggers the fade-out animation
            
            // Wait for the animation to finish (500ms), then remove the HTML element
            setTimeout(() => {
                toast.remove();
            }, 500); 
        }, 3000); 
    });
});