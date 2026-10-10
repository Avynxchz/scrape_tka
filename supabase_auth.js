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

// B9: Periksa parameter URL & mode tamu
(function checkModeFromUrl() {
  try {
    const params = new URLSearchParams(window.location.search);
    if (params.get('mode') === 'tamu') {
      sessionStorage.setItem('tka_mode', 'guest');
      localStorage.setItem('tka_guest_session', 'true');
    } else if (params.get('mode') === 'login') {
      sessionStorage.removeItem('tka_mode');
      localStorage.removeItem('tka_guest_session');
    }
  } catch (e) {}
})();

// Segera pulihkan sesi login dari perangkat ini tanpa menunggu loading CDN
(function restoreDeviceLoginImmediately() {
  try {
    const isGuest = sessionStorage.getItem('tka_mode') === 'guest' || localStorage.getItem('tka_guest_session') === 'true';
    if (isGuest) {
      window.TKA_USER = { name: 'Tamu', loggedIn: false };
      window.currentUser = null;
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          if (typeof updateLoginUI === 'function') updateLoginUI(false);
        });
      } else {
        if (typeof updateLoginUI === 'function') updateLoginUI(false);
      }
      return;
    }
    const saved = localStorage.getItem('tka_user');
    const isEverLoggedIn = localStorage.getItem('tka_device_logged_in') === 'true';
    const hasAuthToken = !!localStorage.getItem('tka_supabase_auth_token');
    // Hanya pulihkan tampilan jika token otentikasi benar-benar tersimpan di perangkat
    if (saved && isEverLoggedIn && hasAuthToken) {
      const u = JSON.parse(saved);
      if (u && u.loggedIn) {
        window.TKA_USER = u;
        window.currentUser = {
          email: u.email,
          user_metadata: { full_name: u.name, avatar_url: u.avatar }
        };
        // Update tampilan login segera setelah DOM siap
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            if (typeof updateLoginUI === 'function') updateLoginUI(true);
          });
        } else {
          if (typeof updateLoginUI === 'function') updateLoginUI(true);
        }
      }
    }
  } catch (e) {}
})();

async function initSupabase() {
  await loadSupabaseJS();
  supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      storageKey: 'tka_supabase_auth_token'
    }
  });
  
  // B9: Jangan pulihkan sesi login jika sedang dalam mode tamu
  const isGuest = sessionStorage.getItem('tka_mode') === 'guest' || localStorage.getItem('tka_guest_session') === 'true';
  if (isGuest) {
    currentUser = null;
    window.TKA_USER = { name: 'Tamu', loggedIn: false };
    window.currentUser = null;
    updateLoginUI(false);
    return;
  }

  // Cek session yang tersimpan di perangkat ini
  try {
    const { data: { session } } = await supabaseClient.auth.getSession();
    if (session && session.user) {
      currentUser = session.user;
      localStorage.setItem('tka_device_logged_in', 'true');
      await syncUserToDB(session.user);
      updateLoginUI(true);
      // Bersihkan hash OAuth jika masih ada di URL
      if (window.location.hash && (window.location.hash.includes('access_token=') || window.location.hash.includes('refresh_token='))) {
        try {
          const cleanUrl = window.location.pathname + window.location.search;
          window.history.replaceState(null, '', cleanUrl);
        } catch (e) {}
      }
    } else {
      // Jika session tidak ada di Supabase dan tidak ada token, jangan pertahankan status login palsu
      const hasAuthToken = !!localStorage.getItem('tka_supabase_auth_token');
      if (!hasAuthToken) {
        currentUser = null;
        window.TKA_USER = null;
        window.currentUser = null;
        localStorage.removeItem('tka_device_logged_in');
        localStorage.removeItem('tka_user');
        updateLoginUI(false);
      }
    }
  } catch (e) {
    console.warn('Gagal cek session:', e);
  }
  
  // Listen perubahan status otentikasi
  supabaseClient.auth.onAuthStateChange(async (event, session) => {
    if ((event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') && session) {
      currentUser = session.user;
      localStorage.setItem('tka_device_logged_in', 'true');
      await syncUserToDB(session.user);
      updateLoginUI(true);
      // Bersihkan hash OAuth dari URL setelah sukses diproses
      if (window.location.hash && (window.location.hash.includes('access_token=') || window.location.hash.includes('refresh_token='))) {
        try {
          const cleanUrl = window.location.pathname + window.location.search;
          window.history.replaceState(null, '', cleanUrl);
        } catch (e) {}
      }
    } else if (event === 'SIGNED_OUT') {
      currentUser = null;
      localStorage.removeItem('tka_device_logged_in');
      localStorage.removeItem('tka_supabase_auth_token');
      localStorage.removeItem('tka_user');
      updateLoginUI(false);
    }
  });
}

// Sumber kebenaran tunggal untuk token: supabase.auth.getSession().
// getSession() otomatis refresh token jika kedaluwarsa (autoRefreshToken: true).
async function getFreshToken() {
  try {
    if (typeof supabaseClient === 'undefined' || !supabaseClient) return null;
    const { data: { session } } = await supabaseClient.auth.getSession();
    return (session && session.access_token) ? session.access_token : null;
  } catch (e) { return null; }
}
// Paksa refresh token (dipakai saat server return 401).
async function refreshTokenNow() {
  try {
    if (typeof supabaseClient === 'undefined' || !supabaseClient) return null;
    const { data: { session }, error } = await supabaseClient.auth.refreshSession();
    if (error || !session) return null;
    return session.access_token || null;
  } catch (e) { return null; }
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
  sessionStorage.removeItem('tka_mode');
  localStorage.removeItem('tka_guest_session');
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

// Modal Konfirmasi Keluar (Estetik, Responsif Desktop & Mobile)
function showLogoutConfirmationModal() {
  const existing = document.getElementById('tkaLogoutModal');
  if (existing) existing.remove();

  const user = window.TKA_USER || (currentUser ? {
    name: currentUser.user_metadata?.full_name || currentUser.email,
    email: currentUser.email,
    avatar: currentUser.user_metadata?.avatar_url || ''
  } : null);

  const userName = user?.name || 'Siswa TKA';
  const userEmail = user?.email || 'Akun Google Terhubung';
  const userAvatar = user?.avatar || '';

  const modalOverlay = document.createElement('div');
  modalOverlay.id = 'tkaLogoutModal';
  modalOverlay.className = 'tka-logout-overlay';
  modalOverlay.style.cssText = `
    position: fixed; inset: 0; z-index: 9999999;
    display: flex; align-items: center; justify-content: center;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0; transition: opacity 0.25s ease-out;
    padding: 16px;
    box-sizing: border-box;
  `;

  modalOverlay.innerHTML = `
    <div class="tka-logout-card" style="
      background: #ffffff;
      color: #0f172a;
      width: 100%;
      max-width: 420px;
      border-radius: 24px;
      box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.35), 0 0 0 1px rgba(226, 232, 240, 0.8);
      padding: 24px 22px 20px 22px;
      transform: scale(0.92) translateY(10px);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    ">
      <!-- Icon & Close -->
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
        <div style="
          width: 48px; height: 48px; border-radius: 14px;
          background: #fef2f2; border: 1px solid #fee2e2;
          display: flex; align-items: center; justify-content: center;
          color: #ef4444; font-size: 24px;
        ">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
        </div>
        <button id="tkaLogoutCloseBtn" type="button" style="
          border: none; background: #f1f5f9; color: #64748b;
          width: 32px; height: 32px; border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          cursor: pointer; transition: all 0.15s; font-size: 14px;
        " title="Tutup">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Title & Message -->
      <h3 style="margin: 0 0 6px 0; font-size: 19px; font-weight: 700; color: #0f172a; line-height: 1.3;">
        Keluar dari Akun?
      </h3>
      <p style="margin: 0 0 16px 0; font-size: 13.5px; color: #64748b; line-height: 1.5;">
        Kamu yakin ingin keluar dari akun Google ini?
      </p>

      <!-- User Card Box -->
      <div style="
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 14px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 16px;
      ">
        ${userAvatar ? `
          <img src="${userAvatar}" alt="Avatar" style="
            width: 44px; height: 44px; border-radius: 50%;
            object-fit: cover; border: 2px solid #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08); flex-shrink: 0;
          ">
        ` : `
          <div style="
            width: 44px; height: 44px; border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: #ffffff; font-weight: 700; font-size: 16px;
            display: flex; align-items: center; justify-content: center; flex-shrink: 0;
          ">${userName.charAt(0).toUpperCase()}</div>
        `}
        <div style="min-width: 0; flex: 1;">
          <div style="font-weight: 700; font-size: 14px; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${userName}
          </div>
          <div style="font-size: 12px; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${userEmail}
          </div>
        </div>
        <span style="
          font-size: 10px; font-weight: 700; text-transform: uppercase;
          background: #e0e7ff; color: #4338ca; padding: 3px 7px;
          border-radius: 6px; letter-spacing: 0.5px; flex-shrink: 0;
        ">Google</span>
      </div>

      <!-- Info Box Kuota -->
      <div style="
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-radius: 14px;
        padding: 11px 13px;
        display: flex; gap: 10px; align-items: flex-start;
        margin-bottom: 20px;
      ">
        <i class="fa-solid fa-circle-info" style="color: #d97706; font-size: 15px; margin-top: 2px;"></i>
        <div style="font-size: 12.5px; color: #92400e; line-height: 1.45;">
          Sesi belajarmu akan beralih ke mode <strong>Tamu (5 tanya/hari)</strong>. Kamu bisa masuk kembali kapan saja untuk menikmati 25 tanya/hari.
        </div>
      </div>

      <!-- Actions Button -->
      <div style="display: flex; gap: 10px;">
        <button id="tkaLogoutCancelBtn" type="button" style="
          flex: 1; height: 44px;
          background: #f1f5f9; color: #334155;
          border: 1px solid #cbd5e1; border-radius: 12px;
          font-size: 13.5px; font-weight: 600;
          cursor: pointer; transition: all 0.15s;
        ">
          Batal
        </button>
        <button id="tkaLogoutConfirmBtn" type="button" style="
          flex: 1.2; height: 44px;
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: #ffffff; border: none; border-radius: 12px;
          font-size: 13.5px; font-weight: 600;
          cursor: pointer; transition: all 0.15s;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
          display: flex; align-items: center; justify-content: center; gap: 8px;
        ">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
          <span>Keluar Akun</span>
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modalOverlay);

  // Animate in
  requestAnimationFrame(() => {
    modalOverlay.style.opacity = '1';
    const card = modalOverlay.querySelector('.tka-logout-card');
    if (card) {
      card.style.transform = 'scale(1) translateY(0)';
    }
  });

  const closeModal = () => {
    modalOverlay.style.opacity = '0';
    const card = modalOverlay.querySelector('.tka-logout-card');
    if (card) {
      card.style.transform = 'scale(0.92) translateY(10px)';
    }
    setTimeout(() => {
      if (modalOverlay.parentNode) modalOverlay.parentNode.removeChild(modalOverlay);
    }, 220);
  };

  const closeBtn = modalOverlay.querySelector('#tkaLogoutCloseBtn');
  const cancelBtn = modalOverlay.querySelector('#tkaLogoutCancelBtn');
  const confirmBtn = modalOverlay.querySelector('#tkaLogoutConfirmBtn');

  if (closeBtn) closeBtn.onclick = closeModal;
  if (cancelBtn) cancelBtn.onclick = closeModal;

  modalOverlay.onclick = (e) => {
    if (e.target === modalOverlay) closeModal();
  };

  const onKey = (e) => {
    if (e.key === 'Escape') {
      closeModal();
      document.removeEventListener('keydown', onKey);
    }
  };
  document.addEventListener('keydown', onKey);

  if (confirmBtn) {
    confirmBtn.onclick = async () => {
      confirmBtn.disabled = true;
      confirmBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> <span>Mengeluarkan...</span>';
      // T3b: Simpan progres terakhir ke server sebelum logout
      if (typeof saveProgressToServer === 'function') {
        try { await saveProgressToServer(); } catch (e) {}
      }
      try {
        await supabaseClient.auth.signOut();
      } catch (e) {}
      // B9: Set status tamu eksplisit saat logout agar tidak auto login kembali
      sessionStorage.setItem('tka_mode', 'guest');
      localStorage.setItem('tka_guest_session', 'true');
      // BUGFIX (10 Okt 2026 - T3b): bersihkan SEMUA data akun & progres agar tidak bocor ke user berikutnya
      try {
        localStorage.removeItem('tka_supabase_auth_token');
        localStorage.removeItem('tka_device_logged_in');
        localStorage.removeItem('tka_user');
        localStorage.removeItem('tka_progress');
        localStorage.removeItem('tka_progress_owner');
        // Hapus juga semua paket tersimpan (tka_answers_*, tka_ragu_*, tka_finished_*, tka_checked_*, tka_timer_remaining_*, sb-*)
        for (var i = localStorage.length - 1; i >= 0; i--) {
          var k = localStorage.key(i);
          if (!k) continue;
          if (k.indexOf('tka_answers_') === 0 || k.indexOf('tka_ragu_') === 0 || 
              k.indexOf('tka_finished_') === 0 || k.indexOf('tka_checked_') === 0 || 
              k.indexOf('tka_timer_remaining_') === 0 || k.indexOf('sb-') === 0) {
            localStorage.removeItem(k);
          }
        }
      } catch (e2) {}
      currentUser = null;
      window.TKA_USER = { name: 'Tamu', loggedIn: false };
      window.currentUser = null;
      updateLoginUI(false);
      location.reload();
    };
  }
}
window.showLogoutConfirmationModal = showLogoutConfirmationModal;

// Logout langsung
async function logout() {
  showLogoutConfirmationModal();
}

// Update UI berdasarkan status login
function updateLoginUI(isLoggedIn) {
  const btn = document.getElementById('loginBtn');
  const userInfo = document.getElementById('userInfo');
  const avatarBtn = document.getElementById('headerAvatarBtn') || document.querySelector('.stitch-header-actions .stitch-avatar');
  
  const effectiveUser = currentUser || window.currentUser;
  if (isLoggedIn && effectiveUser) {
    let cleanName = effectiveUser.user_metadata?.full_name || effectiveUser.user_metadata?.name || '';
    if (!cleanName && effectiveUser.email) {
      const prefix = effectiveUser.email.split('@')[0] || '';
      cleanName = prefix ? (prefix.charAt(0).toUpperCase() + prefix.slice(1)) : '';
    }
    const userName = cleanName || 'Siswa TKA';
    const avatarUrl = effectiveUser.user_metadata?.avatar_url || '';
    
    // Simpan global biar bisa diakses semua bagian app
    window.TKA_USER = {
      name: userName,
      email: effectiveUser.email,
      avatar: avatarUrl,
      loggedIn: true
    };
    try {
      localStorage.setItem('tka_user', JSON.stringify(window.TKA_USER));
      localStorage.setItem('tka_device_logged_in', 'true');
    } catch (e) {}
    
    if (btn) btn.style.display = 'none';
    if (avatarBtn) avatarBtn.style.display = 'none'; // Sembunyikan avatar default agar tidak bertumpuk/dobel di header
    
    if (userInfo) {
      userInfo.style.display = 'flex';
      userInfo.innerHTML = `
        <img src="${avatarUrl}" onclick="if(typeof homeShowPanel==='function')homeShowPanel('akun')"
             class="user-avatar-img"
             title="Buka Akun (${userName})" alt="Avatar">
        <span class="user-name" onclick="if(typeof homeShowPanel==='function')homeShowPanel('akun')"
              title="${userName}">${userName}</span>
        <button onclick="showLogoutConfirmationModal()" class="user-logout-btn" type="button" title="Keluar dari akun">Keluar</button>
      `;
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
      localStorage.removeItem('tka_device_logged_in');
    } catch (e) {}
    if (btn) btn.style.display = 'inline-flex';
    if (avatarBtn) avatarBtn.style.display = 'grid';
    if (userInfo) userInfo.style.display = 'none';
    window.dispatchEvent(new CustomEvent('tka-logout'));
  }
}

// Ambil info user (untuk AI greeting dll)
function getTKAUser() {
  const isGuest = sessionStorage.getItem('tka_mode') === 'guest' || localStorage.getItem('tka_guest_session') === 'true';
  if (isGuest) {
    return { name: 'Tamu', loggedIn: false };
  }
  if (window.TKA_USER && window.TKA_USER.loggedIn) return window.TKA_USER;
  try {
    const saved = localStorage.getItem('tka_user');
    const hasAuthToken = !!localStorage.getItem('tka_supabase_auth_token');
    if (saved && hasAuthToken) {
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
