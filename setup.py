import setuptools

VERSION = "0.9.4"

DESCRIPTION = "GUI for converting MEG data to BIDS format"
URL = "https://macquarie-meg-research.github.io/Biscuit/"
DOWNLOAD_URL = "https://github.com/Macquarie-MEG-Research/Biscuit"
LONG_DESCRIPTION = open('README.md').read()

setuptools.setup(
    name="Biscuit",
    version=VERSION,
    author="Matt Sanderson",
    author_email="matt.sanderson@mq.edu.au",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    include_package_data=True,
    download_url=DOWNLOAD_URL,
    packages=setuptools.find_packages(),
    # TODO: may not work on linux?
    install_requires=['numpy', 'scipy', 'matplotlib', 'pandas', 'Pygments',
                      'Pillow', 'mne', 'requests'],
    license="MIT",
    platform="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['Biscuit = Biscuit.__main__:main']
    }
)
