/* ============================================================
   BRIDGE — home_desktop.html (desain Stitch desktop)
   Terima data nyata dari app utama via postMessage, update angka
   di card, dan kirim klik paket balik ke parent.
   Urutan card di kode Stitch (fixed): section 1..3, masing2 2 card
   (Paket 1, Paket 2) -> mapping ke daftar subject dari parent.
   ============================================================ */
(function () {
  'use strict';

  var BRIDGE = {
    render: function (data) {
      if (!data || !data.subjects) return;
      // subjects: daftar terurut sesuai SECTION Stitch:
      // [ {subject,pkg,label,count,minutes,progress} x6 ]
      var cards = document.querySelectorAll(
        'main section .grid.grid-cols-1.md\\:grid-cols-2 > div.relative'
      );
      var list = data.subjects;
      var i = 0;
      cards.forEach(function (card) {
        if (i >= list.length) return;
        var d = list[i++];
        card.dataset.subject = d.subject;
        card.dataset.pkg = d.pkg;
        card.style.cursor = 'pointer';
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', (d.label || '') + ' Paket ' + d.pkg);

        // chip mapel (MATEMATIKA / FISIKA / EKONOMI)
        var chip = card.querySelector('span.rounded-full.bg-brand-emerald-light');
        if (chip && d.label) chip.textContent = d.label.toUpperCase();

        // jumlah soal: span yang berisi ikon list + "N Soal ..."
        // (struktur Stitch: <span class=flex...><span.ikon>format_list_numbered</span> 20 Soal HOTS</span>)
        // placeholder "— Soal" juga dicocokkan supaya kiriman setelah prefetch tetap mengisi
        var spans = card.querySelectorAll('span');
        spans.forEach(function (s) {
          if (/(\d+|—)\s*Soal/.test(s.textContent)) {
            var icon = s.querySelector('span.material-symbols-outlined');
            var iconHtml = icon ? icon.outerHTML : '';
            s.innerHTML = iconHtml + ' ' + (d.count != null ? d.count : '—') + ' Soal';
          }
        });
        // durasi menit: span berisi "N Menit" (atau placeholder "— Menit")
        spans.forEach(function (s) {
          if (/(\d+|—)\s*Menit/.test(s.textContent)) {
            var icon2 = s.querySelector('span.material-symbols-outlined');
            var iconHtml2 = icon2 ? icon2.outerHTML : '';
            s.innerHTML = iconHtml2 + ' ' + (d.minutes || 45) + ' Menit';
          }
        });

        // progress
        var pct = Math.max(0, Math.min(100, d.progress || 0));
        var pctLabel = card.querySelector('.font-semibold:last-child, span.font-bold');
        var bar = card.querySelector('.h-2 > div, .rounded-full.h-full, div[style*="width"]');
        // label persen: span yang isinya persen
        spans.forEach(function (s) {
          if (/^\d+%$/.test(s.textContent.trim())) {
            s.textContent = pct + '%';
            s.classList.toggle('text-primary', pct > 0);
            s.classList.toggle('text-text-muted', pct === 0);
          }
        });
        // span persen kosong (data-progress-pct) diisi langsung
        card.querySelectorAll('[data-progress-pct]').forEach(function (s) {
          s.textContent = pct + '%';
        });
        // status pengerjaan kartu Paket 2: jangan biarkan "Belum Dimulai" saat sudah ada progres
        spans.forEach(function (s) {
          if (s.textContent.trim() === 'Belum Dimulai') {
            s.textContent = pct > 0 ? pct + '% dikerjakan' : 'Belum Dimulai';
            s.classList.toggle('text-text-muted', pct === 0);
            s.classList.toggle('text-primary', pct > 0);
          }
        });
        if (bar) {
          bar.style.width = pct + '%';
          bar.classList.toggle('bg-primary', pct > 0);
          bar.classList.toggle('bg-outline-variant', pct === 0);
        }

        // ribbon "Baru" sembunyikan bila sudah ada progres
        var ribbon = card.querySelector('.bg-badge-amber-bg');
        if (ribbon) ribbon.style.display = pct > 0 ? 'none' : '';
      });

      BRIDGE._list = list;
      if (data.progress) BRIDGE.renderProgress(data);
      // PENTING: jangan kirim 'home-desktop-ready' dari sini — parent membalas
      // ready dengan data baru, data memicu render lagi -> ping-pong tak henti.
      // Sinyal ready cukup sekali saat init (paling bawah file).
    },


    // Kartu progres (kanan atas): isi dari data nyata yang dikirim parent
    renderProgress: function (data) {
      var el = document.getElementById('deskSoalDikerjakan');
      if (!el) return;
      var p = data.progress || { dikerjakan: 0, benar: 0, tepat: 0 };
      el.textContent = String(p.dikerjakan || 0);
      // label 'Soal Benar' -> angka benar; 'Ketepatan' -> persen
      var spans = document.querySelectorAll('main span, aside span');
      spans.forEach(function (s) {
        if (s.textContent.trim() === 'Ketepatan: —' || s.textContent.trim().indexOf('Ketepatan:') === 0) {
          s.textContent = 'Ketepatan: ' + (p.dikerjakan ? p.tepat + '%' : '—');
        }
      });
      // checklist benar/salah: value span setelah label Jawaban Benar / Jawaban Salah
      var fills = document.querySelectorAll('main .font-label-md.text-label-md.text-primary.font-semibold');
      if (fills[0]) fills[0].textContent = String(p.benar || 0);
      if (fills[1]) fills[1].textContent = String((p.dikerjakan || 0) - (p.benar || 0));
    },

    send: function (payload) {
      try { parent.postMessage(payload, '*'); } catch (e) {}
    },
  };

  // klik / keyboard pada card -> kirim ke parent
  document.querySelectorAll('main .relative[role="button"], main section .grid > div.relative').forEach(function (card) {
    var act = function () {
      var subject = card.dataset.subject, pkg = parseInt(card.dataset.pkg || '1', 10);
      if (!subject) return;
      BRIDGE.send({ type: 'open-package', subject: subject, pkg: pkg });
    };
    card.addEventListener('click', act);
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); act(); }
    });
  });

  // tombol nav atas: kirim path ke parent (Beranda/Modul/Progres dll.)
  document.querySelectorAll('nav a[href="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      BRIDGE.send({ type: 'nav', path: a.textContent.trim() });
    });
  });

  // chip user (kanan atas) -> buka panel Akun
  document.querySelectorAll('[data-nav-akun]').forEach(function (el) {
    el.addEventListener('click', function () {
      BRIDGE.send({ type: 'nav', path: 'Akun' });
    });
  });

  // terima data
  window.addEventListener('message', function (e) {
    var d = e.data || {};
    if (d.type === 'home-desktop-data') BRIDGE.render(d);
  });

  BRIDGE.send({ type: 'home-desktop-ready' });
  window.__homeDesktopBridge = BRIDGE;
})();
