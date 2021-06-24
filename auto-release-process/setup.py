#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Auto Release Process installation configuration
file for software packaging
"""
import os

from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages

setup(
    name='arp',
    version='1.0.0',
    packages=find_packages(),
    license='Dependency package management',
    long_description=open('README.md', encoding='utf-8').read(),
    author='wangyiru',
    data_files=[
        ('/usr/bin', ['arp/arp'])
    ],
    zip_safe=False
)
