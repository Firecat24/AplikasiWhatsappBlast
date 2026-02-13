import time, os
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

def copy_image_to_clipboard(image_path):
    # Menggunakan PowerShell untuk copy gambar (Tanpa instal library tambahan)
    try:
        cmd = f"powershell -command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{image_path}'))\""
        subprocess.run(cmd, shell=True)
        return True
    except Exception as e:
        print(f"[ERROR CLIPBOARD] Gagal copy gambar: {e}")
        return False
    
def blast_whatsapp(file_path, profile_browser, gambar_path, pesan, waktu_tunggu, interval, jumlah_batch, waktu_batch):
    driver = None
    df = pd.read_excel(file_path, dtype={"Nomor": str})
    waktu_tunggu = int(waktu_tunggu)
    interval = int(interval)
    jumlah_batch = int(jumlah_batch)
    waktu_batch = int(waktu_batch)
    os.system("taskkill /im chrome.exe /f >nul 2>&1") 
    time.sleep(1) 
    # ---------------------------------------------------------------------

    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Hapus remote-debugging-port jika sering bentrok, tapi kalau butuh biarkan saja
        # options.add_argument("--remote-debugging-port=9222") 

        # ✅ Set path ke folder profil
        abs_profile_path = os.path.abspath(profile_browser)
        options.add_argument(f"--user-data-dir={abs_profile_path}")
        print(f"[INFO] Menggunakan profil Chrome: {profile_browser}")

        # 🚀 PERBAIKAN UTAMA: Jalankan driver dengan pembaruan otomatis yang valid
        # print("[INFO] Mendownload/Mengecek ChromeDriver sesuai versi Chrome...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://web.whatsapp.com")
        for index, row in df.iterrows():
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

            if "Status" not in df.columns:
                df["Status"] = ""

            df["Status"] = df["Status"].astype(str)
                
            if jumlah_batch > 0:
                nomor_sekarang = index + 1
                
                # Cek apakah saatnya istirahat?
                if nomor_sekarang % jumlah_batch == 0 and nomor_sekarang < len(df):
                    print(f"[PAUSE] Sudah memproses {nomor_sekarang} nomor.")
                    print(f"[PAUSE] Pendinginan mesin selama {waktu_batch} detik")
                    
                    # Hitung mundur
                    for i in range(waktu_batch, 0, -1):
                        print(f" {i}", end=" ", flush=True)
                        time.sleep(1)
                    print("\n")

            try:
                # print(f"[INFO] Mengirim pesan ke {nomor_nama} ({nomor_hp})...")
                search_box = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @role='textbox']")))
                search_box.click()
                time.sleep(interval)
                search_box.send_keys(nomor_hp)
                time.sleep(interval)
                search_box.send_keys(Keys.ENTER)
                time.sleep(interval)

                message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
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
                time.sleep(interval)

                if gambar_path == "" :
                    message_box.send_keys(Keys.ENTER)
                    time.sleep(interval)
                    action = ActionChains(driver)
                    action.send_keys(Keys.ESCAPE).perform()
                    df.at[index, "Status"] = "ada History Chatnya✅"
                    print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                    df.to_excel(file_path, index=False)
                    time.sleep(waktu_tunggu)
                else:
                    full_path = os.path.abspath(gambar_path)
                    
                    if os.path.exists(full_path):
                        copy_image_to_clipboard(full_path)
                        time.sleep(1) # Beri waktu komputer mikir
                        message_box.click()
                        time.sleep(0.5)
                        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                        try:
                            send_btn = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"] | //div[@aria-label="Send"] | //div[@aria-label="Kirim"]'))
                            )
                            time.sleep(1) 
                            driver.execute_script("arguments[0].click();", send_btn)
                            WebDriverWait(driver, 20).until(
                                EC.invisibility_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
                            )
                            df.at[index, "Status"] = "Terkirim Gambar ✅"

                        except Exception as e:
                            print(f"[WARNING] Tombol kirim tidak ketemu/macet. Mencoba tekan ENTER paksa...")
                            try:
                                # Tekan Enter sekali
                                ActionChains(driver).send_keys(Keys.ENTER).perform()
                                time.sleep(1)
                                # Tekan Enter lagi (jaga-jaga kalau fokus hilang)
                                ActionChains(driver).send_keys(Keys.ENTER).perform()
                                
                                # Cek apakah sudah terkirim (Preview hilang?)
                                time.sleep(2)
                                send_exists = driver.find_elements(By.XPATH, '//span[@data-icon="send"]')
                                if not send_exists:
                                    print(f"[SUKSES] Terkirim via ENTER Darurat.")
                                    df.at[index, "Status"] = "Terkirim (Enter) ✅"
                                else:
                                    # Kalau masih nongol juga, tekan ESC biar script lanjut
                                    print(f"[GAGAL] Gambar macet total. Skip nomor ini.")
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                    df.at[index, "Status"] = "Gagal Total ❌"
                            except:
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()

                        time.sleep(interval)
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                        df.to_excel(file_path, index=False)
                        time.sleep(waktu_tunggu)
            except NoSuchElementException as e:
                print(f"element tidak ditemukan {e}")

            except TimeoutException:
                # print(f"[INFO] Nomor dari {nomor_nama} Tidak Ditemukan di daftar kontak")
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.BACKSPACE)
                time.sleep(interval)
                try:
                    ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('n').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
                    time.sleep(interval)
                    search_box_new = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']")))
                    search_box_new.click()
                    time.sleep(interval)
                    search_box_new.send_keys(nomor_hp)
                    time.sleep(interval)
                    search_box_new.send_keys(Keys.ENTER)
                    time.sleep(interval)

                    message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
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
                    time.sleep(interval)

                    if gambar_path == "" :
                        message_box.send_keys(Keys.ENTER)
                        time.sleep(interval)
                        action = ActionChains(driver)
                        action.send_keys(Keys.ESCAPE).perform()
                        df.at[index, "Status"] = "Nomor Belum Pernah di Chat ➖"
                        df.to_excel(file_path, index=False)
                        print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                        time.sleep(waktu_tunggu)
                    else:
                        full_path = os.path.abspath(gambar_path)
                        
                        if os.path.exists(full_path):
                            copy_image_to_clipboard(full_path)
                            time.sleep(1) # Beri waktu komputer mikir
                            message_box.click()
                            time.sleep(0.5)
                            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                            try:
                                send_btn = WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"] | //div[@aria-label="Send"] | //div[@aria-label="Kirim"]'))
                                )
                                time.sleep(1) 
                                driver.execute_script("arguments[0].click();", send_btn)
                                WebDriverWait(driver, 20).until(
                                    EC.invisibility_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
                                )
                                df.at[index, "Status"] = "Terkirim Gambar ✅"

                            except Exception as e:
                                print(f"[WARNING] Tombol kirim tidak ketemu/macet. Mencoba tekan ENTER paksa...")
                                try:
                                    # Tekan Enter sekali
                                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                                    time.sleep(1)
                                    # Tekan Enter lagi (jaga-jaga kalau fokus hilang)
                                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                                    
                                    # Cek apakah sudah terkirim (Preview hilang?)
                                    time.sleep(2)
                                    send_exists = driver.find_elements(By.XPATH, '//span[@data-icon="send"]')
                                    if not send_exists:
                                        df.at[index, "Status"] = "Nomor Belum Pernah di Chat ➖"
                                    else:
                                        # Kalau masih nongol juga, tekan ESC biar script lanjut
                                        print(f"[GAGAL] Gambar macet total. Skip nomor ini.")
                                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                        df.at[index, "Status"] = "Gagal Total ❌"
                                except:
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            
                            time.sleep(interval)
                            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            print(f"[SUKSES] Berhasil mengirim ke {nomor_nama}")
                            df.to_excel(file_path, index=False)
                            time.sleep(waktu_tunggu)
                except NoSuchElementException as e:
                    print(f"suatu element tidak ditemukan {e}")

                except TimeoutException:
                    print(f'[INFO] Nomor {nomor_nama} Tidak Terdaftar di Whatsapp')
                    df.at[index, "Status"] = "Nomor Tidak Ditemukan ❌"
                    df.to_excel(file_path, index=False)
                    # Tekan ESC sekali untuk menutup popup "Nomor tidak ditemukan" (jika ada)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.5)
                    
                    # Tekan ESC lagi untuk menutup drawer "New Chat" dan kembali ke menu utama
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.5)
                    
                    # Tekan ESC sekali lagi untuk memastikan search bar bersih/tidak fokus
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(waktu_tunggu)

                except ElementNotInteractableException:
                    print("Elemen tidak bisa diklik karena jendela mungkin di-minimize. Coba restore dulu.")

                except Exception as e:
                    {f"ada error lainnya selain elemen tidak ditemukan didalam chat baru : {e}"}
            
            except ElementNotInteractableException:
                print("Elemen tidak bisa diklik karena jendela mungkin di-minimize. Coba restore dulu.")

            except Exception as e:
                print(f"error lainnya : {e}")

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