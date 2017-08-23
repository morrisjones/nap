#!/usr/bin/env python

from setuptools import setup, find_packages
import nap

setup(name='nap',
      version=nap.__version__,
      packages=find_packages(),
      package_data={'nap': ['ACBLgame*']},
      )

