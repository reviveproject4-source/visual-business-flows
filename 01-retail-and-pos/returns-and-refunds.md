# Customer Return, Defect Quarantine & Anti-Return Fraud Flow

> **Domain:** Retail, E-Commerce, Consumer Electronics, Fashion  
> **Core Mission:** Menghilangkan kejahatan retur barang palsu/rusak (*Return Fraud*), membedakan karantina barang cacat pabrik vs barang layak jual, dan menjaga keakuratan stok akuntansi.

---

## 1. Masalah Nyata & Risiko Kerugian di Lapangan

Retur barang adalah lubang hitam kebocoran biaya bagi bisnis ritel:
1. **Wardrobing / Pemakaian Sepintas:** Pelanggan membeli baju/elektronik untuk dipakai di satu pesta/acara, lalu mereturnya ke toko pura-pura tidak suka.
2. **Switching Fraud (Tukar Barang):** Pelanggan membeli barang baru original, tetapi mengembalikan barang lama mereka yang sudah rusak dengan kotak barang baru.
3. **Ghost Return (Retur Hantu):** Kasir nakal membuat retur palsu di komputer seolah-olah ada pelanggan yang meretur barang, lalu kasir mengambil uang tunai pengembalian dari laci kasir.

---

## 2. Diagram Alur Sistem: "3-Way Inspection & Quarantine Protocol"

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Pelanggan
    actor Staff as Staf Toko (Frontline)
    participant POS as Terminal POS
    participant QC as Staf QC / Supervisor Gudang
    participant Inventory as Database Stok (WMS)
    participant Accounting as Jurnal Keuangan & Refund

    Customer->>Staff: Ajukan Retur Barang + Nota Asli / E-Receipt
    Staff->>POS: Scan Barcode Nota / Nomor Invoice
    
    alt Nota Tidak Ditemukan ATAU Usia Nota > 14 Hari
        POS-->>Staff: "RETURN_EXPIRED_OR_INVALID"
        Staff-->>Customer: Tolak Pengajuan Sesuai Kebijakan Garansi Toko
    else Nota Valid Ditemukan
        POS-->>Staff: Tampilkan Data Asli: Serial Number, Foto Barang, Tanggal Beli
        Staff->>Staff: Verifikasi Fisik Segel, Tag Harga, dan Serial Number Unit
        
        alt Serial Number Berbeda ATAU Cacat Akibat Kelalaian Pembeli
            Staff-->>Customer: Retur Ditolak (Alasan: Kerusakan Akibat Kelalaian Pengguna)
        else Fisik & Serial Number Cocok
            Staff->>POS: Buka Tiket Retur #RET-882 (Input Alasan Retur)
            Staff->>QC: Serahkan Unit untuk Klasifikasi Kondisi Barang
            
            alt KATEGORI A: Barang Masih Baru & Segel Utuh (Resellable)
                QC->>Inventory: Masukkan Kembali ke Stok Siap Jual (Gudang Utama)
                QC->>POS: Konfirmasi Status: "RESTOCKED_TO_SHELF"
            else KATEGORI B: Cacat Pabrik / Rusak Ringan (Defective Unit)
                QC->>Inventory: Pindahkan ke "Buffer Karantina Klaim Pabrik/Supplier"
                QC->>POS: Konfirmasi Status: "DEFECT_QUARANTINED"
            end

            Note over POS,Customer: TAHAP RESOLUSI FINANSIAL
            POS->>Customer: Pilihan Metode Pengembalian:
            
            alt Pilihan 1: Tukar Unit Baru yang Sama
                POS->>Inventory: Potong Stok Unit Pengganti (-1)
                Staff-->>Customer: Serahkan Unit Baru + Nota Penggantian
            else Pilihan 2: Store Credit / Voucher Digital (+ Bonus 5%)
                POS->>Accounting: Terbitkan Voucher Belanja Digital
                Staff-->>Customer: Kirim Kode Voucher Belanja via SMS/WhatsApp
            else Pilihan 3: Pengembalian Uang Asli (Bank Transfer / Card Reversal)
                POS->>Accounting: Terbitkan Instruksi Refund Otomatis
                Accounting-->>Customer: Dana Masuk Rekening (Sesuai Metode Pembayaran Awal)
            end
            
            POS->>Accounting: Tutup Tiket Retur & Catat Pemotongan Pajak Penjualan
        end
    end
```

---

## 3. Checklist Aturan Sistem (Untuk Tim Programmer & Bisnis)

* [ ] **Aturan Anti Ghost Return:** Setiap transaksi retur wajib mencantumkan Nomor Seri Produk (*Serial Number*) dan Foto Bukti Fisik Barang yang diunggah kasir ke sistem.
* [ ] **Pemisahan Lokasi Gudang:** Barang retur yang cacat pabrik **dilarang keras** langsung menambah stok jual di kasir. Sistem harus otomatis memasukkannya ke ID Gudang Karantina agar tidak terambil oleh kasir lain untuk dijual ke pembeli berikutnya.
* [ ] **Incentive Store Credit:** Tawarkan opsi *Store Credit* (Voucher Belanja) dengan tambahan bonus 5% daripada pengembalian uang tunai, agar uang tetap berputar di dalam bisnis Anda.

---

## 4. Dampak Operasional bagi Bisnis

* **Mencegah Kerugian Barang Rusak:** Toko tidak akan pernah salah menjual barang cacat bekas returan ke pelanggan baru yang bisa merusak nama baik merek.
* **Mencegah Kasir "Mencuri Lewat Retur Palsu":** Karena setiap retur membutuhkan pencocokan nomor invoice lama dan fisik serial number barang.
