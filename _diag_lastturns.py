# -*- coding: utf-8 -*-
"""_diag_lastturns.py — Lihat 6 turn terakhir di DOM AI Studio."""
from playwright.sync_api import sync_playwright

JS = r"""
() => {
  const turns = document.querySelectorAll('ms-chat-turn');
  const n = turns.length;
  const last = [];
  for (let i = Math.max(0, n - 6); i < n; i++) {
    const t = turns[i];
    const txt = (t.innerText || '').trim();
    const hasQ = txt.match(/"question_number"\s*:\s*(\d+)/);
    last.push({
      idx: i,
      len: txt.length,
      qnum: hasQ ? hasQ[1] : null,
      head: txt.slice(0, 90).replace(/\n/g, ' | ')
    });
  }
  const has21 = /"question_number"\s*:\s*21/.test(document.body.innerText);
  const has25 = /"question_number"\s*:\s*25/.test(document.body.innerText);
  const has29 = /"question_number"\s*:\s*29/.test(document.body.innerText);
  return { turnCount: n, last, has21, has25, has29 };
}
"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    pg = next((x for x in ctx.pages if "aistudio" in x.url.lower()), None)
    r = pg.evaluate(JS)
    print("turnCount:", r["turnCount"], "| has21:", r["has21"], "| has25:", r["has25"], "| has29:", r["has29"])
    for x in r["last"]:
        print(x)
