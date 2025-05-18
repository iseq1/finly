document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.getElementById('toggleConfirmedPassword');
    const passwordInput = document.getElementById('confirmed_password');

    togglePassword.addEventListener('mouseenter', function() {
        passwordInput.setAttribute('type', 'text');
    });

    togglePassword.addEventListener('mouseleave', function() {
        passwordInput.setAttribute('type', 'password');
    });

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    });
});