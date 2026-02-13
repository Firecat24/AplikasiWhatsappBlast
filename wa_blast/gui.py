import tkinter as tk
import logic, sys, threading, os, chrome_profile, time
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from login_checker import cek_status_login
from chrome_profile import get_chrome_profiles

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # CEK PENTING: Apakah widget teks masih ada/hidup?
        try:
            if self.text_widget.winfo_exists():
                self.text_widget.insert(tk.END, string)  # Tampilkan teks
                self.text_widget.see(tk.END)  # Auto-scroll
            else:
                # Jika GUI sudah mati, alihkan print ke terminal biasa (console)
                # biar error gak numpuk
                sys.__stdout__.write(string)
        except Exception:
            # Kalau ada error aneh lainnya, buang saja ke terminal asli
            sys.__stdout__.write(string)

    def flush(self):
        pass

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Whatsapp Blast DMU")
        self.root.geometry("500x950")
        self.root.resizable(False, False)
        icon_path = os.path.join(os.path.dirname(__file__), 'icon', 'icon.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"[WARNING] Icon file not found at: {icon_path}")
        self.profiles = get_chrome_profiles()

        # Variabel untuk menyimpan path file
        self.path_gambar = ""
        self.path_excel = ""

        # Input teks
        tk.Label(self.root, text="Masukkan text:").pack(pady=5)
        self.entry_nama = tk.Text(self.root, width=70, height=12)  # Lebar & tinggi diperbesar
        self.entry_nama.pack(pady=5, padx=10)

        #frame utama
        self.frame_utama = tk.Frame(self.root)
        self.frame_utama.pack(pady=10)

        #frame kiri
        self.frame_kiri = tk.Frame(self.frame_utama, borderwidth=1, relief="solid")
        self.frame_kiri.pack(side="left" ,pady=5, padx=5)

        #frame kanan
        self.frame_kanan = tk.Frame(self.frame_utama)
        self.frame_kanan.pack(side="right",pady=5, padx=5)

        # Dropdown (Opsi Pilihan)
        self.profiles_dict = chrome_profile.get_chrome_profiles()
        self.profile_names = list(self.profiles_dict.keys())

        tk.Label(self.frame_kiri, text="Pilih Opsi:").pack(pady=5)
        self.combo_box = ttk.Combobox(self.frame_kiri, values=self.profile_names, state="readonly")
        self.combo_box.pack(pady=5, padx=5)
        self.combo_box.current(0)

        self.combo_box.bind("<<ComboboxSelected>>", self.cek_status)
        self.status_label = tk.Label(self.root, text="Status: -", fg="blue")
        self.status_label.pack()

        #frame kanan
        self.frame_tombol_gambar = tk.Frame(self.frame_kiri)
        self.frame_tombol_gambar.pack(pady=5, padx=5)

        # Tombol Hapus Gambar
        self.btn_hapus_gambar = tk.Button(self.frame_tombol_gambar, text="Hapus Gambar", command=self.hapus_gambar)
        self.btn_hapus_gambar.pack(side="right",pady=5, padx=5)

        # Tombol Pilih Gambar
        self.btn_file_gambar = tk.Button(self.frame_tombol_gambar, text="Unggah Gambar", command=self.pilih_gambar)
        self.btn_file_gambar.pack(side="left",pady=5, padx=5)

        # Frame untuk pratinjau gambar
        self.frame_gambar = tk.Frame(self.frame_kanan, width=200, height=200, bg="gray")
        self.frame_gambar.pack(pady=10)

        # Label untuk menampilkan gambar
        self.label_gambar = tk.Label(self.frame_gambar)
        self.label_gambar.pack(expand=True, fill="both")

        # Tombol Pilih Excel
        self.btn_file_excel = tk.Button(self.frame_kiri, text="Unggah File Excel", command=self.pilih_excel)
        self.btn_file_excel.pack(pady=5)
        self.file_label_excel = tk.Label(self.frame_kiri, text="File Excel: Belum ada", height=2, width=30, anchor="center", wraplength=200)
        self.file_label_excel.pack(pady=3)

        # ======================================================================
        # [MODIFIKASI] AREA PENGATURAN WAKTU (KIRI & KANAN)
        # ======================================================================
        # Kita buat Frame container agar pengaturan waktu rapi bersebelahan

        self.frame_waktu_container = tk.Frame(self.frame_kiri, borderwidth=1, relief="groove")
        self.frame_waktu_container.pack(pady=10, padx=5, ipadx=5, ipady=5)

        tk.Label(self.frame_waktu_container, text="--- PENGATURAN WAKTU ---", font=("Arial", 8, "bold")).pack(side="top", pady=2)

        # --- SUB-FRAME UNTUK BATCH (KIRI) ---
        self.frame_batch_setting = tk.Frame(self.frame_waktu_container)
        self.frame_batch_setting.pack(side="left", padx=10)

        # Dropdown Jumlah Batch
        tk.Label(self.frame_batch_setting, text="Istirahat Tiap (Pesan):").pack(anchor="w")
        batch_opts = ["0", "5", "10", "20", "50", "100"] # 0 artinya matikan fitur
        self.jumlah_batch = ttk.Combobox(self.frame_batch_setting, values=batch_opts, state="readonly", width=12)
        self.jumlah_batch.pack(pady=2)
        self.jumlah_batch.current(0) # Default 0 (Mati)
        
        # Dropdown Durasi Batch
        tk.Label(self.frame_batch_setting, text="Durasi Istirahat (Detik):").pack(anchor="w")
        durasi_opts = ["5", "10", "15", "20"]
        self.waktu_batch = ttk.Combobox(self.frame_batch_setting, values=durasi_opts, state="readonly", width=12)
        self.waktu_batch.pack(pady=2)
        self.waktu_batch.current(2)

        # --- SUB-FRAME UNTUK STANDAR (KANAN) ---
        self.frame_std_setting = tk.Frame(self.frame_waktu_container)
        self.frame_std_setting.pack(side="left", padx=10)

        # Dropdown Waktu Tunggu (Jeda antar chat)
        angka_rentang = [str(i) for i in range(5, 21)]
        tk.Label(self.frame_std_setting, text="Jeda Antar Chat (Detik):").pack(anchor="w")
        self.waktu_tunggu = ttk.Combobox(self.frame_std_setting, values=angka_rentang, state="readonly", width=12)
        self.waktu_tunggu.pack(pady=2)
        self.waktu_tunggu.current(5)

        # Dropdown Interval Ketik
        angka_rentang_interval = [str(i) for i in range(1, 4)]
        tk.Label(self.frame_std_setting, text="Interval Program (Detik):").pack(anchor="w")
        self.waktu_tunggu_interval = ttk.Combobox(self.frame_std_setting, values=angka_rentang_interval, state="readonly", width=12)
        self.waktu_tunggu_interval.pack(pady=2)
        self.waktu_tunggu_interval.current(2)

        # ======================================================================

        # Frame Tombol Eksekusi
        self.frame_button = tk.Frame(self.frame_kiri)
        self.frame_button.pack(pady=10)
        self.btn_submit = tk.Button(self.frame_button, text="MULAI KIRIM 🚀", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.submit)
        self.btn_submit.pack(side="left", padx=5)
        self.btn_stop = tk.Button(self.frame_button, text="KELUAR", bg="#f44336", fg="white", font=("Arial", 10, "bold"), command=self.on_closing)
        self.btn_stop.pack(side="left", padx=5)

        # Output Text
        self.output_label = tk.Label(self.root, text="Log Aktivitas:", font=("Arial", 10, "bold"))
        self.output_label.pack(pady=1)
        self.text_output = tk.Text(self.root, height=15, width=70)
        self.text_output.pack(pady=5, padx=10)
        self.hasil_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.hasil_label.pack(pady=1)

        # Redirect print
        sys.stdout = RedirectText(self.text_output)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Keluar", "Yakin ingin menutup aplikasi?"):
            print("Mematikan paksa semua proses...")
            self.root.destroy()
            os._exit(0)
            
    def hapus_gambar(self):
        self.path_gambar = ""
        self.label_gambar.config(image="")
        self.label_gambar.image = None


    def pilih_gambar(self):
        file_path = filedialog.askopenfilename(filetypes=[("Gambar", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.path_gambar = file_path
            img = Image.open(file_path)

            # Dapatkan ukuran asli gambar
            original_width, original_height = img.size

            # Tentukan rasio agar gambar tetap proporsional
            max_size = 200  # Maksimum 200x200
            scale = min(max_size / original_width, max_size / original_height)

            # Hitung ukuran baru
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            # Resize gambar dengan ukuran baru
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Konversi ke format Tkinter
            img_tk = ImageTk.PhotoImage(img)

            # Set gambar ke label
            self.label_gambar.config(image=img_tk)
            self.label_gambar.image = img_tk  # Simpan referensi agar tidak terhapus

    def pilih_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls;*.xlsx")])  # Hanya Excel
        if file_path:
            self.path_excel = file_path
            self.file_label_excel.config(text=f"{os.path.basename(file_path)}")  # Tampilkan path Excel

    def cek_status_thread(self):
        profile_name = self.combo_box.get()
        profile_folder = self.profiles.get(profile_name)
        print(f"[DEBUG] Memeriksa status login untuk profil: {profile_name}")
        print(f"[DEBUG] Menunggu selama 15 detik...")
        if profile_folder:
            status = cek_status_login(profile_folder)
            self.status_label.config(text=f"Status: {status}", fg="green" if "Sudah" in status else "red")
        else:
            self.status_label.config(text="Profil tidak ditemukan", fg="orange")

    def cek_status(self, event=None):
        threading.Thread(target=self.cek_status_thread).start()

    def submit(self):
        pesan = self.entry_nama.get("1.0", "end-1c")  # Ambil teks dari input
        profile_display_name = self.combo_box.get()
        opsi = self.profiles_dict[profile_display_name]

        # Buat thread baru untuk menjalankan blast_whatsapp
        thread = threading.Thread(target=self.run_blast, args=(pesan, opsi))
        thread.start()

    def run_blast(self, pesan, opsi):
        try:
            # Ambil nilai dari GUI
            waktu_tunggu = self.waktu_tunggu.get()
            waktu_tunggu_interval = self.waktu_tunggu_interval.get()
            
            # AMBIL NILAI BATCH BARU
            jumlah_batch = self.jumlah_batch.get()
            waktu_batch = self.waktu_batch.get()

            # Panggil logic dengan parameter tambahan
            logic.blast_whatsapp(
                self.path_excel, 
                opsi, 
                self.path_gambar, 
                pesan, 
                waktu_tunggu, 
                waktu_tunggu_interval,
                jumlah_batch,
                waktu_batch
            )

            if self.root.winfo_exists():
                self.root.after(0, lambda: self.hasil_label.config(text="Selesai!"))

        except Exception as e:
            print(f"[ERROR] {e}")

    def run(self):
        self.root.mainloop()  # Menjalankan loop utama Tkinter