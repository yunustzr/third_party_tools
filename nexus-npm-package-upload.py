import requests
import os


proxy = {
    'http': 'http://test:test123@10.10.10.10:3128',
    'https': 'http://test:test123@10.10.10.10:3128'
}

nexus_url ="http://example.com"
source_directory = "/home/mobaxterm/npm-install/downloaded_packages/"
api_endpoint = f"{nexus_url}/service/rest/v1/components"

data = {
    "repository": "react-package-repository",
}

nexus_username = "admin" 
nexus_password = "Pp123456"
print(f"nexus_username:{nexus_username}")


try:
    tgz_files = []
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".tgz"):
                tgz_files.append(os.path.join(root, file))

    for tgz_file in tgz_files:
        package_file_path = os.path.join(source_directory, tgz_file)
        print(f"tgz_file : {tgz_file}")
        

        with open(package_file_path, "rb") as package_file:
            files = {
                "npm.asset": (package_file_path, package_file),
            }
            response = requests.post(
                api_endpoint,
                params=data,
                auth=(nexus_username, nexus_password),
                files=files,
                proxies=proxy,
            )

            if response.status_code == 204:
                print(f"{tgz_file} başarıyla yüklendi.")
            else:
                print(f"{tgz_file} yüklenirken bir hata oluştu. Hata kodu: {response.status_code}")
                print(response.text)

except Exception as e:
    print(f"Hata: {e}")
