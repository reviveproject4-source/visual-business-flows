# Inter-Branch Inventory Transfer, Transit Shrinkage & Anti-Loss Flow

> **Domain:** Multi-Store Retail Chain, Franchise, Pergudangan Terdistribusi  
> **Core Mission:** Menghilangkan perselisihan antar kepala cabang toko ("Toko Asal kirim 100, tapi Toko Tujuan mengaku cuma terima 90"), serta melacak pertanggungjawaban barang hilang saat pengiriman di jalan.

---

## 1. Masalah Nyata & Risiko Kerugian di Lapangan

Di bisnis ritel dengan banyak cabang toko, perpindahan barang antar toko adalah sarang kebocoran stok:
1. **Saling Lempar Tanggung Jawab:** Toko A mengklaim sudah mengirim 50 pcs kopi mahal. Toko B mengklaim saat kardus dibuka hanya ada 45 pcs. Siapa yang bersalah? Kasir Toko A, Kasir Toko B, atau kurir mobil box yang mencuri 5 pcs di perjalanan?
2. **Stok Mengambang (Ghost Inventory):** Barang yang keluar dari Toko A langsung dihapus dari sistem, padahal butuh waktu 3 hari sampai di Toko B. Selama 3 hari itu, sistem tidak tahu di mana barang berada.

---

## 2. Diagram Alur Sistem: "Dual-Scan In-Transit Buffer Protocol"

```mermaid
sequenceDiagram
    autonumber
    actor StoreA as Kepala Toko A (Asal)
    actor Driver as Driver Ekspedisi / Kurir Internal
    actor StoreB as Kepala Toko B (Tujuan)
    participant WMS as Database Stok Pusat (Cloud)

    Note over StoreA,WMS: TAHAP 1: PERMINTAAN & PENGEMASAN
    StoreA->>WMS: Buka Surat Jalan Transfer Antar Cabang (SJ-901: 50 Unit)
    StoreA->>StoreA: Kemas Barang ke Kotak & Pasang Segel Barcode Unik (Segel #SG-4412)
    StoreA->>WMS: Potong Stok Toko A (-50) -> Masukkan ke "STOK_DALAM_PERJALANAN"
    
    Note over StoreA,Driver: TAHAP 2: SERAH TERIMA EXPEDISI
    Driver->>StoreA: Datang ke Toko A untuk Ambil Barang
    Driver->>Driver: Periksa Keutuhan Nomor Segel Fisik (#SG-4412)
    Driver->>WMS: Scan QR Surat Jalan: Konfirmasi Driver Telah Mengambil Paket Utuh
    
    Note over Driver,WMS: TAHAP 3: PERJALANAN DI JALAN
    Note over WMS: Sistem mencatat: Tanggung Jawab Barang Berada 100% pada Driver
    
    Note over Driver,StoreB: TAHAP 4: PENERIMAAN DI TOKO B
    Driver->>StoreB: Tiba di Toko B & Menyerahkan Paket
    StoreB->>StoreB: Periksa Nomor Segel Fisik: Apakah Segel Rusak / Pernah Dibuka?
    
    alt Segel Fisik Terbukti Rusak / Terbuka
        StoreB->>WMS: Foto Segel Rusak & Wajib Buka Kardus di Depan Driver
    end

    StoreB->>WMS: Scan Barcode Tiap Satuan Unit Produk (Hitung Fisik Masuk)
    
    alt Hitungan Fisik Cocok Sempurna (50 Unit)
        StoreB->>WMS: Konfirmasi Penerimaan Penuh (Status: COMPLETED)
        WMS->>WMS: Pindahkan dari "STOK_DALAM_PERJALANAN" ke "STOK_AKTIF_TOKO_B" (+50)
    else Hitungan Fisik Kurang (Hanya 47 Unit Ditemukan, Kurang 3 Unit)
        StoreB->>WMS: Input Catatan Selisih: "Diterima 47, Hilang 3 Unit"
        WMS->>WMS: Pindahkan 47 Unit ke "STOK_AKTIF_TOKO_B"
        WMS->>WMS: Pindahkan 3 Unit ke Akun Beban "KERUSAKAN_LOGISTIK_DRIVER"
        WMS-->>StoreA: Notifikasi Otomatis: Surat Jalan Ditutup dengan Selisih
        WMS-->>Driver: Surat Berita Acara Potong Klaim Pengiriman
    end
```

---

## 3. Checklist Aturan Sistem (Untuk Programmer & Tim Bisnis)

* [ ] **Aturan Status 'In-Transit':** Barang yang keluar dari Toko A tidak boleh langsung dianggap "sudah sampai di Toko B". Wajib ada wadah status khusus *In-Transit Buffer* agar nilai aset perusahaan tidak hilang di laporan neraca harian.
* [ ] **Aturan Segel Bernomor (Tamper-Evident Seal):** Setiap kardus transfer wajib memiliki nomor segel pengaman. Jika nomor segel saat sampai di Toko B tidak cocok dengan nomor segel yang diinput Toko A, sistem otomatis membunyikan alarm audit investigasi.
* [ ] **Tanda Tangan Digital Driver:** Driver pengirim wajib melakukan konfirmasi serah terima di aplikasi sebelum meninggalkan Toko Asal, sehingga titik pertanggungjawaban hukum barang jelas.

---

## 4. Dampak Operasional bagi Bisnis

* **Nol Perselisihan Antar Toko Cabang:** Tidak ada lagi drama saling tuduh antar kepala cabang, karena titik kebocoran barang terlacak dengan bukti digital segel dan barcode.
* **Pertanggungjawaban Finansial Akurat:** Jika barang hilang karena dicuri sopir di jalan, kerugian otomatis dibebankan ke vendor ekspedisi atau klaim asuransi pengiriman secara otomatis.
