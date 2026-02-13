from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os, time

def cek_status_login(profile_path, timeout=10):
    def buat_driver(headless=True):
        opts = Options()
        opts.add_argument(f"--user-data-dir={os.path.abspath(profile_path)}")
        if headless:
            opts.add_argument("--headless")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=800,600")
        else:
            opts.add_argument("--start-maximized")
        opts.add_argument("--no-sandbox")
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    try:
        driver = buat_driver(headless=True)
        driver.get("https://web.whatsapp.com")
        wait = WebDriverWait(driver, timeout)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true' and @role='textbox']")))
            print("[DEBUG] Search bar ditemukan → Sudah login")
            return "✅ Sudah Login"

        except TimeoutException:
            print("[DEBUG] Search bar tidak ditemukan → Belum login")

            # Tutup browser headless
            driver.quit()

            # Buka ulang browser dalam mode tampilan penuh
            driver = buat_driver(headless=False)
            driver.get("https://web.whatsapp.com")
            print("[INFO] Silakan login WhatsApp di browser yang muncul...")
            
            # Tunggu user login (sampai search bar muncul)
            WebDriverWait(driver, 600).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @role='textbox']"))
            )
            print("[INFO] Login berhasil, browser akan ditutup.")
            return "✅ Sudah Login"

    except Exception as e:
        print(f"[ERROR] Gagal buka Chrome: {e}")
        return "⚠️ Tidak Diketahui (Gagal load WA)"
    
    finally:
        try:
            driver.quit()
        except:
            pass