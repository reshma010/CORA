document.addEventListener('DOMContentLoaded', function () {
    console.log('Password reset form loaded');

    const form = document.getElementById('resetForm');
    const passwordInput = document.getElementById('passwordInput');
    const confirmPasswordInput = document.getElementById('confirmPasswordInput');
    const submitButton = document.getElementById('submitBtn');
    const errorDiv = document.getElementById('errorMessage');
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const charCounter = document.getElementById('charCounter');

    console.log('Elements found:', {
        form: !!form,
        passwordInput: !!passwordInput,
        confirmPasswordInput: !!confirmPasswordInput,
        submitButton: !!submitButton,
        errorDiv: !!errorDiv,
        togglePassword: !!togglePassword,
        toggleConfirmPassword: !!toggleConfirmPassword,
        charCounter: !!charCounter
    });

    if (!passwordInput || !confirmPasswordInput || !submitButton) {
        console.error('Critical elements not found');
        return;
    }

    // Password toggle functionality
    function setupPasswordToggle(toggleButton, passwordInput) {
        if (!toggleButton || !passwordInput) {
            console.error('Toggle button or password input not found');
            return;
        }

        toggleButton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Toggle button clicked for:', passwordInput.name);
            
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            toggleButton.textContent = isPassword ? 'Hidden' : 'Show';
            
            console.log('Password visibility toggled to:', passwordInput.type);
        });
    }

    setupPasswordToggle(togglePassword, passwordInput);
    setupPasswordToggle(toggleConfirmPassword, confirmPasswordInput);

    // Password validation requirements
    const requirements = {
        length: { min: 10, max: 20 },
        uppercase: /[A-Z]/,
        lowercase: /[a-z]/,
        number: /[0-9]/,
        special: /[!@#$%^&*(),.?":{}|<>]/
    };

    function updatePasswordRequirements(password) {
        console.log('Updating requirements for password:', password ? `${password.length} characters` : 'empty');

        const checks = {
            length: password.length >= requirements.length.min && password.length <= requirements.length.max,
            upper: requirements.uppercase.test(password),
            lower: requirements.lowercase.test(password),
            number: requirements.number.test(password),
            special: requirements.special.test(password)
        };

        console.log('Validation checks:', {
            length: `${password.length} chars (need 10-20): ${checks.length}`,
            upper: `uppercase found: ${checks.upper}`,
            lower: `lowercase found: ${checks.lower}`,
            number: `number found: ${checks.number}`,
            special: `special char found: ${checks.special}`
        });

        // Update requirement indicators
        Object.keys(checks).forEach(key => {
            const element = document.getElementById(`req-${key}`);
            if (element) {
                element.className = `req-item ${checks[key] ? 'req-satisfied' : 'req-pending'}`;
            }
        });

        // Update character counter
        if (charCounter) {
            const currentLength = password.length;
            charCounter.textContent = `${currentLength}/${requirements.length.max}`;
            
            charCounter.className = 'char-counter';
            if (currentLength > requirements.length.max) {
                charCounter.classList.add('max-reached');
            } else if (currentLength >= requirements.length.max - 2) {
                charCounter.classList.add('warning');
            } else if (currentLength >= requirements.length.min) {
                charCounter.classList.add('good');
            }
        }

        return Object.values(checks).every(check => check);
    }

    function validatePasswordMatch(password, confirmPassword) {
        const match = password === confirmPassword && password.length > 0;
        console.log('Password match check:', match);
        
        const matchElement = document.getElementById('req-match');
        if (matchElement) {
            matchElement.className = `req-item ${match ? 'req-satisfied' : 'req-pending'}`;
        }
        
        return match;
    }

    function isFormValid() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        const passwordValid = updatePasswordRequirements(password);
        const matchValid = validatePasswordMatch(password, confirmPassword);
        const isValid = passwordValid && matchValid;
        
        console.log('Form validation:', { passwordValid, matchValid, isValid });
        
        // Update submit button state
        if (submitButton) {
            submitButton.disabled = !isValid;
            console.log('Submit button disabled:', submitButton.disabled);
        }
        
        return isValid;
    }

    // Add event listeners for real-time validation
    passwordInput.addEventListener('input', function () {
        console.log('Password input changed, validating...');
        isFormValid();
    });

    confirmPasswordInput.addEventListener('input', function () {
        console.log('Confirm password input changed, validating...');
        isFormValid();
    });

    // Form submission handler
    if (form) {
        form.addEventListener('submit', function (e) {
            console.log('Form submission attempted');
            
            if (!isFormValid()) {
                e.preventDefault();
                console.log('Form submission blocked - validation failed');
                
                if (errorDiv) {
                    errorDiv.textContent = 'Please ensure all password requirements are met.';
                    errorDiv.style.display = 'block';
                }
                return false;
            }
            
            console.log('Form submission allowed - validation passed');
            
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        });
    }

    // Initial validation check
    console.log('Running initial validation check');
    isFormValid();

    console.log('Password reset form initialization complete');
});