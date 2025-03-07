# HahaWallet Multi-Account Auto Claimer

HahaWallet Multi-Account Auto Claimer adalah alat otomatis untuk melakukan check-in harian dan klaim reward di platform HahaWallet. Script ini mendukung penggunaan banyak akun dan dapat berjalan dengan atau tanpa proxy.

## Fitur
- **Login Otomatis**: Masuk ke akun HahaWallet dengan kredensial yang disimpan.
- **Check-in Harian**: Memeriksa dan mengklaim check-in harian secara otomatis.
- **Dukungan Proxy**: Bisa berjalan dengan proxy gratis, proxy pribadi, atau tanpa proxy.
- **Multi-threading**: Proses akun secara bersamaan untuk efisiensi lebih tinggi.
- **Progress Bar**: Menampilkan kemajuan pemrosesan akun dengan `tqdm`.
- **Error Handling yang Baik**: Menangani kesalahan dan rotasi proxy jika diperlukan.

## Persyaratan
Sebelum menjalankan script, pastikan Anda telah menginstal dependensi yang diperlukan:

```sh
pip install -r requirements.txt
```

Atau instal manual:

```sh
pip install aiohttp aiohttp_socks fake_useragent colorama tqdm pytz
```

Cara Penggunaan

1. **Siapkan Akun**
Buat file accounts.txt dan isi dengan daftar akun dalam format:

email1@example.com|password1
email2@example.com|password2


2. **Siapkan Proxy** (Opsional)

Jika menggunakan proxy pribadi, buat file proxy.txt dan isi daftar proxy dengan format:

http://user:pass@host:port
socks5://host:port

Jika memilih proxy gratis, script akan mengunduh daftar proxy otomatis.



3. **Jalankan Script**
Jalankan script dengan perintah:

```sh
python bot.py
```

4. **Pilih Mode Proxy**
Setelah menjalankan script, Anda akan diminta untuk memilih mode proxy:

- 1 Jalankan dengan proxy sharing
- 2 Jalankan dengan Proxy Pribadi
- 3 Jalankan tanpa Proxy


---

## 📜 Lisensi  

Script ini didistribusikan untuk keperluan pembelajaran dan pengujian. Penggunaan di luar tanggung jawab pengembang.  

Untuk update terbaru, bergabunglah di grup **Telegram**: [Klik di sini](https://t.me/sentineldiscus).


---

## 💡 Disclaimer
Penggunaan bot ini sepenuhnya tanggung jawab pengguna. Kami tidak bertanggung jawab atas penyalahgunaan skrip ini.
