import hashlib,chardet
def get_md5(s):
    md5= hashlib.md5()
    md5.update(s.encode("utf-8"))
    return md5.hexdigest()
def is_chinese(s):
    #s=s.decode("utf-8")
    if s>=u"\u4e00" and s<=u"\u9fa6":
        return True
    else:return False
def decode(s):
    if isinstance(s,type(u"")):
        return s
    encoding=chardet.detect(s)["encoding"]
    if encoding:
        return s.decode(encoding)
    else:
        return s.decode("utf-8")