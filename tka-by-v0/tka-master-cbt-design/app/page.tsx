'use client'

import { useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  Bot,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  Compass,
  Grid2X2,
  Lightbulb,
  MessageCircle,
  Paperclip,
  Plane,
  Sparkles,
  Target,
  Timer,
  X,
  Zap,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const options = [
  { key: 'A', text: 'A ∩ B = {2, 4}' },
  { key: 'B', text: 'A ∪ C = {1, 2, 3, 4, 5}' },
  { key: 'C', text: '(A ∩ B) ∪ C = {1, 2, 3, 4}' },
  { key: 'D', text: 'A − B = {1, 3, 5}' },
  { key: 'E', text: 'Aᶜ ∩ C = {2, 4, 6}' },
]

const steps = [
  ['Tentukan anggota himpunan A', 'Dari informasi pada soal, himpunan A memiliki anggota {1, 2, 3, 4}.'],
  ['Temukan irisan A dan B', 'Irisan adalah anggota yang terdapat di kedua himpunan. Jadi A ∩ B = {2, 4}.'],
  ['Gabungkan dengan himpunan C', 'Himpunan C = {1, 3}. Gabungkan tanpa mengulang anggota yang sama.'],
  ['Tulis hasil akhir', 'Maka (A ∩ B) ∪ C = {1, 2, 3, 4}. Jawaban yang tepat adalah C.'],
]

export default function Page() {
  const [selected, setSelected] = useState('C')
  const [doubtful, setDoubtful] = useState(false)
  const [showSolution, setShowSolution] = useState(true)
  const [showNavigator, setShowNavigator] = useState(false)
  const [chat, setChat] = useState<string[]>(['Hai! Aku siap membantu kamu memahami konsep pada soal ini.'])
  const [message, setMessage] = useState('')

  function sendMessage() {
    const trimmed = message.trim()
    if (!trimmed) return
    setChat((current) => [...current, trimmed, 'Pertanyaan bagus! Ingat, irisan (∩) berarti memilih anggota yang sama pada dua himpunan. Coba periksa kembali langkah kedua.'])
    setMessage('')
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200/90 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-[1440px] items-center justify-between gap-2 px-3 sm:h-[72px] sm:gap-4 sm:px-4 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-200"><Target className="size-5" /></div>
            <div className="hidden sm:block"><p className="text-sm font-bold tracking-tight">TKA Master</p><p className="text-[11px] text-slate-500">Simulasi Ujian & AI Tutor</p></div>
          </div>
          <div className="hidden items-center rounded-xl border border-slate-200 bg-slate-50 p-1 md:flex">
            <button className="rounded-lg bg-white px-5 py-2 text-xs font-bold text-blue-700 shadow-sm">Paket 1</button><button className="px-5 py-2 text-xs font-semibold text-slate-500">Paket 2</button>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700 sm:flex"><Clock3 className="size-4" /> 01:45:20</div>
            <Button variant="outline" size="lg" className="h-10 gap-2 rounded-xl border-slate-200 px-3 text-xs font-bold" onClick={() => setShowNavigator(true)}><Grid2X2 data-icon="inline-start" /> <span className="hidden sm:inline">Daftar Soal</span></Button>
            <div className="flex size-9 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">AR</div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1440px] gap-4 px-3 py-4 sm:gap-6 sm:px-4 sm:py-6 lg:grid-cols-[minmax(0,1fr)_390px] lg:px-8">
        <section className="min-w-0">
          <div className="mb-3 flex items-center justify-between sm:mb-5"><div><p className="text-[10px] font-bold text-blue-600 sm:text-xs">MATEMATIKA SMA · HIMPUNAN</p><h1 className="mt-0.5 text-lg font-bold tracking-tight sm:mt-1 sm:text-2xl">Latihan soal UTBK</h1></div><div className="flex items-center gap-2 text-xs font-medium text-slate-500"><span>1</span><div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-200"><div className="h-full w-[8%] rounded-full bg-blue-600" /></div><span>40</span></div></div>
          <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 px-3 py-3 sm:px-7 sm:py-4"><div className="flex items-center gap-1.5 text-xs font-bold sm:gap-2 sm:text-sm"><span className="flex size-7 items-center justify-center rounded-lg bg-blue-50 text-xs text-blue-700">01</span> Soal Nomor 1 dari 40</div><span className="rounded-full bg-slate-100 px-3 py-1.5 text-[11px] font-bold text-slate-600">Pilihan Ganda</span></div>
            <div className="p-3.5 sm:p-8"><p className="max-w-3xl text-sm font-medium leading-6 text-slate-800 sm:text-lg sm:leading-8">Diketahui himpunan <span className="formula">A = {'{'}1, 2, 3, 4{'}'}</span>, <span className="formula">B = {'{'}2, 4, 6{'}'}</span>, dan <span className="formula">C = {'{'}1, 3{'}'}</span>. Hasil dari operasi himpunan berikut adalah:</p><div className="my-4 overflow-x-auto rounded-xl bg-slate-50 px-3 py-4 text-center font-mono text-base font-semibold text-indigo-700 sm:my-7 sm:px-5 sm:py-6 sm:text-xl">(A ∩ B) ∪ C = ?</div><div className="flex flex-col gap-3">{options.map((option) => <button key={option.key} onClick={() => setSelected(option.key)} className={`flex min-h-11 items-center gap-3 rounded-xl border px-3 text-left transition sm:min-h-14 sm:gap-4 sm:px-4 ${selected === option.key ? 'border-blue-500 bg-blue-50/70 text-blue-950 ring-2 ring-blue-500/10' : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'}`}><span className={`flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${selected === option.key ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}`}>{option.key}</span><span className="text-sm font-medium">{option.text}</span>{selected === option.key && <Check className="ml-auto size-4 text-blue-600" />}</button>)}</div></div>
            <div className="flex flex-col gap-2.5 border-t border-slate-100 bg-slate-50/60 p-3 sm:flex-row sm:items-center sm:justify-between sm:px-7 sm:py-5"><div className="flex gap-2"><Button className="h-11 rounded-xl bg-slate-900 px-4 text-xs font-bold hover:bg-slate-700"><CheckCircle2 data-icon="inline-start" /> Cek Jawaban & Pembahasan</Button><Button variant="outline" className={`h-11 rounded-xl px-4 text-xs font-bold ${doubtful ? 'border-amber-400 bg-amber-50 text-amber-700' : ''}`} onClick={() => setDoubtful(!doubtful)}><CircleHelp data-icon="inline-start" /> Ragu-ragu</Button></div><div className="flex gap-2"><Button variant="ghost" className="h-11 rounded-xl text-xs font-semibold text-slate-500"><ArrowLeft data-icon="inline-start" /> Sebelumnya</Button><Button variant="outline" className="h-11 rounded-xl text-xs font-bold">Selanjutnya <ArrowRight data-icon="inline-end" /></Button></div></div>
          </article>

          <button onClick={() => setShowSolution(!showSolution)} className="mt-3 flex w-full items-center justify-between rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-left shadow-sm sm:mt-5 sm:px-5 sm:py-4"><span className="flex items-center gap-3 text-sm font-bold"><BookOpen className="size-5 text-emerald-600" /> Tata Cara & Langkah Penyelesaian</span><ChevronDown className={`size-5 text-slate-400 transition ${showSolution ? 'rotate-180' : ''}`} /></button>
          {showSolution && <div className="mt-3 flex flex-col gap-3 sm:mt-4 sm:gap-4">
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-5"><div className="flex items-center gap-3"><div className="flex size-10 items-center justify-center rounded-full bg-emerald-600 text-white"><CheckCircle2 className="size-5" /></div><div><p className="text-sm font-bold text-emerald-900">Solusi Terverifikasi</p><p className="text-xs text-emerald-700">Jawaban kamu tepat. Pertahankan!</p></div></div><div className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white">Kunci Resmi: C</div></div>
            <div className="rounded-2xl border-l-4 border-emerald-500 bg-white p-5 shadow-sm"><div className="mb-4 flex items-center gap-2 text-sm font-bold"><Compass className="size-5 text-emerald-600" /> Konsep & Teori Kunci</div><div className="flex flex-wrap gap-2"><span className="rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">Irisan Himpunan ∩</span><span className="rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">Gabungan Himpunan ∪</span><span className="rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">Anggota Himpunan</span></div></div>
            <div className="rounded-2xl border border-indigo-100 bg-indigo-50/60 p-5"><div className="mb-4 flex items-center gap-2 text-sm font-bold text-indigo-950"><Zap className="size-5 text-indigo-600" /> Glosarium Simbol & Notasi</div><div className="grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-white p-3"><span className="mr-2 rounded-md bg-indigo-100 px-2 py-1 font-mono text-sm font-bold text-indigo-700">∩</span><span className="text-xs font-semibold text-slate-700">Irisan — anggota yang sama</span></div><div className="rounded-xl bg-white p-3"><span className="mr-2 rounded-md bg-indigo-100 px-2 py-1 font-mono text-sm font-bold text-indigo-700">∪</span><span className="text-xs font-semibold text-slate-700">Gabungan — semua anggota</span></div></div></div>
            <div className="rounded-2xl bg-violet-50 p-5"><div className="mb-2 flex items-center gap-2 text-sm font-bold text-violet-950"><Lightbulb className="size-5 text-violet-600" /> Mengapa rumus ini dipakai?</div><p className="text-sm leading-6 text-violet-900/80">Kita mencari anggota yang sama terlebih dahulu melalui irisan, lalu menggabungkan hasilnya dengan anggota C. Urutan ini membuat tidak ada anggota yang terhitung dua kali.</p></div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><h2 className="mb-5 text-sm font-bold">Langkah-Langkah Pengerjaan Rinci</h2><div className="flex flex-col gap-5">{steps.map(([title, text], index) => <div className="relative flex gap-4" key={title}><div className="relative flex w-7 shrink-0 justify-center"><span className="z-10 flex size-7 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">{index + 1}</span>{index < steps.length - 1 && <span className="absolute top-7 h-[calc(100%+20px)] w-px bg-blue-100" />}</div><div className="pb-1"><p className="text-sm font-bold text-slate-800">{title}</p><p className="mt-1 text-sm leading-6 text-slate-500">{text}</p><div className="mt-2 overflow-x-auto rounded-lg bg-slate-50 px-3 py-2 font-mono text-xs text-indigo-700">{index === 1 ? 'A ∩ B = {2, 4}' : index === 3 ? '(A ∩ B) ∪ C = {1, 2, 3, 4}' : '→ lanjutkan ke langkah berikutnya'}</div></div></div>)}</div></div>
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5"><div className="flex items-center gap-2 text-sm font-bold text-amber-900"><Timer className="size-5 text-amber-600" /> Tips Cepat & Jebakan Soal</div><p className="mt-2 text-sm leading-6 text-amber-800">Jangan menjumlahkan anggota irisan dua kali. Tulis anggota dalam kurung kurawal dan pastikan tidak ada duplikasi.</p></div>
          </div>}
        </section>

        <aside className="h-fit lg:sticky lg:top-[96px]"><div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><div className="flex items-center justify-between border-b border-slate-100 p-3.5 sm:p-5"><div className="flex items-center gap-3"><div className="flex size-10 items-center justify-center rounded-xl bg-blue-600 text-white"><Bot className="size-5" /></div><div><h2 className="text-sm font-bold">AI Tutor Cerdas</h2><p className="flex items-center gap-1 text-[11px] text-emerald-600"><span className="size-1.5 rounded-full bg-emerald-500" /> Sedang aktif</p></div></div><Sparkles className="size-4 text-blue-500" /></div><div className="flex gap-2 overflow-x-auto border-b border-slate-100 p-4"><span className="shrink-0 rounded-full bg-blue-50 px-3 py-2 text-[11px] font-semibold text-blue-700">Apa arti simbol ini?</span><span className="shrink-0 rounded-full bg-slate-100 px-3 py-2 text-[11px] font-semibold text-slate-600">Trik cepat ujian</span></div><div className="flex min-h-[240px] flex-col gap-3 p-3.5 sm:min-h-[310px] sm:gap-4 sm:p-5">{chat.map((item, index) => <div key={`${item}-${index}`} className={index % 2 === 1 ? 'max-w-[90%] self-end rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-3 text-xs leading-5 text-white' : 'rounded-xl border border-slate-100 bg-slate-50 p-4 text-xs leading-5 text-slate-600'}>{index % 2 === 0 && <div className="mb-2 flex items-center gap-2 font-bold text-slate-800"><Bot className="size-4 text-blue-600" /> AI Tutor</div>}{item}</div>)}</div><div className="border-t border-slate-100 p-3 sm:p-4"><div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-2"><input aria-label="Tanyakan kepada AI Tutor" value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.nativeEvent.isComposing && event.keyCode !== 229) sendMessage() }} placeholder="Tanyakan langkah atau rumus..." className="min-w-0 flex-1 bg-transparent px-2 text-xs outline-none placeholder:text-slate-400" /><Button size="icon" className="size-9 rounded-lg bg-blue-600" onClick={sendMessage}><Plane /></Button></div><p className="mt-2 text-center text-[10px] text-slate-400">AI dapat membuat kesalahan. Verifikasi jawabanmu.</p></div></div></aside>
      </div>

      {showNavigator && <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/30 p-4 sm:items-center" onClick={() => setShowNavigator(false)}><div role="dialog" aria-modal="true" aria-label="Daftar soal" className="w-full max-w-lg rounded-2xl bg-white p-5 shadow-2xl" onClick={(event) => event.stopPropagation()}><div className="mb-5 flex items-center justify-between"><div><h2 className="font-bold">Daftar Soal</h2><p className="mt-1 text-xs text-slate-500">Pilih nomor untuk berpindah soal</p></div><Button variant="ghost" size="icon" onClick={() => setShowNavigator(false)}><X /></Button></div><div className="mb-5 flex flex-wrap gap-3 text-[11px] font-medium text-slate-500"><span><i className="mr-1 inline-block size-2 rounded-full bg-blue-600" /> Sedang dikerjakan</span><span><i className="mr-1 inline-block size-2 rounded-full bg-emerald-500" /> Sudah dijawab</span><span><i className="mr-1 inline-block size-2 rounded-full bg-amber-400" /> Ragu-ragu</span></div><div className="grid grid-cols-8 gap-2">{Array.from({ length: 40 }, (_, index) => <button key={index} onClick={() => setShowNavigator(false)} className={`flex aspect-square items-center justify-center rounded-lg border text-xs font-bold ${index === 0 ? 'border-blue-600 bg-blue-600 text-white' : index < 5 ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : index === 7 && doubtful ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-slate-200 text-slate-500 hover:border-blue-300'}`}>{index + 1}</button>)}</div></div></div>}
    </main>
  )
}
