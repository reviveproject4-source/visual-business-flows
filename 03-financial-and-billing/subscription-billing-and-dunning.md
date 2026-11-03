# SaaS Subscription Billing, Smart Dunning & Involuntary Churn Recovery Flow

> **Domain:** Subscription SaaS, Membership Digital, B2B Cloud Platform  
> **Core Mission:** Menyelamatkan 30-40% pendapatan langganan yang hilang akibat gagal bayar otomatis (*Involuntary Churn*), kartu kredit kedaluwarsa, atau saldo tidak cukup.

---

## 1. Masalah Nyata & Risiko Pendapatan di Lapangan

Di bisnis model langganan (SaaS / Membership), musuh terbesar bisnis bukanlah pelanggan yang berhenti secara sadar (*voluntary churn*), melainkan **Involuntary Churn**:
1. Pelanggan sebenarnya masih ingin memakai software Anda, tapi **kartu kredit mereka bermasalah / saldo sedang kosong saat sistem menagih**.
2. **Kesalahan Fatal Banyak Developer:** Begitu kartu gagal di-charge pada jam 00:00 tanggal 1, sistem langsung mematikan akun pelanggan. Pelanggan kaget, marah, dan akhirnya pindah ke kompetitor.
3. Menagih ulang di waktu yang salah (misalnya jam 2 pagi di akhir bulan saat saldo bank belum gajian) hanya akan menghabiskan batas kuota *retry* payment gateway.

---

## 2. Diagram Alur Sistem: "Smart Multi-Schedule Dunning Protocol"

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Mesin Penagihan Berkala
    participant Gateway as Stripe / Payment Gateway
    participant Customer as Pelanggan / Subscriber
    participant Notifier as WhatsApp & Email Notifikasi
    participant AppAccess as Kontrol Akses Software

    Note over Engine,Gateway: HARI KE-0: TAGIHAN JATUH TEMPO
    Engine->>Gateway: Eksekusi Tagihan Bulanan ($49)
    Gateway-->>Engine: GAGAL: `insufficient_funds` (Saldo Belum Ada)
    
    Note over Engine,AppAccess: TAHAP GRACE PERIOD (Akses Tetap Dibuka!)
    Engine->>AppAccess: Set Status: "GRACE_PERIOD_DAY_1" (Fitur 100% Tetap Berjalan)
    Engine->>Notifier: Kirim Email Santai: "Hai [Nama], pembayaran bulananmu belum berhasil. Kami akan coba lagi otomatis."
    
    Note over Engine: SMART WAIT 3 HARI (Menunggu Pola Pengisian Saldo/Gajian)
    Engine->>Gateway: RETRY #1 (Hari ke-3, Pukul 10:00 Pagi Waktu Lokal)
    alt Retry #1 Berhasil
        Gateway-->>Engine: Tagihan Sukses Dipotong ($49)
        Engine->>AppAccess: Kembalikan Status: "ACTIVE_NORMAL"
        Engine->>Notifier: Kirim Tanda Terima & Ucapan Terima Kasih
    else Retry #1 Masih Gagal
        Engine->>AppAccess: Aktifkan "SOFT_BLOCK BANNER" (Hanya Banner Peringatan di Dashboard)
        Engine->>Notifier: Kirim WhatsApp + Email Link Update Kartu Baru
        
        Note over Engine: SMART WAIT 4 HARI (Hari ke-7)
        Engine->>Gateway: RETRY #2 (Hari ke-7, Pukul 14:00 Siang)
        alt Retry #2 Berhasil
            Gateway-->>Engine: Tagihan Berhasil Di-recover!
            Engine->>AppAccess: Hilangkan Banner Peringatan
        else Retry #2 Masih Gagal
            Note over Engine,AppAccess: TAHAP HARD-BLOCK (Setelah 14 Hari Toleransi)
            Engine->>AppAccess: Ubah Akses ke "READ_ONLY" (Hanya Bisa Lihat Data, Tidak Bisa Tambah Data Baru)
            Engine->>Notifier: Email Urgent: "Akses akun Anda dibatasi sementara. Klik di sini untuk memulihkan dalam 1 klik."
            
            Note over Engine: WAIT HARI KE-30
            alt Pelanggan Memperbarui Kartu
                Customer->>AppAccess: Klik Update Kartu & Bayar Tagihan Tertunda
                AppAccess->>Gateway: Charge Kartu Baru Sukses
                AppAccess-->>Customer: Akses Full Otomatis Terbuka Seketika
            else Melewati 30 Hari Tanpa Respon
                Engine->>AppAccess: Set Status: "CHURNED_CANCELLED" (Arsipkan Data Pelanggan)
            end
        end
    end
```

---

## 3. Checklist Aturan Sistem (Untuk Programmer & Tim Bisnis)

* [ ] **Aturan Waktu Penagihan Pintar (Smart Scheduling):** Hindari mencoba penagihan ulang di jam tidur (tengah malam). Jadwalkan *retry* pada jam 10:00 pagi atau 14:00 siang waktu lokal saat orang cenderung mengecek rekening atau baru transfer uang.
* [ ] **Prinsip Grace Period (Masa Tenggang):** Jangan pernah mematikan akun pelanggan di hari pertama pembayaran gagal. Berikan minimal 7 hingga 14 hari masa tenggang dengan banner peringatan sopan di dalam aplikasi.
* [ ] **Satu Klik Update Kartu:** Email penagihan (*dunning email*) harus langsung memiliki tautan aman (*magic link*) langsung ke halaman ganti kartu tanpa mengharuskan pelanggan login ulang dengan password yang mungkin mereka lupa.

---

## 4. Dampak Operasional bagi Bisnis

* **Menyelamatkan 30% Hingga 40% Pendapatan Bulanan (MRR):** Bisnis tidak kehilangan pelanggan setia hanya karena masalah sepele seperti tanggal kartu kredit kedaluwarsa atau keterlambatan transfer saldo.
* **Tingkat Kepuasan Pelanggan Tetap Tinggi:** Pelanggan tidak merasa diperlakukan kasar atau langsung diusir dari aplikasi ketika sedang ada kendala teknis pada bank mereka.
