import urllib.parse
def get_payload(url):
    parser=urllib.parse.urlparse(url)
    payload=parser.params+parser.query+parser.fragment
    return payload
def get_path(url):
    parser=urllib.parse.urlparse(url)
    return parser.path
