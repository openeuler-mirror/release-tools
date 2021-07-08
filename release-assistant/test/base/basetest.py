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
The test base class contains some public methods
"""
import argparse
import json
import sys
import unittest
from io import StringIO

import requests

from javcra.cli.base import BaseCommand


class TestBase(unittest.TestCase):
    """
    The test base class contains some public methods
    Args:
        unittest: unittest framework used
    """
    cmd_class = None

    def setUp(self) -> None:
        """
        Each test case needs to be run
        first before it can be run
        Returns:

        """
        self._to_clean_patchers = []
        self.stdout_io = StringIO()
        self.expect_str = ""
        self.command_params = []
        sys.stdout = sys.stderr = self.stdout_io

    def _execute_command(self):
        """
        To Simulated execution command line
        Returns:
            None
        """
        if self.cmd_class is None:
            raise ValueError(
                f"please check cmd_class variable in your {self},"
                f"assignment current do command class name"
            )

        ins = self.cmd_class()
        args = ins.sub_parse.parse_args(self.command_params)
        ins.do_command(args)

    @property
    def print_result(self):
        """
        execute cmd and return print redirect content
        Returns:
            print redirect result
        """
        self._execute_command()
        return self.stdout_io.getvalue().strip()

    def assert_result(self):
        """
        to assert command lines result as same sa excepted str
        Returns:
            None
        """
        self.assertEqual(
            self.expect_str.strip().strip("\r\n").strip("\n"), self.print_result
        )

    def tearDown(self) -> None:
        """
        The last to run after each test case is run
        Returns:

        """
        BaseCommand.parser = argparse.ArgumentParser(
            description="Just A Very Convenient Release Assistant"
        )
        BaseCommand.subparsers = BaseCommand.parser.add_subparsers(
            help="Just A Very Convenient Release Assistant"
        )
        return super().tearDown()


class TestMixin(unittest.TestCase):
    """
    The base class that sends HTTP requests
    """

    def client_request(self, url=None, method="GET", data=None):
        """
        Send the HTTP request and return the response
        Args:
            url: url
            method: method
            data: data

        Returns:
            response_content: Parsed response data
        """
        self.assertIsNotNone(url, msg="Error url")
        methods = {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
            "PATCH",
            "get",
            "post",
            "put",
            "delete",
            "options",
            "patch",
        }
        self.assertIn(method, methods, msg="Wrong way of requesting method")

        response = requests.__getattribute__(method.lower())(url, data=data)
        response_content = json.loads(response.text)
        return response_content

    def get_comments(self, owner, repo, access_token, number):
        """
        Gets all Issue ratings, as a list, and returns them
        Args:
            owner: owner
            repo: repo
            access_token: access_token
            number: number

        Returns:
            cve_comments: Comment information for all issues
        """
        issue_comment_url = "https://gitee.com/api/v5/repos/{owner}/{repo}/issues/" \
                            "{number}/comments".format(
            owner=owner, repo=repo, number=number
        )
        response_content = self.client_request(
            issue_comment_url, data=dict(access_token=access_token)
        )
        # Comment information for all issues
        cve_comments = [com.get("body") for com in response_content]

        return cve_comments

    def assert_comment_in_comments(self, comment, owner, repo, access_token, number):
        """
        Asserts if the newly created comment is in all comment information
        Args:
            comment: comment
            owner: owner
            repo: repo
            access_token: access_token
            number: number

        Returns:
            None
        """
        cve_comments = self.get_comments(owner, repo, access_token, number)
        self.assertIn(comment, cve_comments)

    def get_issue_describe(self, owner, repo, number, access_token):
        """
        Gets the description information for the issue
        Args:
            owner: owner
            repo: repo
            number: number
            access_token: access_token

        Returns:
            describe: All comment information in the issue
        """
        issuse_describe_url = "https://gitee.com/api/v5/repos/{owner}/{repo}/issues/{number}".format(
            owner=owner, repo=repo, number=number
        )
        describe = self.client_request(
            issuse_describe_url, data=dict(access_token=access_token)
        ).get("body")
        return describe
