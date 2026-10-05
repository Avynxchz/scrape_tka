# -*- coding: utf-8 -*-
"""Ambil string EXACT dari sumber untuk penggantian aman."""
import io, re

b = io.open('scratch/_desk_body.html', encoding='utf-8').read()

def show(pat, ctx=140):
    i = b.find(pat)
    print(f'--- "{pat}" @ {i}')
    if i != -1:
        print(repr(b[max(0, i - ctx // 2):i + ctx // 2 + len(pat)]))

show('Skor Komposit', 260)
show('92</span>', 200)
show('Kategori Tinggi', 160)
show('Persentil', 120)
show('Penalaran Matematika', 160)
show('95%', 120)
show('Literasi Sains', 160)
show('89%', 120)
show('Target: STEI', 140)
show('Peluang Lolos', 140)
show('Akun Pro', 140)
show('Aktif s/d', 120)
show('84/100', 140)
show('Tersisa 84', 120)
show('Rata-rata Durasi', 160)
show('Minggu Ini', 120)
show('Target tercapai', 160)
show('Rian Pratama', 160)
show('Kelas 12 SMA', 140)
show('60% (', 160)
show('Lihat Semua (8', 140)
show('Mekanika Kuantum', 160)
show('Mikro-Makro', 160)
show('>Terjadwal<', 120)
show('>Populer<', 120)
