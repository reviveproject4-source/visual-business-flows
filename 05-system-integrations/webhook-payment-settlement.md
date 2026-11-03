# Payment Webhook, Offline Network Drop & Zero-Loss Recovery Flow

> **Domain:** Payment Gateway (QRIS, Midtrans, Stripe, OVO/GoPay), POS Kasir, E-Commerce  
> **Core Mission:** Menyelamatkan toko dari situasi kritis ketika pelanggan sudah membayar (uang terpotong di m-Banking/QRIS), tetapi internet di kasir mendadak mati sehingga pesanan dianggap belum bayar.

---

## 1. Masalah Nyata & Situasi Panik di Meja Kasir

Kekacauan paling sering terjadi di kasir modern:
1. **Internet Kasir Tiba-Tiba Putus (Network Drop):** Pembeli melakukan scan QRIS, saldo rekening pembeli sudah terpotong Rp 150.000. Tapi wifi kasir mendadak mati. Kasir menolak memberikan barang karena di layar kasir statusnya masih *"Menunggu Pembayaran"*. Pembeli marah karena merasa sudah bayar.
2. **Double Charge (Terdebet Dua Kali):** Karena panik nota tidak keluar, kasir menyuruh pembeli scan QRIS sekali lagi. Akhirnya uang pembeli terpotong dua kali.
3. **Webhook Terlambat Tiba:** Notifikasi dari bank baru tiba 10 menit kemudian setelah pembeli meninggalkan toko.

---

## 2. Diagram Alur Sistem: "Resilient Offline-Ready Payment Protocol"

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Pembeli (m-Banking)
    actor Cashier as Kasir Toko
    participant POS as Terminal POS Lokal
    participant CloudGateway as Server Cloud & Payment Gateway
    participant Bank as Server Bank / QRIS Network

    Cashier->>POS: Buka Tagihan: Rp 150.000 (Generate Dinamis QRIS)
    POS->>CloudGateway: Request QRIS dengan Idempotency Key: `TX-8821-SAFE`
    CloudGateway-->>POS: Tampilkan QR Code di Layar Pelanggan
    
    Customer->>Bank: Scan & Bayar via m-Banking Pelanggan
    Bank->>CloudGateway: Bank Konfirmasi Dana Sukses Diterima
    
    Note over POS: SITUASI KRITIS: KONEKSI INTERNET KASIR MATI TOTAL!
    CloudGateway-xPOS: Webhook Dikirim tapi Gagal Tembus ke Layar Kasir (Network Drop)
    
    Note over Cashier,Customer: TAHAP RESOLUSI DI KASIR TANPA KEKACAUAN
    Customer->>Cashier: Tunjukkan Bukti Struk Hijau Berhasil di Layar HP Pembeli
    
    Cashier->>POS: Klik Tombol Darurat: "Validasi Pembayaran Manual / Offline"
    Cashier->>POS: Input 4 Digit Terakhir Nomor Referensi Bank dari HP Pembeli
    
    POS->>POS: Simpan Transaksi Sementara dalam "PENDING_OFFLINE_BUFFER"
    POS-->>Cashier: Cetak Nota Sementara: "STATUS: DIVERIFIKASI DENGAN REF BANK"
    Cashier-->>Customer: Serahkan Barang ke Pembeli (Pembeli Pulang dengan Senang)
    
    Note over POS,CloudGateway: TAHAP REKONSILIASI OTOMATIS (Saat Internet Kasir Nyala Kembali)
    POS->>POS: Mendeteksi Koneksi Internet Aktif Kembali
    POS->>CloudGateway: Sinkronisasi: Cocokkan ID `TX-8821-SAFE` dengan Webhook Bank Tertunda
    CloudGateway-->>POS: Konfirmasi Valid: Dana Rp 150.000 Memang Sudah Masuk Rekening Toko
    POS->>POS: Ubah Status Nota Menjadi "LUNAS_PERMANEN" (Closed Reconciliation)
```

---

## 3. Checklist Aturan Sistem (Untuk Tim Programmer & Bisnis)

* [ ] **Kunci Unik Idempotency Key:** Setiap kode QRIS atau tagihan kartu wajib memiliki *Idempotency-Key* unik per transaksi. Jika kasir mencoba mengklik cetak ulang, sistem dilarang keras membuat QR baru yang bisa membuat pembeli terdebet dua kali.
* [ ] **Fitur Validasi Referensi Bank di Kasir:** Berikan kasir tombol khusus untuk memasukkan nomor referensi bank (*RRN / Retrieval Reference Number*) dari HP pelanggan, sehingga barang bisa langsung diserahkan tanpa harus menunggu internet hidup kembali.
* [ ] **Antrean Sinkronisasi Latar Belakang (Background Queue):** Begitu internet kasir kembali stabil, terminal POS otomatis melakukan penyisiran (*polling*) ke server pusat untuk melunaskan transaksi-transaksi yang sempat tersangkut di mode offline.

---

## 4. Dampak Operasional bagi Bisnis

* **Menyelamatkan Reputasi Toko:** Nol keributan di depan meja kasir saat jaringan operator internet sedang *down*.
* **Nol Kerugian Finansial:** Toko tetap aman karena nomor referensi bank dicatat secara valid di dalam database kasir dan otomatis dicocokkan kembali dengan rekening koran bank saat internet kembali online.
