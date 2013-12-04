from setuptools import setup

from data import __version__


version_str = ".".join(str(n) for n in __version__)


setup(
    name = "mohawk-data-platform",
    version = version_str,
    license = "BSD",
    description = "A Django app for editing and publishing arbitrary JSON data in a form-based environment.",
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "http://github.com/mohawkhq/mohawk-data-platform",
    packages = [
        "data",
        "data.migrations",
    ],
    package_data = {
        "data": [
            "static/data/img/*.png",
        ],
    },
    zip_safe = False,
    install_requires = [
        "django-cross-origin==0.9.0",
        "jsonfield==0.9.20",
    ],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)
