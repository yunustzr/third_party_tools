import requests
import subprocess
import os

# Nexus API endpoint
nexus_api_url = "http://example.com/service/rest/v1/components"

# Nexus repository name
repository_name = "maven-releases"

source_directory = "/home/mobaxterm/npm-install/maven_packages"

nexus_username = "admin"
nexus_password = "Pp123456"

proxy-user ="test"
proxy-password="test123"
proxy-url="http://10.10.10.10:3128"


print(f"nexus_username: {nexus_username}")

try:
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".jar"):
                print(f"file : {os.path.join(root, file)}")
                jar_file_name = os.path.basename(os.path.join(root, file))
                group_id = os.path.dirname(os.path.join(root, file)).split(os.path.sep)[-2]
                artifact_id = os.path.dirname(os.path.join(root, file)).split(os.path.sep)[-1]
                version = file.replace(artifact_id + "-", "").replace(".jar", "")
                jar_file_path = os.path.join(root, file)

                     
                curl_command = f"curl -x {proxy-url} --proxy-user {proxy-user}:{proxy-password} -u {nexus_username}:{nexus_password} -X POST {nexus_api_url}?repository={repository_name} -F maven2.generate-pom=true -F maven2.groupId={group_id} -F maven2.artifactId={artifact_id} -F maven2.asset1.extension=jar -F maven2.packaging=jar -F maven2.version={version} -F maven2.asset1=@{jar_file_path};type=application/java-archive"
                result = subprocess.run(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(result.stderr)
              
                

except Exception as e:
    print(f"Hata: {e}")


