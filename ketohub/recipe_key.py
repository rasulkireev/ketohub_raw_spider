import re


def from_url(url):
    """Converts a URL to a recipe key."""
    # Strip out http:// or https:// prefix.
    url = re.sub(r'^https?://', '', url)
    # Strip out www subdomain.
    url = re.sub(r'^www\.', '', url)
    # Strip trailing slash
    url = re.sub(r'/$', '', url)
    # Convert all characters to lowercase
    url = url.lower()
    # Replace all non a-z0-9/ characters with -
    url = re.sub(r'[^a-z0-9/]', '-', url)
    # Replace all / characters with _
    return re.sub(r'/', '_', url)
