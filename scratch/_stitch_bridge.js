/* ============================================================
   BRIDGE — lapisan data asli TKA Master di atas desain Stitch.
   Dipanggil oleh parent (app.js) via postMessage:
     { type:'home-data', subjects:[{key,label,icon,pkg:1|2,count,minutes,progress}], ... }
   Mengirim balik: { type:'open-package', subject, pkg }
   ============================================================ */
(function () {
  'use strict';

  var BRIDGE = {
    // deteksi paket: kartu ke-i dalam section = Paket 1/2 bergantian
    render: function (data) {
      if (!data || !data.subjects) return;

      // 1) Hero: teks & CTA
      var heroTitle = document.querySelector('.hhero-text h1, .ho-hero-copy h2');
      var heroBtn = document.querySelector('main button');
      // biarkan teks hero default Stitch (sudah relevan)

      // 2) Update setiap kartu paket dengan angka nyata
      var cards = document.querySelectorAll('.snap-start');
      var list = data.subjects; // [{subject, pkg, label, count, minutes, progress}]
      var i = 0;
      cards.forEach(function (card) {
        if (i >= list.length) return;
        var d = list[i++];
        card.dataset.subject = d.subject;
        card.dataset.pkg = d.pkg;

        // judul: "Paket 1" / "Paket 2" (biarkan)
        // meta: "46 Soal • 45 Menit"
        var meta = card.querySelector('p.font-body-sm span:last-child');
        if (meta) meta.textContent = (d.count ? d.count + ' Soal' : 'Paket ' + d.pkg) + ' • ' + (d.minutes || 45) + ' Menit';

        // chip mapel
        var chip = card.querySelector('div.inline-flex, .inline-flex.items-center.px-2\\.5');
        if (chip) chip.textContent = (d.label || '').toUpperCase();

        // progres
        var pct = Math.max(0, Math.min(100, d.progress || 0));
        var pctLabel = card.querySelector('.text-\\[11px\\] span:last-child, span.font-bold');
        var bar = card.querySelector('.h-2 > div, div[class*="h-full rounded-full"]');
        if (pctLabel) {
          pctLabel.textContent = pct + '%';
          pctLabel.classList.toggle('text-tertiary', pct > 0);
          pctLabel.classList.toggle('text-secondary', pct === 0);
        }
        if (bar) {
          bar.style.width = pct + '%';
          bar.classList.toggle('bg-tertiary-container', pct > 0);
          bar.classList.toggle('bg-outline-variant/60', pct === 0);
        }

        // ribbon "Baru" hanya untuk paket yang belum pernah dikerjakan
        var ribbon = card.querySelector('.rotate-45');
        if (ribbon) ribbon.style.display = pct > 0 ? 'none' : '';

        card.style.cursor = 'pointer';
        card.setAttribute('role', 'link');
        card.setAttribute('aria-label', (d.label || '') + ' Paket ' + d.pkg);
      });

      // 3) simpan untuk klik
      BRIDGE._list = list;
    },

    send: function (payload) {
      try { parent.postMessage(payload, '*'); } catch (e) {}
    },
  };

  // klik kartu paket -> kirim ke parent
  document.querySelectorAll('.snap-start').forEach(function (card) {
    card.addEventListener('click', function () {
      var subject = card.dataset.subject, pkg = parseInt(card.dataset.pkg || '1', 10);
      if (!subject) return;
      BRIDGE.send({ type: 'open-package', subject: subject, pkg: pkg });
    });
  });

  // tombol "Mulai Sekarang" (hero) -> paket pertama yang tersedia
  var heroBtn = document.querySelector('main .grid button');
  if (heroBtn) heroBtn.addEventListener('click', function () {
    var first = (BRIDGE._list || [])[0];
    if (first) BRIDGE.send({ type: 'open-package', subject: first.subject, pkg: first.pkg });
  });

  // tombol nav bawah: cuma Beranda aktif; lainnya kirim pesan (belum ada halamannya)
  document.querySelectorAll('nav[data-active-classes] a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var path = a.dataset.path;
      if (path !== 'beranda') BRIDGE.send({ type: 'nav', path: path });
    });
  });

  // terima data dari parent
  window.addEventListener('message', function (e) {
    var d = e.data || {};
    if (d.type === 'home-data') BRIDGE.render(d);
  });

  // beri tahu parent bahwa iframe siap
  BRIDGE.send({ type: 'home-ready' });

  window.__homeStitchBridge = BRIDGE;
})();
