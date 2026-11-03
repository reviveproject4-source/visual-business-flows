# End-of-Day POS Reconciliation, Blind Balancing & Anti-Theft Flow

> **Domain:** Brick-and-Mortar Retail, F&B, Supermarket, Franchise POS  
> **Core Mission:** Menghilangkan kebocoran uang kasir (*cash leakage*), mencegah manipulasi nota (*Void Fraud*), dan memangkas waktu tutup buku dari 2 jam menjadi 15 menit.

---

## 1. Masalah Nyata & Risiko Kecurangan di Lapangan

Di bisnis kasir nyata, kebocoran uang paling sering terjadi lewat **3 celah sistem**:
1. **Modus Void Fraud:** Kasir melayani pembeli tunai, uang diterima, tetapi setelah pembeli pergi, kasir membatalkan (*void*) transaksi di sistem dan mengantongi uangnya.
2. **Hitungan Terbuka (Open Count):** Kasir melihat angka penjualan di layar komputer terlebih dahulu, lalu mencocok-cocokkan uang fisik di laci agar terlihat pas.
3. **Selisih yang Disembunyikan:** Selisih kas ditutupi dengan uang tip pelanggan tanpa pernah tercatat di laporan keuangan resmi.

---

## 2. Diagram Alur Sistem: "Blind Count & Dual-PIN Audit"

Alur ini menerapkan prinsip perbankan modern: **Kasir sama sekali tidak boleh melihat total uang sistem sebelum menghitung uang fisik secara murni (*Blind Balancing*)**.

```mermaid
sequenceDiagram
    autonumber
    actor Cashier as Kasir (Operator Shift)
    participant POS as Terminal POS Software
    participant Drawer as Laci Kas Fisik
    actor Manager as Supervisor / Pemilik Toko
    participant Accounting as Jurnal Akuntansi (Cloud DB)

    Note over Cashier,POS: TAHAP 1: FREEZE OPERASIONAL
    Cashier->>POS: Klik "Tutup Shift / Rekonsiliasi Akhir Hari"
    POS->>POS: Kunci terminal (Cegah input transaksi baru atau void)
    POS->>POS: Hitung Total Penjualan Sistem Otomatis (A) = Cash + QRIS + EDC Card
    
    Note over Cashier,Drawer: TAHAP 2: BLIND CASH COUNT (Hitung Buta)
    Note over Cashier,POS: Layar POS TIDAK MENAMPILKAN angka (A) agar kasir tidak curang
    Cashier->>Drawer: Hitung fisik uang kertas, koin, dan struk EDC
    Cashier->>POS: Input rincian fisik: lembar 100rb, 50rb, 20rb, dll. (B)
    
    Note over POS: TAHAP 3: EVALUASI VARIANCE (SELISIH)
    POS->>POS: Hitung Selisih: Discrepancy = B - A
    
    alt Selisih == Rp 0 (Balance Sempurna)
        POS->>Accounting: Catat Status: "SHIFT_BALANCED" ($0.00 Variance)
        POS-->>Cashier: Cetak Struk Tutup Kasir & Buka Kunci Laci untuk Setoran
    else Selisih != Rp 0 (Uang Kurang atau Lebih)
        POS->>POS: Kunci layar merah: "SELISIH KAS TERDETEKSI"
        POS->>Manager: Kirim Notifikasi WhatsApp/Push Alert: Selisih Rp X di Register #1
        Manager->>Drawer: Dampingi Kasir Hitung Ulang Fisik Bersama
        
        alt Salah Hitung Kasir (Setelah hitung ulang ternyata pas)
            Cashier->>POS: Koreksi Angka Hitungan Fisik
            POS->>Accounting: Catat Status: "BALANCED_AFTER_RECOUNT"
        else Selisih Riil Terbukti (Uang Fisik Memang Hilang / Berlebih)
            Manager->>POS: Input PIN Supervisor + Alasan Wajib (Memo Investigasi)
            POS->>Accounting: Masukkan Selisih ke Akun Beban "Cash Over/Short"
            POS->>Accounting: Catat Log Audit: ID Kasir, ID Supervisor, Nominal Selisih, Jam
            POS-->>Cashier: Cetak Lembar Berita Acara Selisih Kasir (Wajib TTD Kasir & Manager)
            POS-->>Manager: Arsipkan Laporan Discrepancy untuk Evaluasi Gaji / SOP
        end
    end
```

---

## 3. Checklist Aturan Sistem (Untuk Programmer & Tim Bisnis)

* [ ] **Aturan Blind Screen:** Sebelum kasir menekan tombol "Submit Hitungan Fisik", layar POS wajib disamarkan (*masked*). Tidak boleh ada angka target penjualan yang terlihat.
* [ ] **Aturan Anti-Void Pasca Tutup:** Tombol pembatalan (*void*) otomatis dinonaktifkan permanen saat proses rekonsiliasi kasir dimulai.
* [ ] **Pemisahan Akun Akuntansi:** Uang lebih (*cash overage*) tidak boleh dipakai menutup uang kurang (*cash shortage*). Keduanya harus masuk ke buku akun "Selisih Kas" secara transparan.

---

## 4. Dampak Operasional bagi Bisnis

* **Kebocoran Kas Turun Hingga 98%:** Kasir tidak bisa memanipulasi angka karena tidak tahu berapa angka riil yang sedang ditunggu oleh sistem komputer.
* **Audit Trail Jelas:** Pemilik toko yang tidak berada di lokasi langsung tahu detik itu juga jika ada selisih kas di toko cabang tanpa perlu menunggu laporan bulanan.
