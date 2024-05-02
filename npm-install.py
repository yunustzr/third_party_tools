import requests
from colorama import init, Fore, Back, Style
import os
import re
import json
import time

#Projede renk kullanımı için kullanılan kod.
init()

proxy = {
    'http': 'http://testuser:testpassword.*@10.10.10.10:3128',
    'https': 'http://testuser:testpassword.*@10.10.10.10:3128'
}

def find_files_with_package_name(directory, package_name):
    files = os.listdir(directory)
    matching_files = []
    for file in files:
        if package_name in file:
            matching_files.append(file)
    if matching_files:
        for file in matching_files:
            print(os.path.join(directory, file))
            return True
    else:
        print("Eşleşen dosya bulunamadı.")
        return False


def is_package_downloaded(package_name, version, base_directory):
    package_directory = os.path.join(base_directory, package_name, version)
    tarball_file_name = f"{package_name}-{version}.tgz"
    tarball_file_path = os.path.join(package_directory, tarball_file_name)
    return os.path.exists(tarball_file_path)

def download_package(package_name, version, base_directory):
    if is_package_downloaded(package_name, version, base_directory):
        print(f"{package_name} {version} zaten indirildi. İşlem atlandı.")
        return

    fullPath=f"\\{base_directory}\\{package_name}.{version}"
    package_url = f"https://registry.npmjs.org/{package_name}/{version}"
    

    try:
        response = requests.get(package_url, proxies=proxy)        
        package_data = response.json()
        tarball_url = package_data.get("dist", {}).get("tarball")
    except ValueError as e:
        print(f"Hata: {e}")
        print(f"{package_name} {version} için paket bilgileri alınamadı. İşlem atlandı.")
        return

    if not tarball_url:
        print(f"{package_name} {version} için 'dist' anahtarı veya 'tarball' URL'si bulunamadı. İşlem atlandı.")
        return


    tarball_response = requests.get(tarball_url, proxies=proxy)
    tarball_file_name = f"{package_name}-{version}.tgz"
    tarball_file_path = fullPath+"/"+tarball_file_name
    directories = os.path.dirname(tarball_file_path)
    os.makedirs(directories, exist_ok=True)
    

    with open(tarball_file_path, "wb") as f:
        f.write(tarball_response.content)

    print(f"{Fore.GREEN}{package_name} {version} indirildi ve kaydedildi.{Style.RESET_ALL}")

    return package_data.get("dependencies", {})




def download_dependencies_new(base_directory,data,limit):
    if data is None:
        print(f"{Fore.RED}Bağımlılıklar bulunamadı.{Style.RESET_ALL}")
        return
    
    while data:
        package_name=data.pop(0)
        dependencies_data = npm_package_version_list(limit,package_name)
        if dependencies_data:
            package_name = dependencies_data["name"]
            package_versions = dependencies_data["versions"]
            print(f"package_name:{package_name} - {package_versions}")
            for version in package_versions:
                print(f"Checking package: {package_name}, version: {version}")
                dependencies=download_package(package_name, version, base_directory)
                for name,version in dependencies.items():
                    if name not in data:
                        data.append(name)
                        print(f"{Fore.GREEN}İşlem yapılan paket {package_name} bu paketin {version} ait dependencies packages : {name} eklendi.{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Tüm dependencies Son Liste:\n {data}{Style.RESET_ALL}")
                        time.sleep(2)



def npm_package_version_list(limit,package):
    data = {}
    url = f"https://registry.npmjs.org/{package}"
    try:
        response = requests.get(url, proxies=proxy)
        package_data = response.json()
        try:
            version_list=list(package_data["versions"].keys())
        except KeyError:
            print(f"{Fore.RED}Paketin version bilgisi bulunamadi url : {url} {Style.RESET_ALL}")
            version_list=[]
        versions = version_list[-limit:] if len(version_list)>limit else version_list
        filtered_versions = [
            version
            for version in versions
            if not any(
                keyword in version
                for keyword in ["-","alpha", "nightly", "canary", "dev", "experimental","next","insiders"]
            )
        ]
        data = {"name": package, "versions": filtered_versions}
        print(f"{Fore.GREEN}Downloand data : {data} {Style.RESET_ALL}")
        return data
    except ValueError as e:
        print(f"npm version check error : {e}")


def get_elements_in_new_lines(file_path):
    elements = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                elements.append(line)
    return elements

file_path = 'npm_packages'  # Paketlerin isimleri okunacak metin dosyasinin adı
package_data = get_elements_in_new_lines(file_path)

limit = 40
base_path = "\\10.10.10.10\\shared_public"
base_download_directory = 'npm_react'
download_path = os.path.join(base_path, base_download_directory)

#Paketler burdan tanımlanabilir.
#package_data = ["@jridgewell/gen-mapping"]


def main_packages_downloand(limit,package_data):
    depend_data = []
    if package_data is None:
        print(f"{Fore.RED}İndirecek paket listesi boş..{Style.RESET_ALL}")
        return
    
    for package in package_data:
        try:
            dependencies_data = npm_package_version_list(limit,package)
            if dependencies_data:
                package_name = dependencies_data["name"]
                package_versions = dependencies_data["versions"]
                for version in package_versions:
                    dependencies = download_package(package_name, version, download_path)
                    print(f"dependencies:{dependencies}")
                    for name,version in dependencies.items():
                        if name not in depend_data:
                            depend_data.append(name)
        except ValueError as e:
            print(f"{Fore.RED}main_packages_downloand fonksiyonunda hata alindi: {e}{Style.RESET_ALL}")
            continue
    return depend_data
        


print("\n******************MAİN PACKAGES DOWNLOAND******************")
dependencies_data = main_packages_downloand(limit,package_data)
print("\n******************DEPENDENCİES DOWNLOAND******************")
print(f"Dependencies List : {list(set(dependencies_data))}")
#Yeni benzersiz dependencies list verisi
data = list(set(dependencies_data))
download_dependencies_new(download_path,data,limit)

