from setuptools import setup, find_namespace_packages
import sys

with open("requirements.txt") as f:
    reqs = f.readlines()
    reqs = [r.strip() for r in reqs]
    reqs = [r for r in reqs if r and not r.startswith("#")]


packages = find_namespace_packages(include=["search*"])
print(f"packages:: {packages}", file=sys.stderr)

setup(
    name='nichirin',
    version='0.1',
    packages=packages,
    author="Shivani Gowda",
    author_email="shivanigowdaks@gmail.com",
    python_requires=">=3.7",
    license="Apache",
    install_requires=reqs,
    entry_points={"console_scripts": [
          "run-solr=search.retriever.solr:main",
          "index-solr=search.retriever.solr_index_docs:main",
          ]}
)
