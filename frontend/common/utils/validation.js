// utils/validation.js
function checkPasswordRule(pw) {
    if (pw.length < 8) return false;
    let types = 0;
    if (/[A-Za-z]/.test(pw)) types++;
    if (/[0-9]/.test(pw)) types++;
    if (/[^A-Za-z0-9]/.test(pw)) types++;
    return types >= 2;
} 