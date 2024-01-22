import xml.etree.ElementTree as ET
import requests
import os

repository_url = "https://repo1.maven.org/maven2"
proxy = {
    'http': 'http://test:test123@10.10.10.10:3128',
    'https': 'http://test:test123@10.10.10.10:3128'
}

def maven_pomXML_parsing():
    all_artifact = []
    # Define the path to your pom.xml file
    pom_xml_path = "/home/mobaxterm/npm-install/pom.xml"
    # Parse the pom.xml file using ElementTree
    tree = ET.parse(pom_xml_path)
    root = tree.getroot()

    # Define the XML namespace for Maven POM files
    namespace = {"maven": "http://maven.apache.org/POM/4.0.0"}

    # Find and print the project's group ID, artifact ID, and version
    group_id = root.find(".//maven:groupId", namespaces=namespace).text
    artifact_id = root.find(".//maven:artifactId", namespaces=namespace).text

    print(f"Group ID: {group_id}")
    print(f"Artifact ID: {artifact_id}")

    # Find and print project dependencies
    dependencies = root.findall(".//maven:dependency", namespaces=namespace)
    for dependency in dependencies:
        dep_group_id = dependency.find("maven:groupId", namespaces=namespace).text
        dep_artifact_id = dependency.find("maven:artifactId", namespaces=namespace).text

        print(f"Dependency Group ID: {dep_group_id}")
        print(f"Dependency Artifact ID: {dep_artifact_id}")
        packages = {"group_id": dep_group_id, "artifact_id": dep_artifact_id}
        all_artifact.append(packages)
    return all_artifact

packages = maven_pomXML_parsing()
for package_info in packages:
    group_id = package_info["group_id"]
    artifact_id = package_info["artifact_id"]
    urlParsing = "/".join(group_id.split("."))
    print(f"group_id : {group_id} = artifact_id:{artifact_id}")
    package_directory = os.path.join(group_id, artifact_id)
    os.makedirs(package_directory, exist_ok=True)

    metadata_url = f"{repository_url}/{urlParsing}/{artifact_id}/maven-metadata.xml"
    print(f"metadata_url : {metadata_url}")
    response = requests.get(metadata_url, proxies=proxy)
    metadata_xml = response.text
    print(f"metadata_xml : {metadata_xml}")
    versions = []
    
    # Parse Maven-metadata.xml manually
    for line in metadata_xml.split("\n"):
        if line.strip().startswith("<version>"):
            version = line.strip().replace("<version>", "").replace("</version>", "")
            versions.append(version)

    # Get the latest 3 versions (you can adjust this as needed)
    latest_versions = versions[-5:]

    for version in latest_versions:
        jar_url = f"{repository_url}/{group_id}/{artifact_id}/{version}/{artifact_id}-{version}.jar"
        jar_response = requests.get(jar_url, proxies=proxy)
        jar_file_name = f"{artifact_id}-{version}.jar"
        jar_file_path = os.path.join(package_directory, jar_file_name)

        with open(jar_file_path, "wb") as f:
            f.write(jar_response.content)

        print(f"{group_id}:{artifact_id}:{version} indirildi ve kaydedildi.")
