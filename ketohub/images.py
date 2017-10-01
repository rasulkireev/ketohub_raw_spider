import urllib


def download_data(url):
    image_handle = urllib.urlopen(url)
    return image_handle.read()
