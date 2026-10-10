# -*- coding: utf-8 -*-
import json
import os

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA_DEV"

SOAL_SERUPA_DATA = {
    "teknik_otomotif": {
        1: {
            "pertanyaan": "Saat melakukan pengujian emisi gas buang kendaraan berbahan bakar bensin di dalam bengkel tertutup tanpa instalasi cerobong otomatis, seorang mekanik mulai mengeluhkan pusing dan lemas. Tindakan darurat awal yang paling tepat untuk keselamatan kerja adalah...",
            "pilihan": [
                {"key": "A", "text": "Memberikan masker kain tambahan kepada mekanik tersebut lalu melanjutkan pengujian"},
                {"key": "B", "text": "Segera mematikan mesin, mengevakuasi korban ke area udara terbuka, dan membuka seluruh sirkulasi ventilasi"},
                {"key": "C", "text": "Menyalakan kipas angin kecil ke arah knalpot agar asap mengalir ke sudut ruangan"},
                {"key": "D", "text": "Menyiram knalpot kendaraan dengan air dingin agar suhu gas buang segera turun"},
                {"key": "E", "text": "Menutup pintu bengkel rapat-rapat agar polusi gas tidak mencemari ruang kantor bengkel"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Gas karbon monoksida (CO) bersifat racun asfiksia yang mengikat hemoglobin darah. Penanganan darurat wajib segera menghentikan emisi mesin dan membawa korban ke udara segar beroksigen cukup."
        },
        2: {
            "pertanyaan": "Terjadi kebakaran pada tumpukan kain majun yang terkena tumpahan bensin dan thinner di sudut ruang pencucian komponen otomotif. Jenis APAR (Alat Pemadam Api Ringan) yang paling tepat digunakan untuk memadamkan kebakaran cairan mudah terbakar tersebut adalah...",
            "pilihan": [
                {"key": "A", "text": "APAR jenis air bertekanan tinggi"},
                {"key": "B", "text": "APAR jenis serbuk kimia kering (Dry Chemical Powder) atau busa (Foam)"},
                {"key": "C", "text": "Menyiram kobaran api dengan solar dingin"},
                {"key": "D", "text": "Mengibaskan kain majun basah di atas kobaran api"},
                {"key": "E", "text": "Meniup api menggunakan kompresor udara bertekanan"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Kebakaran Kelas B (cairan mudah terbakar seperti bensin/thinner) wajib dipadamkan dengan APAR Powder atau Busa yang memutus kontak oksigen dengan bahan bakar. Penggunaan air dilarang karena bensin mengapung di atas air dan memperluas kebakaran."
        },
        3: {
            "pertanyaan": "Seorang mekanik hendak melepas baut roda yang terkunci sangat kencang. Peralatan tangan (hand tool) yang paling aman digunakan agar sudut kepala baut tidak rusak/aus dan mekanik terhindar dari selip adalah...",
            "pilihan": [
                {"key": "A", "text": "Kunci pas terbuka dengan sudut miring"},
                {"key": "B", "text": "Kunci inggris yang dapat disetel rahangnya"},
                {"key": "C", "text": "Kunci soket atau kunci ring bersegi enam (6-point socket) sesuai ukuran"},
                {"key": "D", "text": "Tang buaya (locking pliers)"},
                {"key": "E", "text": "Pahat besi yang dipukul palu pada tepi baut"}
            ],
            "kunci": "C",
            "pembahasan_singkat": "Kunci soket/ring 6-point mencengkeram seluruh 6 bidang sisi kepala baut secara merata dengan kontak maksimal, sehingga mencegah risiko kepala baut bulat/aus pada torsi pengencangan tinggi."
        },
        4: {
            "pertanyaan": "Sebuah dongkrak hidrolik memiliki luas penampang silinder pompa kecil $A_1 = 4\\text{ cm}^2$ dan luas silinder beban besar $A_2 = 200\\text{ cm}^2$. Jika gaya tekan yang diberikan pada pompa kecil adalah $120\\text{ N}$, maka gaya angkat yang dihasilkan pada silinder beban adalah...",
            "pilihan": [
                {"key": "A", "text": "2.400 N"},
                {"key": "B", "text": "4.800 N"},
                {"key": "C", "text": "6.000 N"},
                {"key": "D", "text": "8.000 N"},
                {"key": "E", "text": "12.000 N"}
            ],
            "kunci": "C",
            "pembahasan_singkat": "Berdasarkan Hukum Pascal: $F_2 = F_1 \\times \\frac{A_2}{A_1} = 120 \\times \\frac{200}{4} = 120 \\times 50 = 6.000\\text{ N}$."
        },
        5: {
            "pertanyaan": "Hasil pemeriksaan berat jenis cairan elektrolit baterai basah menggunakan hidrometer menunjukkan angka $1,18\\text{ kg/dm}^3$ pada suhu standar (kondisi aki penuh adalah $1,26 - 1,28$). Tindakan perawatan yang paling tepat dilakukan adalah...",
            "pilihan": [
                {"key": "A", "text": "Menguras cairan aki dan menggantinya dengan asam sulfat murni pekat"},
                {"key": "B", "text": "Melakukan pengisian lambat (slow charging) baterai hingga berat jenis kembali standar"},
                {"key": "C", "text": "Membuang aki karena sel aki sudah mengalami kerusakan permanen"},
                {"key": "D", "text": "Menambahkan air aki biasa sampai melewati garis Upper Level"},
                {"key": "E", "text": "Menghubungkan langsung kutub positif dan negatif dengan kabel untuk menguji percikan"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Berat jenis elektrolit 1,18 menandakan baterai mengalami pengosongan muatan (debit kapasitas tinggal ~50%). Tindakan standar adalah melakukan slow charging dan mengukur kembali berat jenisnya setelah terisi penuh."
        },
        6: {
            "pertanyaan": "Saat seorang teknisi menguji tegangan terminal baterai 12V menggunakan multimeter digital, layar multimeter menunjukkan angka 0,00 V meskipun klakson kendaraan masih dapat berbunyi keras. Kesalahan prosedur ukur yang paling mungkin terjadi adalah...",
            "pilihan": [
                {"key": "A", "text": "Sakelar selektor multimeter diarahkan ke pengukuran arus (DCA) atau resistansi (Ohm)"},
                {"key": "B", "text": "Sakelar selektor multimeter diarahkan ke DCV batas ukur 20 V"},
                {"key": "C", "text": "Probe merah dihubungkan ke kutub positif baterai"},
                {"key": "D", "text": "Probe hitam dihubungkan ke kutub negatif baterai"},
                {"key": "E", "text": "Pengukuran dilakukan saat mesin kendaraan dalam posisi mati"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Multimeter tidak dapat mengukur beda potensial tegangan jika selektor tidak berada pada mode DCV. Mengarahkan selektor ke posisi DCA atau Ohm saat mengukur sumber tegangan aktif adalah kesalahan fatal yang membuat nilai tegangan tidak terbaca."
        }
    },
    "teknik_jaringan": {
        1: {
            "pertanyaan": "Pada proses penyambungan kabel fiber optik, seorang teknisi selesai mengupas dan memotong ujung core kaca. Prosedur K3LH yang tepat untuk menangani sisa patahan core kaca adalah...",
            "pilihan": [
                {"key": "A", "text": "Meniup serpihan kaca dari meja kerja menggunakan kompresor angin"},
                {"key": "B", "text": "Mengambil serpihan dengan selotip/lakban khusus dan membuangnya ke wadah tertutup khusus limbah tajam"},
                {"key": "C", "text": "Menyapu pecahan kaca ke lantai bengkel lalu menginjaknya agar hancur"},
                {"key": "D", "text": "Mencuci meja kerja dengan air mengalir ke saluran wastafel"},
                {"key": "E", "text": "Mengumpulkan pecahan kaca dengan tangan telanjang ke saku celana"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Patahan serat kaca (fiber scrap) berukuran mikron sangat berbahaya bila menusuk kulit atau masuk ke aliran darah. Prosedur K3LH mewajibkan penggunaan wadah pembuangan tertutup (fiber disposal container) dan perekat khusus."
        },
        2: {
            "pertanyaan": "Mesin fusion splicer menolak melakukan penyambungan dan memunculkan notifikasi error 'Cleave Angle Exceeded' (> 1.5°). Tindakan korektif teknisi jaringan yang tepat adalah...",
            "pilihan": [
                {"key": "A", "text": "Menambah panas elektroda mesin splicer secara paksa"},
                {"key": "B", "text": "Membersihkan lensa kamera splicer dengan oli pelumas"},
                {"key": "C", "text": "Memotong ulang ujung serat optik menggunakan precision fiber cleaver dengan sudut siku tegak lurus"},
                {"key": "D", "text": "Menempelkan kedua ujung serat dengan lem silikon instan"},
                {"key": "E", "text": "Mengganti kabel serat optik dengan kabel tembaga UTP"}
            ],
            "kunci": "C",
            "pembahasan_singkat": "Error sudut potongan menandakan permukaan ujung core miring melampaui toleransi sambungan. Serat harus dikupas dan dipotong ulang menggunakan alat pemotong presisi (fiber cleaver) agar penampang rata 90 derajat."
        },
        3: {
            "pertanyaan": "Di dalam rak server data center, kabel-kabel patch cord UTP menumpuk semrawut di depan port switch sehingga menyulitkan pelacakan gangguan. Solusi perapihan kabel yang sesuai standar instalasi jaringan adalah...",
            "pilihan": [
                {"key": "A", "text": "Memasang horizontal cable management panel dan memberi label penanda pada kedua ujung kabel"},
                {"key": "B", "text": "Mengikat seluruh bundel kabel menjadi satu menggunakan kawat besi kencang"},
                {"key": "C", "text": "Menarik kabel sekuat tenaga agar panjang kabel tidak menumpuk"},
                {"key": "D", "text": "Memotong kabel yang panjang dan menyambungnya kembali dengan selotip isolasi"},
                {"key": "E", "text": "Memindahkan sakelar switch ke luar rak server agar kabel leluasa"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Standar kerapian rak server mewajibkan penggunaan cable organizer/manager serta sistem pelabelan kabel (cable tagging) untuk mempermudah identifikasi port dan menjaga sirkulasi pendingin rak."
        },
        4: {
            "pertanyaan": "Karakteristik mendasar yang membedakan serat optik jenis Single Mode Fiber (SMF) dengan Multi Mode Fiber (MMF) adalah...",
            "pilihan": [
                {"key": "A", "text": "SMF menggunakan inti tembaga sedangkan MMF menggunakan inti kaca"},
                {"key": "B", "text": "SMF memiliki diameter inti sangat kecil (~9 mikron) untuk jarak jauh dengan sumber laser"},
                {"key": "C", "text": "SMF memiliki diameter inti lebih besar (~50-62,5 mikron) untuk jaringan dalam gedung"},
                {"key": "D", "text": "SMF hanya dapat mentransmisikan sinyal suara dan tidak mendukung data internet"},
                {"key": "E", "text": "SMF rentan terhadap interferensi elektromagnetik gelombang radio"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Single Mode Fiber (SMF) memiliki ukuran core mikroskopis (~9 µm) sehingga hanya satu moda cahaya yang merambat lurus tanpa dispersi modal, sangat ideal untuk transmisi kecepatan gigabit jarak puluhan kilometer."
        },
        5: {
            "pertanyaan": "Saat melakukan pengukuran daya optik di titik Optical Distribution Point (ODP) menggunakan Optical Power Meter (OPM), langkah kalibrasi alat ukur yang paling krusial sebelum mencatat hasil adalah...",
            "pilihan": [
                {"key": "A", "text": "Menyetel satuan ukur ke skala Volt AC"},
                {"key": "B", "text": "Menyesuaikan panjang gelombang (wavelength) pengukuran ke 1490 nm untuk sinyal downstream data OLT"},
                {"key": "C", "text": "Membasahi konektor OPM dengan air keran"},
                {"key": "D", "text": "Mengubah frekuensi multimeter ke 50 Hz"},
                {"key": "E", "text": "Menekan tombol Zero saat cahaya laser masih aktif masuk ke OPM"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Panjang gelombang sensor OPM wajib diselaraskan dengan panjang gelombang transmisi yang diuji (misal 1490 nm untuk data downstream GPON) agar perhitungan konversi daya optik (dBm) akurat."
        },
        6: {
            "pertanyaan": "Pada instalasi kabel drop optik ke rumah pelanggan, redaman sinyal yang terbaca melonjak drastis dari -18 dBm menjadi -31 dBm. Setelah ditelusuri, kabel drop ditekuk tajam 90 derajat di sudut dinding sempit. Penyebab kenaikan redaman tersebut adalah...",
            "pilihan": [
                {"key": "A", "text": "Macro-bending loss akibat radius lekukan kabel melebihi batas toleransi kelengkungan minimum"},
                {"key": "B", "text": "Arus listrik induksi tegangan tinggi dari dinding semen"},
                {"key": "C", "text": "Frekuensi gelombang radio Wi-Fi yang menembus serat kaca"},
                {"key": "D", "text": "Karat pada permukaan cladding serat optik"},
                {"key": "E", "text": "Kelebihan bandwidth data yang tertahan di sudut belokan"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Bending loss (rugi-rugi lekukan) terjadi saat serat optik ditekuk melebihi batas bending radius minimum, mengakibatkan sudut pantulan internal total cahaya terganggu dan sebagian cahaya bocor keluar dari core."
        }
    },
    "akuntansi": {
        1: {
            "pertanyaan": "Laporan keuangan khusus yang memuat analisis biaya bahan baku, biaya tenaga kerja langsung, dan efisiensi produksi yang disusun untuk kepentingan pimpinan pabrik dalam mengendalikan operasi tergolong dalam bidang...",
            "pilihan": [
                {"key": "A", "text": "Akuntansi Keuangan (Financial Accounting)"},
                {"key": "B", "text": "Akuntansi Manajemen / Biaya (Management/Cost Accounting)"},
                {"key": "C", "text": "Akuntansi Perpajakan (Tax Accounting)"},
                {"key": "D", "text": "Akuntansi Sektor Publik (Government Accounting)"},
                {"key": "E", "text": "Sistem Informasi Akuntansi"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Akuntansi manajemen fokus menyediakan informasi keuangan dan operasional internal untuk pihak manajemen guna perencanaan, penetapan harga, dan pengendalian proses bisnis internal."
        },
        2: {
            "pertanyaan": "Perusahaan jasa 'Klinik Sehat' membeli perlengkapan medis senilai Rp8.000.000 secara kredit dari PT Medika. Pengaruh transaksi tersebut terhadap persamaan dasar akuntansi adalah...",
            "pilihan": [
                {"key": "A", "text": "Aset (Kas) berkurang Rp8.000.000 dan Aset (Perlengkapan) bertambah Rp8.000.000"},
                {"key": "B", "text": "Aset (Perlengkapan) bertambah Rp8.000.000 dan Liabilitas (Utang Usaha) bertambah Rp8.000.000"},
                {"key": "C", "text": "Aset (Perlengkapan) bertambah Rp8.000.000 dan Ekuitas (Modal) berkurang Rp8.000.000"},
                {"key": "D", "text": "Liabilitas (Utang Usaha) berkurang Rp8.000.000 dan Ekuitas bertambah Rp8.000.000"},
                {"key": "E", "text": "Tidak ada perubahan nilai pada komponen aset maupun liabilitas"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Pembelian perlengkapan secara kredit menambah akun Aset (Perlengkapan) di sisi aktiva dan menambah akun Liabilitas (Utang Usaha) di sisi pasiva sebesar nominal yang sama."
        },
        3: {
            "pertanyaan": "Seorang staf akuntansi perusahaan menolak permintaan atasannya untuk mencatat kwitansi pengeluaran pribadi direktur sebagai biaya operasional kantor. Sikap staf tersebut mencerminkan kepatuhan terhadap prinsip dasar etika profesi...",
            "pilihan": [
                {"key": "A", "text": "Kerahasiaan"},
                {"key": "B", "text": "Integritas dan Objektivitas"},
                {"key": "C", "text": "Perilaku Pasif"},
                {"key": "D", "text": "Kompetensi Kehati-hatian Sebagian"},
                {"key": "E", "text": "Loyalitas Tanpa Batas"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Prinsip integritas mewajibkan akuntan bertindak jujur dan adil, sedangkan objektivitas menuntut independensi tanpa membiarkan kompromi kepentingan pribadi mencoreng kebenaran laporan keuangan."
        },
        4: {
            "pertanyaan": "Ketika panen raya padi mengalami kegagalan panen akibat banjir bandang di sentra produksi sementara kebutuhan konsumsi beras nasional tetap tinggi, fenomena ekonomi yang akan terjadi di pasar adalah...",
            "pilihan": [
                {"key": "A", "text": "Terjadi kelangkaan pasokan yang mendorong naiknya harga keseimbangan beras di pasar"},
                {"key": "B", "text": "Harga beras turun drastis karena daya beli masyarakat meningkat"},
                {"key": "C", "text": "Kurva penawaran beras bergeser ke kanan dan stok melimpah"},
                {"key": "D", "text": "Pemerintah menghapus subsidi pupuk seketika"},
                {"key": "E", "text": "Permintaan masyarakat terhadap beras otomatis turun menjadi nol"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Penurunan jumlah pasokan barang dengan tingkat permintaan yang konstan menyebabkan pergeseran kurva supply ke kiri, mengakibatkan kelangkaan barang dan mendongkrak naiknya harga pasar."
        },
        5: {
            "pertanyaan": "Setiap akhir bulan, perusahaan memotong sejumlah uang dari gaji bruto karyawan untuk disetorkan ke kas negara sebagai pajak penghasilan atas upah kerja. Jenis pajak yang dimaksud adalah...",
            "pilihan": [
                {"key": "A", "text": "Pajak Penghasilan (PPh) Pasal 21"},
                {"key": "B", "text": "Pajak Pertambahan Nilai (PPN)"},
                {"key": "C", "text": "Pajak Bumi dan Bangunan (PBB)"},
                {"key": "D", "text": "Pajak Penjualan atas Barang Mewah (PPnBM)"},
                {"key": "E", "text": "Bea Masuk dan Cukai"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "PPh Pasal 21 adalah pajak atas penghasilan berupa gaji, upah, honorarium, tunjangan, dan pembayaran lain sehubungan dengan pekerjaan atau jabatan orang pribadi."
        },
        6: {
            "pertanyaan": "Pada lembar kerja spreadsheet akuntansi, kolom C berisi 'Kuantitas Barang' (Cell C4) dan kolom D berisi 'Harga Pokok per Unit' (Cell D4). Rumus formula yang benar untuk menghitung total nilai persediaan pada Cell E4 adalah...",
            "pilihan": [
                {"key": "A", "text": "=SUM(C4:D4)"},
                {"key": "B", "text": "=C4*D4"},
                {"key": "C", "text": "=C4/D4"},
                {"key": "D", "text": "=COUNT(C4:D4)"},
                {"key": "E", "text": "=AVERAGE(C4:D4)"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Formula perkalian di Microsoft Excel atau Google Sheets menggunakan operator tanda bintang (*). Total nilai persediaan diperoleh dari perkalian kuantitas dengan harga per unit (=C4*D4)."
        }
    },
    "manajemen_perkantoran": {
        1: {
            "pertanyaan": "Dokumen tertulis resmi yang dikirimkan oleh pihak pembeli kepada pemasok/penjual yang memuat rincian nama barang, tipe spesifikasi, jumlah pesanan, dan tanggal pengiriman yang dikehendaki disebut...",
            "pilihan": [
                {"key": "A", "text": "Kwitansi pelunasan"},
                {"key": "B", "text": "Surat Pesanan (Purchase Order)"},
                {"key": "C", "text": "Faktur penjualan (Invoice)"},
                {"key": "D", "text": "Nota kredit retur barang"},
                {"key": "E", "text": "Surat penagihan utang"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Purchase Order (PO) atau Surat Pesanan adalah dokumen komersial resmi yang diterbitkan pembeli untuk mengikat pemesanan barang/jasa kepada pihak penjual."
        },
        2: {
            "pertanyaan": "Sebuah badan usaha dibentuk oleh dua orang atau lebih, di mana satu orang bertindak sebagai sekutu pengelola yang menanggung risiko hingga harta pribadi, sedangkan pihak lainnya hanya menanamkan modal dengan tanggung jawab terbatas sebesar modal yang disetor. Badan usaha ini berbentuk...",
            "pilihan": [
                {"key": "A", "text": "Perseroan Terbatas (PT)"},
                {"key": "B", "text": "Persekutuan Komanditer (CV)"},
                {"key": "C", "text": "Firma (Fa)"},
                {"key": "D", "text": "Koperasi Simpan Pinjam"},
                {"key": "E", "text": "Perusahaan Umum (Perum)"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Karakteristik persekutuan komanditer (CV) adalah memiliki dua jenis sekutu: sekutu komplementer/aktif (pengelola bertanggung jawab tak terbatas) dan sekutu komanditer/pasif (tanggung jawab terbatas modal)."
        },
        3: {
            "pertanyaan": "Sebuah produsen tas kulit menjual hasil produksinya langsung kepada konsumen akhir melalui gerai butik milik perusahaan di pusat perbelanjaan tanpa perantara agen. Saluran distribusi yang diterapkan adalah...",
            "pilihan": [
                {"key": "A", "text": "Saluran distribusi langsung (Direct Channel)"},
                {"key": "B", "text": "Saluran distribusi bertingkat grosir-pengecer"},
                {"key": "C", "text": "Saluran distribusi eksklusif konsinyasi"},
                {"key": "D", "text": "Saluran distribusi dropship daring"},
                {"key": "E", "text": "Saluran distribusi waralaba terbuka"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Distribusi langsung (Direct Channel / Zero-level channel) adalah penyaluran produk dari produsen secara langsung ke tangan konsumen akhir tanpa melibatkan pedagang perantara."
        },
        4: {
            "pertanyaan": "Seorang staf administrasi yang bertugas mengetik naskah laporan selama jam kerja sering mengeluhkan nyeri pergelangan tangan dan otot leher tegang. Langkah penataan ergonomi lingkungan kerja kantor yang paling tepat adalah...",
            "pilihan": [
                {"key": "A", "text": "Mengatur posisi monitor sejajar mata, posisi siku membentuk sudut 90 derajat di meja, dan melakukan peregangan berkala"},
                {"key": "B", "text": "Menambah kecepatan mengetik agar pekerjaan lebih cepat selesai"},
                {"key": "C", "text": "Meletakkan keyboard di atas pangkuan saat mengetik"},
                {"key": "D", "text": "Mematikan lampu ruangan dan bekerja hanya dengan cahaya monitor"},
                {"key": "E", "text": "Mengganjal monitor dengan buku tebal hingga posisi kepala mendongak"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Prinsip ergonomi perkantoran meliputi penataan posisi duduk tegak, sudut siku 90°, penempatan monitor sejajar pandangan mata alami, serta peregangan otot rutin untuk mencegah Repetitive Strain Injury (RSI)."
        },
        5: {
            "pertanyaan": "Dalam sistem kearsipan pola abjad (alphabetical filing system), surat dinas yang berasal dari instansi 'Kementerian Perhubungan Republik Indonesia' akan diindeks dengan unit utama kata tangkap...",
            "pilihan": [
                {"key": "A", "text": "Perhubungan, Kementerian"},
                {"key": "B", "text": "Kementerian, Perhubungan"},
                {"key": "C", "text": "Republik, Indonesia"},
                {"key": "D", "text": "Indonesia, Perhubungan"},
                {"key": "E", "text": "Dinas, Perhubungan"}
            ],
            "kunci": "A",
            "pembahasan_singkat": "Berdasarkan pedoman kearsipan nasional, indeks nama lembaga pemerintah mengutamakan bidang tugas/urusan kementerian sebagai Unit 1 (Perhubungan), diikuti nama badan lembaganya (Kementerian)."
        },
        6: {
            "pertanyaan": "Seorang pelanggan mengajukan komplain dengan nada marah di kolom komentar media sosial perusahaan perihal keterlambatan konfirmasi pengiriman barang. Sikap profesional staf humas kantor yang paling tepat adalah...",
            "pilihan": [
                {"key": "A", "text": "Menghapus komentar komplain tersebut agar tidak dibaca oleh pengguna lain"},
                {"key": "B", "text": "Menanggapi dengan empati, meminta maaf atas ketidaknyamanan, dan mengarahkan penyelesaian melalui kanal pesan pribadi (DM)"},
                {"key": "C", "text": "Membalas komentar dengan menyalahkan pihak kurir ekspedisi di depan umum"},
                {"key": "D", "text": "Memblokir akun pelanggan tersebut agar tidak dapat berkomentar lagi"},
                {"key": "E", "text": "Membiarkan komentar tersebut tanpa memberikan tanggapan apapun"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Etika pelayanan pelanggan digital menuntut respons cepat, permohonan maaf sopan, klarifikasi empatik, serta pengalihan ke kanal komunikasi pribadi demi menjaga privasi data pesanan pelanggan dan reputasi korporasi."
        }
    },
    "teknik_mesin": {
        6: {
            "pertanyaan": "Seorang teknisi mesin bubut mengukur diameter poros benda kerja menggunakan mikrometer luar (outside micrometer) dengan ketelitian 0,01 mm. Pada skala utama tabung terlihat garis 24,5 mm dan skala putar thimble menunjukkan garis ke-28 tepat segaris dengan sumbu utama. Hasil pengukuran diameter poros tersebut adalah...",
            "pilihan": [
                {"key": "A", "text": "24,28 mm"},
                {"key": "B", "text": "24,78 mm"},
                {"key": "C", "text": "24,50 mm"},
                {"key": "D", "text": "24,88 mm"},
                {"key": "E", "text": "25,28 mm"}
            ],
            "kunci": "B",
            "pembahasan_singkat": "Hasil pembacaan mikrometer = Skala Utama + (Skala Nonius × 0,01 mm) = 24,50 mm + (28 × 0,01 mm) = 24,50 + 0,28 = 24,78 mm."
        }
    }
}

def inject():
    total_injected = 0
    for sub, questions in SOAL_SERUPA_DATA.items():
        filepath = os.path.join(BASE_DIR, "data", f"{sub}_paket_1_learning.json")
        if not os.path.exists(filepath):
            print("File not found:", filepath)
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for q in data["soal"]:
            num = q["nomor"]
            if num in questions:
                q["soal_serupa"] = questions[num]
                total_injected += 1
                
        # Perbaiki rel_path gambar akuntansi jika ada
        if sub == "akuntansi":
            for q in data["soal"]:
                for im in q.get("stimulus", {}).get("images", []):
                    if "86854_" in str(im.get("filename", "")) and not im.get("rel_path"):
                        im["rel_path"] = f"images/{im['filename']}"
                        print("  -> Fixed rel_path for akuntansi image 86854_")
                        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Sukses injeksi {sub}: {len(questions)} soal serupa.")
        
    print(f"\n[TOTAL BERHASIL] {total_injected} soal serupa terinjeksi 100%!")

if __name__ == "__main__":
    inject()
