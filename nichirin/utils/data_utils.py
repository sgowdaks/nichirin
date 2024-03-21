import yaml

from urllib.parse import urlparse

def load_yaml(path):
    with open(path, "r") as stream:
        return yaml.safe_load(stream)
    
def is_valid_url(url):
    "Check if a URL is valid."   
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme) and bool(parsed_url.netloc)

def filter_urls(urls):
    "Filter out unwanted URLs."
    filtered_urls = []
    for url in urls:
        if is_valid_url(url) and not url.startswith(("java", "javascript")):
            filtered_urls.append(url)
    return filtered_urls
    
def validate_url(root, urls):
    filtered_urls = filter_urls(urls)
    return filtered_urls


    