import urllib2


def download_data(url):
    image_handle = urllib2.urlopen(url)
    return image_handle.read()
