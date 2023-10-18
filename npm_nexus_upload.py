import requests
import os

nexus_url = "https://nexus.example.com/repository/npm-repo/"

# .tgz dosyalarının bulunduğu dizin
source_directory = "downloaded_packages/"

# Dizindeki tüm .tgz dosyalarını bul
tgz_files = [f for f in os.listdir(source_directory) if f.endswith(".tgz")]

for tgz_file in tgz_files:
    package_file_path = os.path.join(source_directory, tgz_file)

    # Nexus API ile yükleme işlemi
    response = requests.post(
        f"{nexus_url}/",
        headers={"Content-Type": "application/octet-stream"},
        data=open(package_file_path, "rb").read(),
    )

    if response.status_code == 201:
        print(f"{tgz_file} başarıyla yüklendi.")
    else:
        print(f"{tgz_file} yüklenirken bir hata oluştu. Hata kodu: {response.status_code}")
