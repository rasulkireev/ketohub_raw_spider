import urllib2


class Error(Exception):
    pass


class UnexpectedImageType(Error):
    pass


def download_data(url):
    image_handle = urllib2.urlopen(url)
    if image_handle.info().type != 'image/jpeg':
        print 'type: %s' % image_handle.info().type
        raise UnexpectedImageType('Expected image/jpeg, got ' +
                                  image_handle.info().type)
    return image_handle.read()
