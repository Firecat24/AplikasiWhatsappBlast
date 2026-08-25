import time, os, random
import pyperclip
import pandas as pd
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, TimeoutException, ElementNotInteractableException, WebDriverException

def get_random_interval():
    """Jeda kecil antar aksi (klik, ketik, dst) - selalu diacak 1-3 detik, tiap kali dipanggil."""
    return random.randint(1, 3)

def get_random_jeda(waktu_tunggu_dasar):
    """Jeda utama antar kontak - diacak dalam rentang -1 s/d +1 dari angka yang dipilih user."""
    minimum = max(1, waktu_tunggu_dasar - 1)
    maksimum = waktu_tunggu_dasar + 1
    return random.randint(minimum, maksimum)

XPATH_SEARCH_BOX = "//input[@data-tab='3']"
XPATH_MESSAGE_BOX = '//div[@contenteditable="true"][@data-tab="10"]'
XPATH_SEND_BUTTON = '//div[@role="button"][.//span[@data-icon="wds-ic-send-filled"]]'
XPATH_SEND_ICON_CHECK = '//span[@data-icon="wds-ic-send-filled"]'
TIMEOUT_TUNGGU_LOGIN = 120
TIMEOUT_MESSAGE_BOX = 10
TIMEOUT_NEW_CHAT_BOX = 10
TIMEOUT_SEND_BUTTON = 20

def trigger_new_chat_shortcut(driver):
    ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys(
        "n"
    ).key_up(Keys.ALT).key_up(Keys.CONTROL).perform()


# ============================================================
# FUNGSI UTAMA
# ============================================================

def copy_image_to_clipboard(image_path):
    # Menggunakan PowerShell untuk copy gambar (Tanpa instal library tambahan)
    try:
        cmd = f"powershell -command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{image_path}'))\""
        subprocess.run(cmd, shell=True)
        return True
    except Exception as e:
        print(f"[ERROR CLIPBOARD] Gagal copy gambar: {e}")
        return False

def blast_whatsapp(file_path, profile_browser, gambar_path, pesan, waktu_tunggu, jumlah_batch, waktu_batch, stop_event=None):
    driver = None
    df = pd.read_excel(file_path, dtype={"Nomor": str})
    waktu_tunggu = int(waktu_tunggu)
    jumlah_batch = int(jumlah_batch)
    waktu_batch = int(waktu_batch)

    # Pastikan kolom Status selalu ada, dipakai untuk skip baris yang sudah pernah diproses
    if "Status" not in df.columns:
        df["Status"] = ""
    df["Status"] = df["Status"].fillna("").astype(str)

    total_baris = len(df)
    sudah_terisi = (df["Status"].str.strip() != "").sum()
    if sudah_terisi >= total_baris:
        print(f"[INFO] Semua {total_baris} baris sudah punya status. Tidak ada yang perlu dikirim.")
        return

    print(f"[INFO] {sudah_terisi} dari {total_baris} baris sudah pernah diproses -> dilewati. Sisanya {total_baris - sudah_terisi} akan dikirim.")

    os.system("taskkill /im chrome.exe >nul 2>&1")
    time.sleep(2)
    os.system("taskkill /im chrome.exe /f >nul 2>&1")
    time.sleep(1)

    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        abs_profile_path = os.path.abspath(profile_browser)
        options.add_argument(f"--user-data-dir={abs_profile_path}")
        print(f"[INFO] Menggunakan profil Chrome: {profile_browser}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://web.whatsapp.com")
        for index, row in df.iterrows():
            if stop_event is not None and stop_event.is_set():
                print("[STOP] Proses dihentikan oleh user.")
                break
            status_awal = str(row["Status"]).strip()
            if status_awal != "":
                continue
            nomor_hp = row["Nomor"].strip().replace("'", "").replace(" ", "")
            nomor_nama = row["Nama"].strip()
            if nomor_hp.startswith("08"):
                nomor_hp = "+62" + nomor_hp[1:]
            elif nomor_hp.startswith("8"):
                nomor_hp = "+62" + nomor_hp
            elif nomor_hp.startswith("628"):
                nomor_hp = "+62" + nomor_hp[2:]
            elif not nomor_hp.startswith("+"):
                nomor_hp = "+" + nomor_hp
            try:
                search_box = WebDriverWait(driver, TIMEOUT_TUNGGU_LOGIN).until(EC.presence_of_element_located((By.XPATH, XPATH_SEARCH_BOX)))
                search_box.click()
                time.sleep(get_random_interval())
                search_box.send_keys(nomor_hp)
                print(f"[INFO] Mencari nomor: {nomor_hp} ({nomor_nama})")
                time.sleep(get_random_interval())
                search_box.send_keys(Keys.ENTER)
                time.sleep(get_random_interval())

                message_box = WebDriverWait(driver, TIMEOUT_MESSAGE_BOX).until(EC.presence_of_element_located((By.XPATH, XPATH_MESSAGE_BOX)))
                try:
                    existing_text = message_box.text
                    if existing_text.strip():
                        message_box.send_keys(Keys.CONTROL, "a")
                        message_box.send_keys(Keys.BACKSPACE)
                        time.sleep(0.5)
                except Exception as e:
                    print(f"[WARNING] Gagal cek/hapus teks sebelumnya: {e}")
                pyperclip.copy(pesan)
                message_box.send_keys(Keys.CONTROL, "v")
                time.sleep(get_random_interval())

                if gambar_path == "" :
                    message_box.send_keys(Keys.ENTER)
                    time.sleep(get_random_interval())
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    df.at[index, "Status"] = "ada History Chatnya✅"
                    print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                    df.to_excel(file_path, index=False)
                    time.sleep(get_random_jeda(waktu_tunggu))
                else:
                    full_path = os.path.abspath(gambar_path)
                    
                    if os.path.exists(full_path):
                        copy_image_to_clipboard(full_path)
                        time.sleep(1)
                        message_box.click()
                        time.sleep(0.5)
                        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                        try:
                            send_btn = WebDriverWait(driver, TIMEOUT_SEND_BUTTON).until(
                                EC.element_to_be_clickable((By.XPATH, XPATH_SEND_BUTTON))
                            )
                            time.sleep(1)
                            try:
                                send_btn.click()
                            except Exception:
                                driver.execute_script("arguments[0].click();", send_btn)
                            WebDriverWait(driver, TIMEOUT_SEND_BUTTON).until(
                                EC.invisibility_of_element_located((By.XPATH, XPATH_SEND_ICON_CHECK))
                            )
                            df.at[index, "Status"] = "Terkirim Gambar ✅"

                        except Exception as e:
                            print(f"[WARNING] Tombol kirim tidak ketemu/macet. Mencoba tekan ENTER paksa...")
                            try:
                                ActionChains(driver).send_keys(Keys.ENTER).perform()
                                time.sleep(1)
                                ActionChains(driver).send_keys(Keys.ENTER).perform()
                                time.sleep(2)
                                send_exists = driver.find_elements(By.XPATH, XPATH_SEND_ICON_CHECK)
                                if not send_exists:
                                    print(f"[SUKSES] Terkirim via ENTER Darurat.")
                                    df.at[index, "Status"] = "Terkirim (Enter) ✅"
                                else:
                                    print(f"[GAGAL] Gambar macet total. Skip nomor ini.")
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                    df.at[index, "Status"] = "Gagal Total ❌"
                            except:
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()

                        time.sleep(get_random_interval())
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                        df.to_excel(file_path, index=False)
                        time.sleep(get_random_jeda(waktu_tunggu))
                    else:
                        print(f"[GAGAL] File gambar tidak ditemukan: {full_path}. Melewati {nomor_nama}.")
                        df.at[index, "Status"] = "Gagal: File Gambar Tidak Ditemukan ❌"
                        df.to_excel(file_path, index=False)
                        time.sleep(get_random_interval())
            except NoSuchElementException as e:
                print(f"element tidak ditemukan {e}")

            except TimeoutException:
                search_box.send_keys(Keys.CONTROL, "a")
                search_box.send_keys(Keys.BACKSPACE)
                time.sleep(get_random_interval())
                try:
                    trigger_new_chat_shortcut(driver)
                    time.sleep(get_random_interval())
                    search_box_new = WebDriverWait(driver, TIMEOUT_NEW_CHAT_BOX).until(EC.presence_of_element_located((By.XPATH, XPATH_SEARCH_BOX)))
                    search_box_new.click()
                    time.sleep(get_random_interval())
                    search_box_new.send_keys(nomor_hp)
                    time.sleep(get_random_interval())
                    search_box_new.send_keys(Keys.ENTER)
                    time.sleep(get_random_interval())

                    message_box = WebDriverWait(driver, TIMEOUT_MESSAGE_BOX).until(EC.presence_of_element_located((By.XPATH, XPATH_MESSAGE_BOX)))
                    try:
                        existing_text = message_box.text
                        if existing_text.strip():
                            message_box.send_keys(Keys.CONTROL, "a")
                            message_box.send_keys(Keys.BACKSPACE)
                            time.sleep(0.5)
                    except Exception as e:
                        print(f"[WARNING] Gagal cek/hapus teks sebelumnya: {e}")
                    pyperclip.copy(pesan)
                    message_box.send_keys(Keys.CONTROL, "v")
                    time.sleep(get_random_interval())

                    if gambar_path == "" :
                        message_box.send_keys(Keys.ENTER)
                        time.sleep(get_random_interval())
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        df.at[index, "Status"] = "Nomor Belum Pernah di Chat ➖"
                        df.to_excel(file_path, index=False)
                        print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                        time.sleep(get_random_jeda(waktu_tunggu))
                    else:
                        full_path = os.path.abspath(gambar_path)
                        
                        if os.path.exists(full_path):
                            copy_image_to_clipboard(full_path)
                            time.sleep(1)
                            message_box.click()
                            time.sleep(0.5)
                            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                            try:
                                send_btn = WebDriverWait(driver, TIMEOUT_SEND_BUTTON).until(
                                    EC.presence_of_element_located((By.XPATH, XPATH_SEND_BUTTON))
                                )
                                time.sleep(1) 
                                driver.execute_script("arguments[0].click();", send_btn)
                                WebDriverWait(driver, TIMEOUT_SEND_BUTTON).until(
                                    EC.invisibility_of_element_located((By.XPATH, XPATH_SEND_ICON_CHECK))
                                )
                                df.at[index, "Status"] = "Terkirim Gambar ✅"

                            except Exception as e:
                                print(f"[WARNING] Tombol kirim tidak ketemu/macet. Mencoba tekan ENTER paksa...")
                                try:
                                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                                    time.sleep(1)
                                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                                    time.sleep(2)
                                    send_exists = driver.find_elements(By.XPATH, XPATH_SEND_ICON_CHECK)
                                    if not send_exists:
                                        df.at[index, "Status"] = "Nomor Belum Pernah di Chat ➖"
                                    else:
                                        print(f"[GAGAL] Gambar macet total. Skip nomor ini.")
                                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                        df.at[index, "Status"] = "Gagal Total ❌"
                                except:
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            
                            time.sleep(get_random_interval())
                            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                            df.to_excel(file_path, index=False)
                            time.sleep(get_random_jeda(waktu_tunggu))
                        else:
                            print(f"[GAGAL] File gambar tidak ditemukan: {full_path}. Melewati {nomor_nama}.")
                            df.at[index, "Status"] = "Gagal: File Gambar Tidak Ditemukan ❌"
                            df.to_excel(file_path, index=False)
                            time.sleep(get_random_interval())
                except NoSuchElementException as e:
                    print(f"suatu element tidak ditemukan {e}")

                except TimeoutException:
                    print(f'[INFO] Nomor {nomor_nama} Tidak Terdaftar di Whatsapp')
                    df.at[index, "Status"] = "Nomor Tidak Ditemukan ❌"
                    df.to_excel(file_path, index=False)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.5)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.5)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(get_random_jeda(waktu_tunggu))

                except ElementNotInteractableException:
                    print("Elemen tidak bisa diklik karena jendela mungkin di-minimize. Coba restore dulu.")

                except Exception as e:
                    {f"ada error lainnya selain elemen tidak ditemukan didalam chat baru : {e}"}
            
            except ElementNotInteractableException:
                print("Elemen tidak bisa diklik karena jendela mungkin di-minimize. Coba restore dulu.")

            except Exception as e:
                print(f"error lainnya : {e}")

            if jumlah_batch > 0:
                nomor_selesai = index + 1
                if nomor_selesai % jumlah_batch == 0 and nomor_selesai < len(df):
                    print(f"[PAUSE] Sudah selesai memproses {nomor_selesai} dari {len(df)} nomor.")
                    print(f"[PAUSE] Istirahat {waktu_batch} detik sebelum lanjut ke nomor berikutnya...")
                    for i in range(waktu_batch, 0, -1):
                        print(f" {i}", end=" ", flush=True)
                        time.sleep(1)
                    print("\n")

        print("[SUKSES] Telah mengirim seluruh pesan ke pelanggan")
        time.sleep(3)

    except WebDriverException as we:
        print("[ERROR] Gagal membuat driver Chrome:")
        print(we)

    except SessionNotCreatedException:
        print('tutup browser chrome terlebih dahulu atau webdriver tidak cocok dengan versi browser')

    except ElementNotInteractableException:
        print("Elemen tidak bisa diklik karena jendela mungkin di-minimize. Coba restore dulu.")
        
    except Exception as e:
        print("Error Lainnya")
        print(e)

    finally:
        if driver:
            driver.quit()