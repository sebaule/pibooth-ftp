#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from io import open
import os.path as osp
from setuptools import setup

HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import pibooth_ftp as plugin  # Import after sys.path modification

def main():
    setup(
        name="pibooth-ftp",
        version=plugin.__version__,
        description="A pibooth plugin for FTP upload and URL shortening",
        long_description=open(osp.join(HERE, 'README.md'), encoding='utf-8').read(),
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Natural Language :: English',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Sébastien Baule",
        author_email="applications@baule.fr",
        url="https://github.com/pibooth/pibooth-ftp",
        download_url="https://github.com/pibooth/pibooth-ftp/archive/{}.tar.gz".format(plugin.__version__),
        license='MIT',
        platforms=['unix', 'linux'],
        keywords=[
            'Raspberry Pi',
            'camera',
            'photobooth',
            'ftp',
            'pibooth',
            'extension',
            'plugin'
        ],
        py_modules=['pibooth_ftp'],
        python_requires=">=3.6",
        install_requires=[
            'pibooth>=2.0.0',
            'requests'
        ],
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={'pibooth.plugin': ["ftp = pibooth_ftp"]},
        include_package_data=True,
    )

if __name__ == '__main__':
    main()
