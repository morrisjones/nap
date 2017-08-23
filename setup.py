#!/usr/bin/env python

from distutils.core import setup, find_packages
import nap

setup(name='nap',
      version=nap.__version__,
      packages=find_packages(),
      )

