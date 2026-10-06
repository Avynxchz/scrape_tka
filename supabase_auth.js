// Supabase Auth untuk TKA Master
// Login Google + manajemen user tier

const SUPABASE_URL = 'https://auhqgzrrgvjbfvzvayzg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1aHFnenJyZ3ZqYmZ2enZheXpnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEyNzUwNDgsImV4cCI6MjEwNjg1MTA0OH0.lthMo0A1QcAGOnp4NJ65-FDsP7yOCpA-OikA-Ei1gqY';

// Load Supabase JS dari CDN
function loadSupabaseJS() {
  return new Promise((resolve, reject) => {
    if (window.supabase) { resolve(); return; }
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

let supabaseClient = null;
let currentUser = null;

async function initSupabase() {
  await loadSupabaseJS();
  supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  
  // Cek session yang tersimpan
  const { data: { session } } = await supabaseClient.auth.getSession();
  if (session) {
    currentUser = session.user;
    await syncUserToDB(session.user);
    updateLoginUI(true);
  }
  
  // Listen perubahan auth
  supabaseClient.auth.onAuthStateChange(async (event, session) => {
    if (event === 'SIGNED_IN' && session) {
      currentUser = session.user;
      await syncUserToDB(session.user);
      updateLoginUI(true);
    } else if (event === 'SIGNED_OUT') {
      currentUser = null;
      updateLoginUI(false);
    }
  });
}

// Simpan/update user ke database
async function syncUserToDB(user) {
  const { data, error } = await supabaseClient
    .from('users')
    .upsert({
      id: user.id,
      email: user.email,
      name: user.user_metadata?.full_name || user.email,
      avatar_url: user.user_metadata?.avatar_url,
      last_login_at: new Date().toISOString()
    }, { onConflict: 'id' });
  
  if (error) console.error('Sync user error:', error);
  return data;
}

// Login dengan Google
async function loginWithGoogle() {
  if (!supabaseClient) {
    alert('Sistem login belum siap, coba lagi sebentar...');
    return;
  }
  const { error } = await supabaseClient.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin + '/app'
    }
  });
  if (error) {
    alert('Login gagal: ' + error.message);
  }
}

// Logout
async function logout() {
  await supabaseClient.auth.signOut();
  currentUser = null;
  updateLoginUI(false);
  location.reload();
}

// Update UI berdasarkan status login
function updateLoginUI(isLoggedIn) {
  const btn = document.getElementById('loginBtn');
  const userInfo = document.getElementById('userInfo');
  
  if (isLoggedIn && currentUser) {
    const userName = currentUser.user_metadata?.full_name || currentUser.email;
    const avatarUrl = currentUser.user_metadata?.avatar_url || '';
    
    // Simpan global biar bisa diakses semua bagian app
    window.TKA_USER = {
      name: userName,
      email: currentUser.email,
      avatar: avatarUrl,
      loggedIn: true
    };
    try {
      localStorage.setItem('tka_user', JSON.stringify(window.TKA_USER));
    } catch (e) {}
    
    if (btn) btn.style.display = 'none';
    if (userInfo) {
      userInfo.style.display = 'flex';
      userInfo.style.alignItems = 'center';
      userInfo.style.gap = '6px';
      userInfo.style.maxWidth = '180px';
      userInfo.style.overflow = 'hidden';
      // Compact: avatar + nama pendek (truncate) + tombol keluar kecil
      // Di HP nama disembunyikan biar header nggak rusak
      const shortName = userName.length > 12 ? userName.substring(0, 12) + '…' : userName;
      userInfo.innerHTML = `
        <img src="${avatarUrl}"
             style="width:28px;height:28px;border-radius:50%;flex-shrink:0" alt="">
        <span class="user-name" style="font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:80px">${shortName}</span>
        <button onclick="logout()" style="flex-shrink:0;font-size:11px;padding:4px 8px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer">Keluar</button>
      `;
      // Sembunyikan nama di layar kecil via CSS
      const style = document.createElement('style');
      style.textContent = '@media (max-width: 640px) { #userInfo .user-name { display: none !important; } #userInfo { max-width: 90px !important; } }';
      if (!document.getElementById('userInfo-mobile-css')) {
        style.id = 'userInfo-mobile-css';
        document.head.appendChild(style);
      }
    }
    // Update quota: logged-in dapat 25/hari — sinkron ke semua tampilan
    const quotaData = { remaining: 25, daily_limit: 25, tier: 'free', is_logged_in: true };
    if (typeof updateTutorQuotaUI === 'function') {
      updateTutorQuotaUI(quotaData);
    }
    // Trigger event biar bagian lain bisa update
    window.dispatchEvent(new CustomEvent('tka-login', { detail: window.TKA_USER }));
  } else {
    window.TKA_USER = { name: 'Tamu', loggedIn: false };
    try {
      localStorage.removeItem('tka_user');
    } catch (e) {}
    if (btn) btn.style.display = 'block';
    if (userInfo) userInfo.style.display = 'none';
    window.dispatchEvent(new CustomEvent('tka-logout'));
  }
}

// Ambil info user (untuk AI greeting dll)
function getTKAUser() {
  if (window.TKA_USER) return window.TKA_USER;
  try {
    const saved = localStorage.getItem('tka_user');
    if (saved) {
      window.TKA_USER = JSON.parse(saved);
      return window.TKA_USER;
    }
  } catch (e) {}
  return { name: 'Tamu', loggedIn: false };
}

// Kirim feedback/rating
async function submitFeedback(rating, message) {
  const { error } = await supabaseClient
    .from('feedback')
    .insert({
      user_id: currentUser?.id || null,
      email: currentUser?.email || 'guest',
      rating: rating,
      message: message
    });
  return !error;
}

// Kirim bug report
async function submitBugReport(title, description) {
  const { error } = await supabaseClient
    .from('bug_reports')
    .insert({
      user_id: currentUser?.id || null,
      email: currentUser?.email || 'guest',
      title: title,
      description: description,
      page_url: window.location.href
    });
  return !error;
}

// Init saat halaman dimuat
document.addEventListener('DOMContentLoaded', initSupabase);
