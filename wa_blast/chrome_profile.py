import os

def get_chrome_profiles():
    """
    Mengambil daftar profil Chrome dari folder lokal 'profile_chrome'
    dan mengembalikan dict dengan nama tampilan → path folder.
    """

    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile_chrome")
    profiles = {}

    # Pastikan folder profile_chrome ada
    if not os.path.exists(base_path):
        print("[ERROR] Folder 'profile_chrome' tidak ditemukan.")
        return {}

    # Mapping manual nama folder ke nama tampilan
    folder_to_label = {
        "farhan": "WhatsApp (Farhan - Otomatis)",
        "Profile 2": "MUT",
        "Profile 3": "MUS",
        "Profile 4": "KWB",
        "Profile 5": "KWM",
        "Profile 6": "KWU"
    }

    # Baca isi folder profile_chrome
    for folder_name in os.listdir(base_path):
        full_path = os.path.join(base_path, folder_name)
        if os.path.isdir(full_path):
            label = folder_to_label.get(folder_name, folder_name)
            profiles[label] = os.path.join("profile_chrome", folder_name)  # relatif terhadap project

    return profiles