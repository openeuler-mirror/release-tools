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
import sys
import argparse
import json
import unittest
from unittest.mock import PropertyMock
from io import StringIO
from unittest import mock
from pathlib import Path
from javcra.cli.base import BaseCommand
import requests

MOCK_DATA_FOLDER = str(Path(Path(__file__).parents[1], "mock_data"))


class MakeObject(object):
    """
    class for object
    """

    def __init__(self, dict_):
        self.__dict__.update(dict_)


def dict_2_object(content):
    """
    dict to object
    Args:
        content: content type:dict

    Returns:

    """
    return json.loads(json.dumps(content), object_hook=MakeObject)


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

    def _to_add_cleanup(self):
        """_to_add_cleanup"""
        for single_patcher in self._to_clean_patchers:
            self.addCleanup(single_patcher.stop)
        self._to_clean_patchers.clear()

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
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self._to_add_cleanup()
        return super().tearDown()


class TestMixin(TestBase):
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

    def _create_patch(self, mock_name, **kwargs):
        """create_patch

        Args:
            method_name (str): mock method or attribute name

        """
        patcher = mock.patch(mock_name, **kwargs)
        self._to_clean_patchers.append(patcher)
        patcher.start()

    def _to_update_kw_and_make_mock(self, mock_name, effect=None, **kwargs):
        """_to_update_kw_and_make_mock

        Args:
            mock_name (str):  mock method or attribute name
            effect (Any, optional): side effect value

        Raises:
            ValueError: If the side_effect or return_value keyword parameter is not specified
                        specify the value of the effect keyword parameter
        """
        if "side_effect" not in kwargs and "return_value" not in kwargs:
            if effect is None:
                raise ValueError(
                    "If the side_effect or return_value keyword parameter is not specified,"
                    "specify the value of the effect keyword parameter"
                )
            kwargs["side_effect"] = effect
        self._create_patch(mock_name, **kwargs)

    @staticmethod
    def read_file_content(path, folder=MOCK_DATA_FOLDER, is_json=True):
        """to read file content if is_json is True return dict else return str

        Args:
            path: Absolute path or the path relative of mock_data folder
            is_json: if is True use json.loads to load data else not load

        Raises:
            FileNotFoundError:Check Your path Please
            JSONDecodeError:Check Your Josn flie Please

        Returns:
            file's content:if is_json is True return dict else return str
        """
        curr_path = Path(folder, path)
        if Path(path).is_absolute():
            curr_path = path

        with open(str(curr_path), "r", encoding="utf-8") as f_p:
            if is_json:
                return json.loads(f_p.read())
            else:
                return f_p.read()

    def mock_request(self, **kwargs):
        """mock_request"""
        self._to_update_kw_and_make_mock(
            "requests.request",
            **kwargs,
        )

    def mock_requests_get(self, **kwargs):
        """mock_requests_get"""
        self._to_update_kw_and_make_mock(
            "requests.get",
            **kwargs,
        )

    def mock_requests_post(self, **kwargs):
        """mock_requests_post"""
        self._to_update_kw_and_make_mock(
            "requests.post",
            **kwargs,
        )

    def mock_obs_cloud_list_objects(self, **kwargs):
        """mock_obs_cloud_list_objects"""
        self._to_update_kw_and_make_mock(
            "obs.ObsClient.listObjects",
            **kwargs,
        )

    def mock_obs_cloud_get_objects(self, **kwargs):
        """mock_obs_cloud_get_objects"""
        self._to_update_kw_and_make_mock(
            "obs.ObsClient.getObject",
            **kwargs,
        )

    def mock_obs_cloud_head_bucket(self, **kwargs):
        """mock_obs_cloud_headBucket"""
        self._to_update_kw_and_make_mock(
            "obs.ObsClient.headBucket",
            **kwargs,
        )

    def mock_obs_cloud_delete_object(self, **kwargs):
        """mock_obs_cloud_deleteObject"""
        self._to_update_kw_and_make_mock(
            "obs.ObsClient.deleteObject",
            **kwargs,
        )

    def mock_obs_cloud_put_file(self, **kwargs):
        """mock_obs_cloud_putFile"""
        self._to_update_kw_and_make_mock(
            "obs.ObsClient.putFile",
            **kwargs,
        )

    def mock_jenkins_build_job(self, **kwargs):
        """mock_jenkins_build_job"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.build_job",
            **kwargs,
        )

    def mock_jenkins_create_job(self, **kwargs):
        """mock_jenkins_create_job"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.create_job",
            **kwargs,
        )

    def mock_jenkins_create_folder(self, **kwargs):
        """mock_jenkins_create_folder"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.create_folder",
            **kwargs,
        )

    def mock_jenkins_get_job_info(self, **kwargs):
        """mock_jenkins_get_job_info"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.get_job_info",
            **kwargs,
        )

    def mock_jenkins_get_build_info(self, **kwargs):
        """mock_jenkins_get_build_info"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.get_build_info",
            **kwargs,
        )

    def mock_jenkins_get_build_console_output(self, **kwargs):
        """mock_jenkins_get_build_console_output"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.get_build_console_output",
            **kwargs,
        )

    def mock_jenkins_get_queue_item(self, **kwargs):
        """mock_jenkins_get_queue_item"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.get_queue_item",
            **kwargs,
        )

    def mock_jenkins_get_job_config(self, **kwargs):
        """mock_jenkins_get_job_config"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.get_job_config",
            **kwargs,
        )

    def mock_jenkins_build_job_url(self, **kwargs):
        """mock_jenkins_build_job_url"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.build_job_url",
            **kwargs,
        )

    def mock_jenkins_job_exists(self, **kwargs):
        """mock_jenkins_job_exists"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.job_exists",
            **kwargs,
        )

    def mock_jenkins_delete_job(self, **kwargs):
        """mock_jenkins_delete_job"""
        self._to_update_kw_and_make_mock(
            "jenkins.Jenkins.delete_job",
            **kwargs,
        )

    def mock_pandas_read_excel(self, **kwargs):
        """mock_pandas_read_excel"""
        self._to_update_kw_and_make_mock(
            "pandas.read_excel",
            **kwargs,
        )

    def mock_subprocess_check_output(self, **kwargs):
        """mock_subprocess_check_output"""
        self._to_update_kw_and_make_mock(
            "subprocess.check_output",
            **kwargs,
        )

    def make_expect_data(self, status_code, file_name, folder=MOCK_DATA_FOLDER):
        """
        make expected data
        Args:
            status_code: status code
            folder: folder
            file_name: file of expected data
        Returns:
        """
        mock_r = requests.Response()
        mock_r.status_code = status_code
        self._to_update_kw_and_make_mock(
            "requests.Response.text",
            new_callable=PropertyMock,
            return_value=self.read_file_content(file_name, folder=folder, is_json=False),
        )
        return mock_r

    @staticmethod
    def make_object_data(status_code, text=""):
        """
        make object data
        Args:
            status_code: status code
            text: text
        Returns:
        """
        object_r = dict_2_object({})
        object_r.status = status_code
        object_r.status_code = status_code
        object_r.text = text
        return object_r

    @staticmethod
    def make_obs_cloud_data(status, body=""):
        """
        make obs cloud data
        Args:
            status: status code
            body: body
        Returns:
        """
        mock_r = requests.Response()
        mock_r.status = status
        mock_r.status_code = status
        mock_r.body = dict_2_object(body)
        return mock_r

    def make_need_content(self, file_name, mock_data_file, is_json=False):
        """
        make need data
        Args:
            file_name: file name
            mock_data_file: file path
            is_json: json flag
        Returns:
        """
        read_data = self.read_file_content(file_name, folder=mock_data_file, is_json=is_json)
        need_content = self.make_object_data(200, read_data)
        return need_content

    def make_need_obs_cloud_data(self, file_name, mock_data_file, status_code):
        """
        make need obs cloud data
        Args:
            file_name: file name
            mock_data_file: file path
            status_code: status code
        Returns:
        """
        read_data = self.read_file_content(file_name, folder=mock_data_file)
        need_obs_content = self.make_obs_cloud_data(status_code, read_data)
        return need_obs_content
