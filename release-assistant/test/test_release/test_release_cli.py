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
TestRelease
"""
import os
from test.base.basetest import TestMixin
from javcra.cli.commands.releasepart import ReleaseCommand

MOCK_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_data")


class TestRelease(TestMixin):
    """
    class for test TestRelease
    """
    cmd_class = ReleaseCommand

    def test_checkok_success(self):
        """
        test checkok success
        """
        self.expect_str = """
[INFO] successfully create transfer standard rpm jenkins res
[INFO] successfully create transfer epol rpm jenkins res
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=checkok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'releasepart.txt')
        self.prepare_jenkins_data()
        self.mock_subprocess_check_output(return_value=b'published-Epol-src')
        mock_create_standard_comment = self.make_need_content('create_standard_comments_success.txt', MOCK_DATA_FILE)
        mock_create_epol_comment = self.make_need_content('create_epol_comments_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, resp, mock_create_standard_comment, mock_create_epol_comment])
        self.assert_result()

    def test_checkok_failed(self):
        """
        test checkok failed
        """
        self.expect_str = """
during the operation checkok, a failure occurred, and the cause of the error was transfer standard rpm jenkins res: No comment information
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=checkok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'releasepart.txt')
        self.prepare_jenkins_data()
        self.mock_jenkins_build_job(return_value=0)
        self.mock_subprocess_check_output(return_value=b'published-Epol-src')
        self.mock_request(side_effect=[resp, resp, resp, resp])
        self.assert_result()

    def test_cvrfok_success(self):
        """
        test cvrfok success
        """
        self.expect_str = """
successful announcement
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=cvrfok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'releasepart.txt')
        mock_post_data = self.make_need_content('mock_post_data.txt', MOCK_DATA_FILE)
        self.mock_request(return_value=resp)
        self.mock_requests_post(return_value=mock_post_data)
        self.assert_result()

    def test_cvrfok_status_code_404(self):
        """
        test cvrfok failed
        """
        self.expect_str = """
during the operation cvrfok, a failure occurred, and the cause of the error was failed to publish announcement
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=cvrfok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'releasepart.txt')
        mock_post_data = self.make_object_data(404, "404 not found")
        self.mock_request(return_value=resp)
        self.mock_requests_post(return_value=mock_post_data)
        self.assert_result()

    def test_cvrfok_json_decode_error(self):
        """
        test cvrfok json decode error
        """
        self.expect_str = """
during the operation cvrfok, a failure occurred, and the cause of the error was failed to publish announcement
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=cvrfok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'releasepart.txt')
        mock_post_data = self.make_object_data(200, "")
        self.mock_request(return_value=resp)
        self.mock_requests_post(return_value=mock_post_data)
        self.assert_result()

    def test_parameter_validation_failed(self):
        """
        test parameter validation failed
        """
        self.expect_str = """
Parameter validation failed
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=checkok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", ""]
        self.assert_result()

    def test_no_personnel_authority(self):
        """test_no_personnel_authority"""
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
"""
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=checkok", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--publishuser=tom", "--publishkey=tomkey", "I40769"]
        resp = self.make_expect_data(200, 'mock_incorrect_issue.txt')
        self.mock_request(side_effect=[resp])
        self.assert_result()

    def prepare_jenkins_data(self):
        """
        prepare jenkins mock data
        """
        self.mock_jenkins_build_job(return_value=2)
        self.mock_jenkins_get_queue_item(
            return_value=self.read_file_content("get_queue_item.json", folder=MOCK_DATA_FILE))
        self.mock_jenkins_get_job_info(
            return_value=self.read_file_content("get_job_info.json", folder=MOCK_DATA_FILE))
        self.mock_jenkins_get_build_info(
            return_value=self.read_file_content("get_build_info.json", folder=MOCK_DATA_FILE))
        self.mock_jenkins_build_job_url(
            return_value=self.read_file_content("build_job_url.txt", folder=MOCK_DATA_FILE, is_json=False))
