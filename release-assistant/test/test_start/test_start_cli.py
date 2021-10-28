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
TestStart
"""
import datetime
import os
from pathlib import Path
from test.base.basetest import TestMixin
from requests.exceptions import RequestException
from javcra.cli.commands.startpart import StartCommand
import pandas as pd

MOCK_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_data")


class TestStart(TestMixin):
    """
    class for test TestStart
    """
    cmd_class = StartCommand

    def test_success(self):
        """
        test success
        """
        self.expect_str = """
[INFO] start update successfully.
        """
        resp = self.make_expect_data(200, 'startpart.txt')
        mock_init_r = self.make_need_content('init_success_data.txt', MOCK_DATA_FILE)
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        con = self.read_file_content('mock_obs_data.json', folder=MOCK_DATA_FILE)
        for con_key in con['contents']:
            con_key["key"] = "cve-manager-updateinfo/{}/{}".format(
                datetime.date(datetime.date.today().year, datetime.date.today().month,
                              datetime.date.today().day).strftime('%Y-%m-%d'), con_key["key"])
        mock_r = self.make_obs_cloud_data(200, con)
        self.mock_obs_cloud_list_objects(return_value=mock_r)
        self.mock_obs_cloud_get_objects(return_value=mock_r)
        read_excel = pd.read_excel(Path(MOCK_DATA_FILE, "mock_cve_data.xlsx"), sheet_name="cve_list")
        self.mock_pandas_read_excel(return_value=read_excel)
        self.mock_request(side_effect=[resp, resp, resp, mock_init_r])
        mock_get_r = self.make_object_data(200, "The number of requests is too frequent, "
                                                "please try again later, there is currently a task being processed")
        self.mock_requests_get(side_effect=[mock_get_r])
        self.assert_result()

    def test_failed(self):
        """
        test failed
        """
        self.expect_str = """
[ERROR] failed to start update.
        """
        resp = self.make_expect_data(200, 'startpart.txt')
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        con = self.read_file_content('mock_obs_data.json', folder=MOCK_DATA_FILE)
        for con_key in con['contents']:
            con_key["key"] = "cve-manager-updateinfo/{}/{}".format(
                datetime.date(datetime.date.today().year, datetime.date.today().month,
                              datetime.date.today().day).strftime('%Y-%m-%d'), con_key["key"])
        mock_r = self.make_obs_cloud_data(200, con)
        self.mock_obs_cloud_list_objects(return_value=mock_r)
        self.mock_obs_cloud_get_objects(return_value=mock_r)
        read_excel = pd.read_excel(Path(MOCK_DATA_FILE, "mock_cve_data.xlsx"), sheet_name="cve_list")
        self.mock_pandas_read_excel(return_value=read_excel)
        self.mock_request(side_effect=[resp, resp, resp, RequestException])
        mock_get_r = self.make_object_data(200)
        self.mock_requests_get(side_effect=[mock_get_r])
        self.assert_result()

    def test_validate_failed(self):
        """
        test validate failed
        """
        self.expect_str = """
Parameter validation failed
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", ""]
        self.assert_result()

    def test_request_status_408(self):
        """test_request_status_408"""
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
"""
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        mock_r = self.make_object_data(408)
        self.mock_request(return_value=mock_r)
        self.assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
"""
        self.mock_request(side_effect=[RequestException])
        self.assert_result()

    def test_no_permission(self):
        """
        test no permission
        """
        self.expect_str = """
[ERROR] The current user does not have relevant operation permissions
        """

        self.command_params = ["--giteeid=onetwothree", "--token=example", "--useremail=mary@123.com",
                               "--ak=forexample", "--sk=forexample", "I40321"]
        resp = self.make_expect_data(200, 'startpart.txt')
        self.mock_request(side_effect=[resp])
        self.assert_result()

    def test_no_personnel_authority(self):
        """
        test no personnel authority
        """
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        resp = self.make_expect_data(200, 'mock_incorrect_issue.txt')
        self.mock_request(side_effect=[resp])
        self.assert_result()

    def test_resp_body_is_none(self):
        """
        test resp body is none
        """
        self.expect_str = """
[ERROR] failed to start update.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        resp = self.make_expect_data(200, 'startpart.txt')
        issue_body_is_none_data = self.read_file_content('mock_issue_is_none.txt', folder=MOCK_DATA_FILE,
                                                         is_json=False)
        mock_issue_body_is_none_r = self.make_object_data(200, issue_body_is_none_data)
        self.mock_request(side_effect=[resp, mock_issue_body_is_none_r])
        self.assert_result()

    def test_already_operated(self):
        """
        test already operated
        """
        self.expect_str = """
[ERROR] failed to start update.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        resp = self.make_expect_data(200, 'startpart.txt')
        already_operated_data = self.read_file_content('already_operated.txt', folder=MOCK_DATA_FILE,
                                                       is_json=False)
        mock_already_operated_r = self.make_object_data(200, already_operated_data)
        self.mock_request(side_effect=[resp, mock_already_operated_r])
        self.assert_result()

    def test_download_file_failed(self):
        """
        test download file failed
        """
        self.expect_str = """
[ERROR] failed to start update.
        """
        resp = self.make_expect_data(200, 'startpart.txt')
        self.command_params = ["--giteeid=Mary", "--token=example", "--useremail=mary@123.com", "--ak=forexample",
                               "--sk=forexample", "I40321"]
        con = self.read_file_content('mock_obs_data.json', folder=MOCK_DATA_FILE)
        for con_key in con['contents']:
            con_key["key"] = "cve-manager-updateinfo/{}/{}".format(
                datetime.date(datetime.date.today().year, datetime.date.today().month,
                              datetime.date.today().day).strftime('%Y-%m-%d'), con_key["key"])
        mock_listobjects_r = self.make_obs_cloud_data(200, con)
        self.mock_obs_cloud_list_objects(return_value=mock_listobjects_r)
        mock_getobjects_r = self.make_object_data(400)
        self.mock_obs_cloud_get_objects(return_value=mock_getobjects_r)
        read_excel = pd.read_excel(Path(MOCK_DATA_FILE, "mock_cve_data.xlsx"), sheet_name="cve_list")
        self.mock_pandas_read_excel(return_value=read_excel)
        self.mock_request(side_effect=[resp, resp, resp, resp, resp, resp, resp])
        mock_get_r = self.make_object_data(200)
        self.mock_requests_get(side_effect=[mock_get_r])
        self.assert_result()
