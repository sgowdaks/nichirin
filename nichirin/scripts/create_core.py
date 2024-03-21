import os
import subprocess
import requests
import argparse

from pathlib import Path


def check_solr_status(SOLR_VERSION):
    solr_url = "http://localhost:8983/solr"
    try:
        response = requests.get(f"{solr_url}/admin/ping")
        check = response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        check = False

    if not check:
        subprocess.run([f"solr-{SOLR_VERSION}/bin/solr", "start"])


def change_schema(core_name, solr_dir):
    # Define the Solr base URL
    solr_base_url = f"http://localhost:8983/solr/{core_name}"

    enconf_path = solr_dir + f"/server/solr/{core_name}/conf/enumsConfig.xml"

    xml_content = """<?xml version="1.0" ?>
            <enumsConfig>
                <enum name="status">
                    <value>UNFETCHED</value>
                    <value>FETCHING</value>
                    <value>FETCHED</value>
                    <value>IGNORED</value>
                    <value>ERROR</value>
                </enum>
            </enumsConfig>"""

    with open(enconf_path, "w") as file:
        file.write(xml_content)

    # Define the field type definition
    field_type_definitions = [
        {
            "add-field-type": {
                "name": "knn_vector",
                "class": "solr.DenseVectorField",
                "vectorDimension": 1024,
                "similarityFunction": "cosine",
            }
        },
        {
            "add-field-type": {
                "name": "status",
                "class": "solr.EnumField",
                "enumsConfig": "enumsConfig.xml",
                "enumName": "status",
            }
        },
        {
            "add-field-type": {
                "name": "date",
                "class": "solr.TrieDateField",
                "docValues": True,
                "precisionStep": "0",
            }
        },
        {
            "add-field-type": {
                "name": "int",
                "class": "solr.TrieIntField",
                "docValues": True,
                "precisionStep": "0",
            }
        },
    ]

    # Define the field definition
    field_definitions = [
        {
            "add-field": {
                "name": "vector",
                "type": "knn_vector",
                "indexed": True,
                "stored": True,
            }
        },
        {
            "add-field": {
                "name": "text",
                "type": "text_en",
                "indexed": True,
                "stored": True,
            }
        },
        {
            "add-field": {
                "name": "status",
                "type": "status",
                "indexed": True,
                "stored": True,
                "default": "UNFETCHED",
                "multiValued": False,
            }
        },
        {
            "add-field": {
                "name": "outlinks",
                "type": "string",
                "indexed": False,
                "stored": True,
                "multiValued": True,
            }
        },
        {
            "add-field": {
                "name": "fetch_depth",
                "type": "int",
                "indexed": True,
                "stored": True,
                "default": "0",
            }
        },
        {
            "add-field": {
                "name": "last_crawled",
                "type": "boolean",
                "indexed": True,
                "stored": True,
            }
        },
        {
            "add-field": {
                "name": "last_updated_at",
                "type": "date",
                "indexed": True,
                "stored": True,
                "default": "NOW",
            }
        },
        {
            "add-field": {
                "name": "url",
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
                "default": "NOW",
            }
        },
    ]

    # Update the schema with the field type
    for field_type_definition in field_type_definitions:
        response_field_type = requests.post(
            f"{solr_base_url}/schema", json=field_type_definition
        )
        if response_field_type.status_code == 200:
            print("Field type was added successfully.")
        else:
            print(
                f"Error adding field type: {response_field_type.status_code} - {response_field_type.text}"
            )

    # Add the field to the schema
    for field_definition in field_definitions:
        response_field = requests.post(f"{solr_base_url}/schema", json=field_definition)
        if response_field.status_code == 200:
            print("Field was added successfully.")
        else:
            print(
                f"Error adding field: {response_field.status_code} - {response_field.text}"
            )


def create_core(SOLR_VERSION, core_name):
    solr_dir = f"solr-{SOLR_VERSION}"
    subprocess.run([f"{solr_dir}/bin/solr", "create", "-c", core_name], check=True)

    change_schema(core_name, solr_dir)


def main():
    args = parse_args()
    SOLR_VERSION = os.getenv("SOLR_VERSION", "9.1.1")
    check_solr_status(SOLR_VERSION)
    create_core(SOLR_VERSION, (args["core"]))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", help="Give the solr core name", required=True)
    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    main()
