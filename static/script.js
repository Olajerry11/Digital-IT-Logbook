document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Smooth fade-in for forms and main containers
    const containers = document.querySelectorAll("form, .log-container");
    containers.forEach(container => {
        container.style.opacity = "0";
        container.style.transform = "translateY(20px)";
        container.style.transition = "all 0.6s cubic-bezier(0.25, 0.8, 0.25, 1)";
        
        setTimeout(() => {
            container.style.opacity = "1";
            container.style.transform = "translateY(0)";
        }, 50);
    });

    // 2. Staggered fade-in animation (Restricted to log entries only)
    const logItems = document.querySelectorAll(".log-container li");
    logItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add("animate-in");
        }, 100 + (index * 120));
    });

    // 3. Tactile button click effect
    const buttons = document.querySelectorAll("button, .secondary-btn, .edit-btn, .delete-btn");
    buttons.forEach(button => {
        button.addEventListener("mousedown", function() {
            this.style.transform = "scale(0.95)";
        });
        button.addEventListener("mouseup", function() {
            this.style.transform = "translateY(-2px)";
        });
        button.addEventListener("mouseleave", function() {
            this.style.transform = "";
        });
    });

    // 4. Professional Flatpickr Calendar Initialization
    const dateInput = document.getElementById('date');
    if (dateInput) {
        flatpickr(dateInput, {
            dateFormat: "Y-m-d",        
            altInput: true,             
            altFormat: "F j, Y",        
            defaultDate: "today",       
            disableMobile: "true"       
        });
    }

    // 5. Password Visibility Toggle
    const togglePasswords = document.querySelectorAll('.toggle-password');
    togglePasswords.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            this.style.color = type === 'text' ? 'var(--accent-gold)' : '#aaa';
            this.style.opacity = type === 'text' ? '1' : '0.6';
        });
    });

    // 6. Live Password Strength Checker
    const regPassword = document.getElementById('password');
    if (regPassword) {
        regPassword.addEventListener('input', function() {
            const val = this.value;
            
            const reqLength = document.getElementById('req-length');
            const reqLower = document.getElementById('req-lower');
            const reqUpper = document.getElementById('req-upper');
            const reqNumber = document.getElementById('req-number');
            const reqSpecial = document.getElementById('req-special');
            
            val.length >= 8 ? reqLength.classList.add('valid') : reqLength.classList.remove('valid');
            /[a-z]/.test(val) ? reqLower.classList.add('valid') : reqLower.classList.remove('valid');
            /[A-Z]/.test(val) ? reqUpper.classList.add('valid') : reqUpper.classList.remove('valid');
            /[0-9]/.test(val) ? reqNumber.classList.add('valid') : reqNumber.classList.remove('valid');
            /[@$!%*?&]/.test(val) ? reqSpecial.classList.add('valid') : reqSpecial.classList.remove('valid');
        });
    }
});