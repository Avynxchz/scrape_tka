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
    if (btn) btn.style.display = 'none';
    if (userInfo) {
      userInfo.style.display = 'flex';
      userInfo.innerHTML = `
        <img src="${currentUser.user_metadata?.avatar_url || ''}" 
             style="width:32px;height:32px;border-radius:50%" alt="">
        <span>${currentUser.user_metadata?.full_name || currentUser.email}</span>
        <button onclick="logout()" style="margin-left:8px">Keluar</button>
      `;
    }
    // Update quota: logged-in dapat 25/hari
    if (typeof updateTutorQuotaUI === 'function') {
      updateTutorQuotaUI({ remaining: 25, daily_limit: 25, tier: 'free' });
    }
  } else {
    if (btn) btn.style.display = 'block';
    if (userInfo) userInfo.style.display = 'none';
  }
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
