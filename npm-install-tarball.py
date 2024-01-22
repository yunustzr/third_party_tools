import requests
import os
import re
import json

proxy = {
    'http': 'http://test:test123@10.10.10.10:3128',
    'https': 'http://test:test123@10.10.10.10:3128'
}



def nexus_package_search(package_name,package_version):

    isdownload = True
    nexus_url = "http://example.com"
    repository_name = "react-package-repository"
    endpoint = f"{nexus_url}/service/rest/v1/search/assets"
    params = {
    "repository": repository_name,
    "format": "npm",
    "name": package_name,
    "version": package_version
    }

    # Nexus Search API'ye GET isteğini gönderin
    try:
        response = requests.get(endpoint, params=params,proxies=proxy)

        # Yanıtı kontrol edin
        if response.status_code == 200:
            search_result = response.json()
            if "items" in search_result and len(search_result["items"]) > 0:
                print(f"Paket bulundu: {package_name} {package_version}")
                isdownload = False
            else:
                print(f"Paket bulunamadı: {package_name} {package_version}")
        else:
            print(f"Nexus ile iletişimde sorun oluştu. {response}")
    except requests.exceptions.RequestException as e:
        print(f"Nexus ile iletişimde sorun oluştu: {e}")
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
    
    return isdownload


def is_package_downloaded(package_name, version, base_directory):
    package_directory = os.path.join(base_directory, package_name, version)
    tarball_file_name = f"{package_name}-{version}.tgz"
    tarball_file_path = os.path.join(package_directory, tarball_file_name)
    return os.path.exists(tarball_file_path)

def download_package(package_name, version, base_directory):
    if is_package_downloaded(package_name, version, base_directory):
        print(f"{package_name} {version} zaten indirildi. İşlem atlandı.")
        return

    package_directory = os.path.join(base_directory, package_name, version)
    package_url = f"https://registry.npmjs.org/{package_name}/{version}"
    
    
    response = requests.get(package_url, proxies=proxy)

    try:
        print(f"\npackage_url : {package_url}\n")
        
        package_data = response.json()
        #print(f"\nJson Data : {package_data}")
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
    tarball_file_path = package_directory+"/"+tarball_file_name
    directories = os.path.dirname(tarball_file_path)
    os.makedirs(directories, exist_ok=True)
    

    with open(tarball_file_path, "wb") as f:
        print(f" open f : {f} tarball_response.content : {tarball_response.content}")
        f.write(tarball_response.content)

    print(f"{package_name} {version} indirildi ve kaydedildi.")

    return package_data.get("dependencies", {})

def download_dependencies(base_directory, dependencies):
    if dependencies is None:
        print("Bağımlılıklar bulunamadı.")
        return

    dependency_list = [{"dependency_name": name, "dependency_version": version} for name, version in dependencies.items()]
    while dependency_list:
        dep = dependency_list.pop(0)
        package_name = dep["dependency_name"]
        version = dep["dependency_version"]
        
        limit = 10
        print(f"Checking package: {package_name}, version: {version}")
        dependencies_data = npm_packages_limit_versions(limit,[package_name])
        
        for package_info in dependencies_data:
            package_name = package_info["name"]
            package_versions = package_info["versions"]
            for version in package_versions:
                print(f"Checking package: {package_name}, version: {version}")
                if nexus_package_search(package_name,version):
                    new_dependencies = download_package(package_name, version, base_directory)

                    if new_dependencies:
                        for dep_name, dep_version in new_dependencies.items():
                            data = {"dependency_name": dep_name, "dependency_version": dep_version}
                            if data not in dependency_list:
                                dependency_list.append(data)


def npm_packages_limit_versions(limit, package_name):
    all_packages_data = []
    for name in package_name:
        data = {}
        url = f"https://registry.npmjs.org/{name}"
        response = requests.get(url, proxies=proxy)

        try:
            package_data = response.json()
            versions = list(package_data["versions"].keys())[-limit:]
            filtered_versions = [
                version
                for version in versions
                if not any(
                    keyword in version
                    for keyword in ["-","alpha", "nightly", "canary", "dev", "experimental","next","insiders"]
                )
            ]
            data = {"name": name, "versions": filtered_versions}
            print(f" downloand data : {data} ")
            all_packages_data.append(data)
        except ValueError as e:
            print(f"Hata: {e}")
            print(f"{name} için paket bilgileri alınamadı. İşlem atlandı.")
            continue

    return all_packages_data

limit = 25
base_download_directory = "downloaded_packages"
package_name = ["reactstrap"]
packages_data = npm_packages_limit_versions(limit, package_name)

for package_info in packages_data:
    package_name = package_info["name"]
    package_versions = package_info["versions"]
    for version in package_versions:
        print(f"Checking package: {package_name}, version: {version}")
        dependencies = download_package(package_name, version, base_download_directory)
        print(dependencies)
        download_dependencies(base_download_directory, dependencies)
