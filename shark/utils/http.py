from urllib.parse import urlparse


def get_netloc(url: str):
    parsed = urlparse(url)
    return parsed.netloc
