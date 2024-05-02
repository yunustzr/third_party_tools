import os
import subprocess
import requests
import xml.etree.ElementTree as ET


#NOT: Bu kodun çalışması için yukarıdaki kullanılan bağımlılıklar haricinde nuget.exe (https://dist.nuget.org/win-x86-commandline/latest/nuget.exe) paketi indirilmiş olmalı ve kodun çalıştığı dizin ile aynı seviyede olmalıdır.


proxy = {
    'http': 'http://testuser:testpassword@10.10.10.10:3128',
    'https': 'http://testuser:testpassword@10.10.10.10:3128'
}


def nuget_process_is_download(package_name, version,download_path):
    # Mevcut dizindeki nuget calistir
    command_text = f".\\nuget.exe install {package_name} -Version {version} -OutputDirectory \\{download_path}"
    print(f"Indirme Komutu : {command_text}")
   
    try:
        fullPath=f"\\{download_path}\\{package_name}.{version}"
        print(f"{fullPath}")
        print(os.path.exists(fullPath))
        if not os.path.exists(fullPath):
            subprocess.run(command_text, shell=True, check=True)
            print(f"{package_name}.{version} NuGet paketi indirildi.\n")
        else:
            print(f"{package_name}.{version} NuGet paketi daha önceden indirilmiş.\n")
    except subprocess.CalledProcessError:
        print("Basarisiz: NuGet paketi yuklenemedi.")


def download_package(package_name, version,download_path):
    try:
        # API URL'si
        api_url = f"https://api.nuget.org/v3-flatcontainer/{package_name}/{version}/{package_name}.{version}.nupkg"
        print(f"Main Api Url : {api_url} \n")
        file_name = f"{package_name}.{version}.nupkg"
        tarball_file_path = download_path+"/"+file_name
        directories = os.path.dirname(tarball_file_path)
        os.makedirs(directories, exist_ok=True)
        # Istek yap
        response = requests.get(api_url,proxies=proxy)

        # Istek basarili mi kontrol et
        if response.status_code == 200:
            with open(tarball_file_path, 'wb') as f:
                f.write(response.content)
            print(f"{file_name} basariyla indirildi.")

        else:
            print(f"{file_name} indirilemedi.")
    except Exception as e:
        print(f"Alinan Hata : {e}")



def download_latest_versions(package_name, count,download_path):
    try:
        api_url = f"https://api.nuget.org/v3-flatcontainer/{package_name.lower()}/index.json"
        response = requests.get(api_url,proxies=proxy)

        # Istek basarili mi kontrol et
        if response.status_code == 200:
            data = response.json()        
            versions = data.get("versions", [])
            last_versions = versions[-count:]
            for version in last_versions:
                nuget_process_is_download(package_name, version,download_path)
        else:
            print(f"{package_name} paketi icin surum bilgileri alinamadi.")
    except Exception as e:
        print(f"Alinan Hata : {e}")






base_path = "\\10.10.10.10\\shared_public"
directory_name = 'nuget_packages'
download_path = os.path.join(base_path, directory_name)

version_count = 30

with open('packages.xml', 'r') as file:
    metin = file.read()

output_data=metin.split("\n")
print(f"Package List  Length : {len(output_data)} ")

for data in output_data:
    parsing_data = data.split()
    if len(parsing_data) > 0:
        package_name = parsing_data[0]
        print(f"Package Name : {package_name}")
        download_latest_versions(package_name, version_count,download_path)
