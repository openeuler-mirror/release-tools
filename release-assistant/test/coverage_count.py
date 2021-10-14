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
# -*- coding:utf-8 -*-
"""
Count all test cases
"""
import os
import sys
import unittest

import coverage
from coverage import CoverageException

suite = unittest.TestSuite()

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

TEST_CASE_PATH = os.path.join(BASE_PATH, "test")

cov = coverage.coverage(include=[BASE_PATH + "/javcra/*"],
                        omit=["*__init__.py", "*/check_requires/*.py", "*/api/obscloud.py"])


def specify_case(file_path):
    """
    Test specify test cases
    Args:
        file_path: test cases file path

    Returns: discover result
    """
    discover = unittest.defaultTestLoader.discover(
        file_path, pattern="test*.py", top_level_dir=file_path
    )
    return discover


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    args = sys.argv
    cov.start()
    test_case_files = [
        os.path.join(TEST_CASE_PATH, "test_start/"),
        os.path.join(TEST_CASE_PATH, "test_modify/"),
        os.path.join(TEST_CASE_PATH, "test_check/"),
        os.path.join(TEST_CASE_PATH, "test_release/")
    ]

    errors = []
    failures = []
    for file in test_case_files:
        runner_result = runner.run(specify_case(file))
        errors.extend(runner_result.errors)
        failures.extend(runner_result.failures)

    if any([errors, failures]):
        sys.exit(1)

    cov.stop()
    try:
        cov.report(show_missing=True)
        # cov.html_report()
    except CoverageException:
        print("No data to report")
        sys.exit(1)
