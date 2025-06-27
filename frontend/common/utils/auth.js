// utils/auth.js
function isLoggedIn() {
    return document.cookie.includes('access_token');
} 