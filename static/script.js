document.addEventListener("DOMContentLoaded", () => {
    // Select all the list items on the logs page
    const entries = document.querySelectorAll("li");
    
    entries.forEach((entry, index) => {
        // Start them invisible and slightly pushed down
        entry.style.opacity = "0";
        entry.style.transform = "translateY(20px)";
        
        // Add a delay based on their index so they cascade in sequentially
        entry.style.transition = `all 0.5s ease-out ${index * 0.15}s`;

        // Trigger the animation shortly after the page loads
        setTimeout(() => {
            entry.style.opacity = "1";
            entry.style.transform = "translateY(0)";
        }, 50);
    });
});