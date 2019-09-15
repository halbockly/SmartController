import ConfigParser

inifile = ConfigParser.SafeConfigParser()
inifile.read("./setting/test.ini")



_get(inifile, section, "hoge1")

def _get(inifile):
    try:
        return inifile.get("", name)
    except Exception, e:
        return "error: could not read " + name