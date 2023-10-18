import requests
import os

def is_package_downloaded(package_name, version, base_directory):
    package_directory = os.path.join(base_directory, package_name, version)
    tarball_file_name = f"{package_name}-{version}.tgz"
    tarball_file_path = os.path.join(package_directory, tarball_file_name)
    return os.path.exists(tarball_file_path)

def download_package_and_dependencies(package_name, version, base_directory):
    if is_package_downloaded(package_name, version, base_directory):
        print(f"{package_name} {version} zaten indirildi. İşlem atlandı.")
        return

    package_directory = os.path.join(base_directory, package_name, version)
    print(f"packagedirectory : {package_directory}")
    print(f"package_name : {package_name}")

    package_url = f"https://registry.npmjs.org/{package_name}/{version}"
    response = requests.get(package_url)
    
    try:
        package_data = response.json()
    except ValueError as e:
        print(f"Hata: {e}")
        print(f"{package_name} {version} için paket bilgileri alınamadı. İşlem atlandı.")
        return

    tarball_url = package_data.get("dist", {}).get("tarball")
    
    if not tarball_url:
        print(f"{package_name} {version} için 'dist' anahtarı veya 'tarball' URL'si bulunamadı. İşlem atlandı.")
        return

    tarball_response = requests.get(tarball_url)
    tarball_file_name = f"{package_name}-{version}.tgz"
    tarball_file_path = package_directory+"/"+tarball_file_name
    directories = os.path.dirname(tarball_file_path)
    os.makedirs(directories, exist_ok=True)
    print(f"directories : {directories}")
    
    
    with open(tarball_file_path, "wb") as f:
        f.write(tarball_response.content)

    print(f"{package_name} {version} indirildi ve kaydedildi.")

    dependencies = package_data.get("dependencies", {})
    for dependency_name, dependency_version in dependencies.items():
        download_package_and_dependencies(dependency_name, dependency_version, package_directory)

def npm_packages_limit_versions(limit, packages):
    all_packages_data = []
    for package_name in packages:
        data = {}
        url = f"https://registry.npmjs.org/{package_name}"
        response = requests.get(url)
        
        try:
            package_data = response.json()
        except ValueError as e:
            print(f"Hata: {e}")
            print(f"{package_name} için paket bilgileri alınamadı. İşlem atlandı.")
            continue

        versions = list(package_data["versions"].keys())[-limit:]
        
        filtered_versions = [version for version in versions if not ("beta" in version or "alpha" in version)]
        data = {"name": package_name, "versions": filtered_versions}
        all_packages_data.append(data)
    
    return all_packages_data

# @restart/ui paketi ve bağımlılıklarını indirme
package_name = ["@fortawesome/fontawesome-svg-core","react-animated-css","react-router-dom","react-dom"]
limit = 2  # İstediğiniz sayıda sürümü sınırlayabilirsiniz
packages_data = npm_packages_limit_versions(limit, package_name)
base_download_directory = "downloaded_packages"

for package_info in packages_data:
    package_name = package_info["name"]
    package_versions = package_info["versions"]
    for version in package_versions:
        print(f"package :{package_name} ,version {version}")
        download_package_and_dependencies(package_name, version, base_download_directory)

