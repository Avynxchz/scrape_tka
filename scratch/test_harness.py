"""
Test Harness TKA Master untuk Mobile Playwright (390x844 + Touch)
Mendukung pengujian lokal (http://127.0.0.1:8080) dan preview (https://tka-master-preview.up.railway.app)
"""

import os
import json
import time
from playwright.sync_api import sync_playwright

LOCAL_URL = os.environ.get("TKA_LOCAL_URL", "http://127.0.0.1:8080")
PREVIEW_URL = os.environ.get("TKA_PREVIEW_URL", "https://tka-master-preview.up.railway.app")

MOBILE_VIEWPORT = {"width": 390, "height": 844}
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
)


class TKATestHarness:
    def __init__(self, base_url=None, headless=True):
        self.base_url = base_url or LOCAL_URL
        self.headless = headless
        self._pw = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(
            headless=self.headless,
            args=["--disable-web-security", "--no-sandbox"]
        )
        self.context = self.browser.new_context(
            viewport=MOBILE_VIEWPORT,
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            ignore_https_errors=True
        )
        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()

    def goto(self, path=""):
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(500)
        return self.page

    def masuk_tamu(self):
        """Masuk ke /app sebagai Tamu tanpa data login"""
        self.page.goto(f"{self.base_url}/app", wait_until="domcontentloaded", timeout=15000)
        self.page.evaluate("""() => {
            localStorage.removeItem('tka_supabase_auth_token');
            localStorage.removeItem('tka_user');
            localStorage.removeItem('tka_device_logged_in');
        }""")
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(800)
        return self.page

    def masuk_login(self, name="Test Siswa", email="siswa_test@example.com"):
        """Masuk ke /app sebagai akun login test (bukan akun riil produksi)"""
        self.page.goto(f"{self.base_url}/app", wait_until="domcontentloaded", timeout=15000)
        self.page.evaluate(f"""() => {{
            const testUser = {{
                name: "{name}",
                email: "{email}",
                avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=TestSiswa",
                loggedIn: true
            }};
            localStorage.setItem('tka_user', JSON.stringify(testUser));
            localStorage.setItem('tka_device_logged_in', 'true');
            localStorage.setItem('tka_supabase_auth_token', JSON.stringify({{
                access_token: 'test_token_mock',
                user: {{ id: 'test_user_123', email: '{email}' }}
            }}));
            window.TKA_USER = testUser;
        }}""")
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(800)
        return self.page

    def hardware_back(self):
        """Simulasikan hardware back button HP / popstate"""
        self.page.evaluate("window.history.back()")
        self.page.wait_for_timeout(600)

    def dump_storage(self):
        """Dump localStorage dan sessionStorage dengan penyensoran token rahasia"""
        storage = self.page.evaluate("""() => {
            const ls = {};
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                ls[k] = localStorage.getItem(k);
            }
            const ss = {};
            for (let i = 0; i < sessionStorage.length; i++) {
                const k = sessionStorage.key(i);
                ss[k] = sessionStorage.getItem(k);
            }
            return { localStorage: ls, sessionStorage: ss };
        }""")
        
        # Sensor token
        for st_type in ("localStorage", "sessionStorage"):
            for k, v in storage[st_type].items():
                if any(sec in k.lower() for sec in ["token", "secret", "auth", "password"]):
                    storage[st_type][k] = "[CENSORED_TOKEN]"
        return storage

    def save_evidence(self, filepath_base, description, assertions=None):
        """Simpan screenshot PNG + text log assertion"""
        os.makedirs(os.path.dirname(filepath_base), exist_ok=True)
        img_path = f"{filepath_base}.png"
        log_path = f"{filepath_base}.log"

        self.page.screenshot(path=img_path)
        
        dom_summary = self.page.evaluate("""() => {
            return {
                url: window.location.href,
                historyLength: window.history.length,
                quizMode: document.body.dataset.quizMode || '0',
                activePanel: typeof homeActivePanel !== 'undefined' ? homeActivePanel : 'none',
                openModals: Array.from(document.querySelectorAll('.open, .active, .show, [style*="display: block"]'))
                    .map(el => el.id || el.className)
                    .filter(Boolean)
                    .slice(0, 15)
            };
        }""")

        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": description,
            "dom_summary": dom_summary,
            "assertions": assertions or {},
            "storage_dump": self.dump_storage()
        }

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(log_data, indent=2, ensure_ascii=False))

        print(f"[Evidence Saved] Image: {img_path} | Log: {log_path}")
        return img_path, log_path
