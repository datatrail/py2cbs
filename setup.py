from distutils.core import setup
from py2cbs import __author__, __email__, __license__, __package__, __version__

setup(
    name = 'py2cbs',
    version = __version__,
    description = 'Python client library for CBS (Netherlands Statistics) Open Data',
    long_description = 'Py2cbs is a small client library for working with CBS (Netherlands Statistics) Open Data from within Python applications and from the command line.',
    packages = [__package__],
    author = __author__,
    author_email = __email__,
    license=__license__,
    keywords='CBS (Netherlands Statistics) Open Data'   
)
