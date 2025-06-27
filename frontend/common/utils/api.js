// utils/api.js
async function apiFetch(url, options) {
    const res = await fetch(url, options);
    let data;
    try {
        data = await res.json();
    } catch (e) {
        data = {};
    }
    if (!res.ok) throw new Error(data.detail || 'API Error');
    return data;
} 