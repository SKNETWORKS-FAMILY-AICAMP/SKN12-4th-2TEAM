// common/components/navbar.js
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

async function loadNavbar() {
  const API_BASE = '';
  const navbarDiv = document.getElementById('navbar');
  const resp = await fetch('/common/components/navbar.html');
  const html = await resp.text();
  navbarDiv.innerHTML = html;

  // 서버에 실제 인증 상태 확인
  let isLoggedIn = false;
  try {
    const res = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' });
    isLoggedIn = res.ok;
  } catch (e) {
    isLoggedIn = false;
  }

  const menu = document.getElementById('navbar-menu');
  const path = window.location.pathname;
  menu.innerHTML = `
    <a href="/index.html"${path === '/' || path.endsWith('/index.html') ? ' class="active"' : ''}>MAIN</a>
    <a href="/chatbot.html"${path.endsWith('/chatbot.html') ? ' class="active"' : ''}>CHATBOT</a>
    <a href="/mypage.html"${path.endsWith('/mypage.html') ? ' class="active"' : ''}>MYPAGE</a>
    ${
      isLoggedIn
        ? '<a href="#" id="logout-btn">LOGOUT</a>'
        : `<a href="/login.html"${path.endsWith('/login.html') ? ' class="active"' : ''}>LOGIN</a>`
    }
  `;

  // 로그아웃 버튼 이벤트
  if (isLoggedIn) {
    document.getElementById('logout-btn').addEventListener('click', async (e) => {
      e.preventDefault();
      await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
      window.location.href = '/index.html';
    });
  }
}
window.addEventListener('DOMContentLoaded', loadNavbar); 