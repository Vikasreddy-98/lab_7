import sys

# This code exists for backwards compatibility reasons.
# I don't like it either. Just look the other way. :)

for package in ('urllib3', 'idna', ('chardet', 'cchardet')):
    if isinstance(package, tuple):
        package, alt_package = package
        try:
            locals()[package] = __import__(alt_package)
        except ImportError:
            locals()[package] = __import__(package)
    else:
        locals()[package] = __import__(package)

    # This traversal is apparently necessary such that the identities are
    # preserved (requests.packages.urllib3.* is urllib3.*)
    for mod in list(sys.modules):
        if mod == package or mod.startswith(package + '.'):
            sys.modules['requests.packages.' + mod] = sys.modules[mod]

# Kinda cool, though, right?
