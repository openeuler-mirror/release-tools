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
TestCheck
"""
import os

from requests import RequestException
from test.base.basetest import TestMixin
from javcra.cli.commands.checkpart import CheckCommand

MOCK_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_data")
EXPECT_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "expected_data")


class TestCheck(TestMixin):
    """
    class for test TestCheck
    """
    cmd_class = CheckCommand

    def test_check_status_success(self):
        """
        test check status success
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[INFO] successfully to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        mock_post_data = self.make_need_content('mock_post_data.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_requests_post(return_value=mock_post_data)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, mock_repo_list_data, resp])
        self.assert_result()

    def test_check_status_failed(self):
        """
        test check status failed
        """
        self.expect_str = """
during the operation status, a failure occurred, and the cause of the error was failed to update status in check part.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_request(
            side_effect=[resp, resp, RequestException])
        self.assert_result()

    def test_count_issue_status_failed(self):
        """
        test count issue status failed
        """
        self.expect_str = """
[INFO] successfully update status in check part.
during the operation status, a failure occurred, and the cause of the error was the status of the issue is not all completed, please complete first
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_abnormal_r = self.make_need_content('mock_abnormal_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, RequestException, mock_abnormal_r])
        self.assert_result()

    def test_send_repo_info_requests_post_failed(self):
        """
        test send repo info requests post failed
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_requests_post(return_value=None)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, mock_repo_list_data, resp])
        self.assert_result()

    def test_send_repo_info_request_exception(self):
        """
        test send repo info test send repo info request exception
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_requests_post(side_effect=[RequestException])
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, mock_repo_list_data, resp])
        self.assert_result()

    def test_send_repo_info_error_code_400(self):
        """
        test send repo info error code 400
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        mock_post_data = self.make_need_content('mock_error_post_data.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_requests_post(return_value=mock_post_data)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, mock_repo_list_data, resp])
        self.assert_result()

    def test_send_repo_info_request_repo_url_failed(self):
        """
        test send repo info requests post failed
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, RequestException, resp])
        self.assert_result()

    def test_send_repo_info_get_update_list_failed(self):
        """
        test send repo info requests post failed
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_bugfix_r = self.make_need_content('mock_bugfix_issue.txt', MOCK_DATA_FILE)
        mock_install_r = self.make_need_content('mock_install_issue.txt', MOCK_DATA_FILE)
        mock_check_r = self.make_need_content('check_status_success.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, mock_install_r, resp, resp, resp, mock_bugfix_r, mock_check_r,
                         resp, resp, mock_install_r, mock_bugfix_r, resp, resp, resp, resp, mock_repo_list_data,
                         RequestException])
        self.assert_result()

    def test_block_has_no_related_issues(self):
        """
        test block has no related issues
        """
        self.expect_str = """
[INFO] successfully update status in check part.
[INFO] All issues are completed, the next step is sending repo to test platform.
[ERROR] failed to send repo info.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_no_related_issues_r = self.make_need_content('mock_no_related_issues.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, mock_no_related_issues_r, mock_no_related_issues_r, mock_no_related_issues_r,
                         RequestException])
        self.assert_result()

    def test_people_review_success(self):
        """
        test people review success
        """
        self.expect_str = """
[INFO] successfully operate test in check part.   
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=test", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_comment_r = self.make_need_content('mock_issue_comment.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_comment_r])
        self.assert_result()

    def test_create_issue_comment_failed(self):
        """
        test create issue comment failed
        """
        self.expect_str = """
[ERROR] failed to operate test in check part.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=test", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_request(side_effect=[resp, resp, resp, RequestException])
        self.assert_result()

    def test_empty_related_personnel_information(self):
        """
        test empty related personnel information
        """
        self.expect_str = """
[ERROR] failed to operate test in check part.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=test", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_empty_related_personnel_r = self.make_need_content('mock_empty_related_personnel.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_empty_related_personnel_r])
        self.assert_result()

    def test_parameter_validation_failed(self):
        """
        test parameter validation failed
        """
        self.expect_str = """
Parameter validation failed
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", ""]
        self.assert_result()

    def test_no_personnel_authority(self):
        """test_no_personnel_authority"""
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
"""
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=status", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'mock_incorrect_issue.txt')
        self.mock_request(side_effect=[resp])
        self.assert_result()

    def test_check_requires_success(self):
        """
        test check requires success
        """
        self.expect_str = self.read_file_content("requires_success.txt", folder=EXPECT_DATA_FILE, is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_subprocess_check_output(
            side_effect=[b"published-everything-src", b"published-everything-src", b"published-everything-src",
                         b"published-everything-src", None, b"published-Epol-src", b"published-everything-src",
                         b"published-everything-src", b"published-everything-src", b"published-everything-src", None,
                         b"published-Epol-src", b"published-everything-src", b"published-everything-src",
                         b"published-everything-src", b"published-everything-src", None, b"published-Epol-src"])
        mock_add_repo_r = self.make_need_content('mock_add_repo_success.txt', MOCK_DATA_FILE)
        mock_exist_issues = self.make_need_content('exist_issues.txt', MOCK_DATA_FILE)
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        mock_create_install_jenkins_comment = self.make_need_content('create_install_jenkins_comments_success.txt',
                                                                     MOCK_DATA_FILE)
        mock_create_build_jenkins_comment = self.make_need_content('create_build_jenkins_comments_success.txt',
                                                                   MOCK_DATA_FILE)
        mock_create_build_issue = self.make_need_content('create_build_issue_success.txt', MOCK_DATA_FILE)
        mock_create_install_issue = self.make_need_content('create_install_issue_success.txt', MOCK_DATA_FILE)
        mock_checkpart_add_build = self.make_need_content('checkpart_add_build_success.txt', MOCK_DATA_FILE)
        mock_checkpart_add_install = self.make_need_content('checkpart_add_install_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_repo_list_data, mock_create_jenkins_comment, mock_create_jenkins_comment, resp, resp,
                         resp, resp, mock_add_repo_r, mock_create_build_jenkins_comment,
                         mock_create_install_jenkins_comment, mock_create_install_jenkins_comment, resp, resp,
                         mock_exist_issues, mock_create_build_issue, resp, resp, mock_create_build_issue,
                         mock_checkpart_add_build, resp, resp, mock_exist_issues, mock_create_install_issue, resp, resp,
                         resp, mock_create_install_issue, mock_checkpart_add_install])
        self.assert_result()

    def test_get_require_delete_file_failed(self):
        """
        test get require and delete file failed
        """
        self.expect_str = self.read_file_content("get_require_delete_file_failed.txt", folder=EXPECT_DATA_FILE,
                                                 is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data(delete_status_code=400)
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_request(side_effect=[resp, resp, resp, resp, resp, resp])
        self.assert_result()

    def test_get_repo_in_table_failed(self):
        """
        test add repo in table failed
        """
        self.expect_str = self.read_file_content("add_repo_in_table_failed.txt", folder=EXPECT_DATA_FILE, is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_create_jenkins_comment, resp, resp, resp, resp, RequestException])
        self.assert_result()

    def test_create_jenkins_comment_and_build_comment_and_install_comment_failed(self):
        """
        test create jenkins comment and build comment and install comment failed
        """
        self.expect_str = self.read_file_content("create_comment_failed.txt", folder=EXPECT_DATA_FILE,
                                                 is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        mock_exist_issues = self.make_need_content('exist_issues.txt', MOCK_DATA_FILE)
        mock_add_repo_r = self.make_need_content('mock_add_repo_success.txt', MOCK_DATA_FILE)
        mock_create_build_issue = self.make_need_content('create_build_issue_success.txt', MOCK_DATA_FILE)
        mock_create_install_issue = self.make_need_content('create_install_issue_success.txt', MOCK_DATA_FILE)
        mock_checkpart_add_build = self.make_need_content('checkpart_add_build_success.txt', MOCK_DATA_FILE)
        mock_checkpart_add_install = self.make_need_content('checkpart_add_install_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         RequestException, resp, resp, resp, resp, mock_add_repo_r, RequestException, RequestException,
                         resp, resp, mock_exist_issues, mock_create_build_issue, resp, resp, mock_create_build_issue,
                         mock_checkpart_add_build, resp, resp, mock_exist_issues, mock_create_install_issue, resp, resp,
                         mock_create_install_issue, mock_checkpart_add_install])
        self.assert_result()

    def test_check_requires_epol_list_failed(self):
        """
        test check requires epol list failed
        """
        self.expect_str = self.read_file_content("check_requires_epol_list_failed.txt", folder=EXPECT_DATA_FILE,
                                                 is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        resp = self.make_expect_data(200, 'check_epol_list.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        self.mock_subprocess_check_output(return_value=b'published-Epol-src')
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_create_jenkins_comment, resp, resp, resp, resp, RequestException])
        self.assert_result()

    def test_get_update_issue_branch_and_get_update_list_failed(self):
        """
        test get update issue branch and get update list failed
        """
        self.expect_str = """
during the operation requires, a failure occurred, and the cause of the error was failed to get branch name.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        branch_abnormal_r = self.make_need_content('check_branch_abnormal.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, branch_abnormal_r, branch_abnormal_r, RequestException])
        self.assert_result()

    def test_branch_name_is_none_and_get_update_list_failed(self):
        """
        test branch name is none and get update list failed
        """
        self.expect_str = """
during the operation requires, a failure occurred, and the cause of the error was failed to get branch name.
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        branch_abnormal_r = self.make_need_content('branch_name_is_none.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, branch_abnormal_r, branch_abnormal_r, RequestException])
        self.assert_result()

    def test_create_jenkins_comment_failed(self):
        """
        failed to create  jenkins comment
        """
        self.expect_str = """
[ERROR] failed to get requires.
already exists the repo url, then update the pkglist in repo.
during the operation requires, a failure occurred, and the cause of the error was transfer standard rpm jenkins res: No comment information. The content is:  [].
        """
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        self.mock_jenkins_build_job(return_value=0)
        self.mock_request(return_value=resp)
        self.assert_result()

    def test_download_pkg_log_write_back_create_install_build_issue_failed(self):
        """
        test download pkg log write back create install build issue failed
        """
        self.expect_str = self.read_file_content("download_pkg_log_failed.txt",
                                                 folder=EXPECT_DATA_FILE, is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data(get_objects_status_code=400)
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        mock_add_repo_r = self.make_need_content('mock_add_repo_success.txt', MOCK_DATA_FILE)
        mock_exist_issues = self.make_need_content('single_exist_issues.txt', MOCK_DATA_FILE)
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        mock_create_install_jenkins_comment = self.make_need_content('create_install_jenkins_comments_success.txt',
                                                                     MOCK_DATA_FILE)
        mock_create_build_jenkins_comment = self.make_need_content('create_build_jenkins_comments_success.txt',
                                                                   MOCK_DATA_FILE)
        mock_issue_comment = self.make_need_content('mock_issue_comment.txt', MOCK_DATA_FILE)
        mock_create_build_issue = self.make_need_content('create_build_issue_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_create_jenkins_comment, resp, resp, resp, resp, mock_add_repo_r,
                         mock_create_build_jenkins_comment, mock_create_install_jenkins_comment, resp, resp,
                         mock_exist_issues, mock_issue_comment, mock_create_build_issue, RequestException,
                         RequestException])
        self.assert_result()

    def test_write_back_create_install_build_issue_failed(self):
        """
        write_back_create_install_build_issue_failed
        """
        self.expect_str = self.read_file_content("write_back_create_install_build_issue_failed.txt",
                                                 folder=EXPECT_DATA_FILE, is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        resp = self.make_expect_data(200, 'checkpart.txt')
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        mock_add_repo_r = self.make_need_content('mock_add_repo_success.txt', MOCK_DATA_FILE)
        mock_exist_issues = self.make_need_content('exist_issues.txt', MOCK_DATA_FILE)
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        mock_create_install_jenkins_comment = self.make_need_content('create_install_jenkins_comments_success.txt',
                                                                     MOCK_DATA_FILE)
        mock_create_build_jenkins_comment = self.make_need_content('create_build_jenkins_comments_success.txt',
                                                                   MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_create_jenkins_comment, resp, resp, resp, resp, mock_add_repo_r,
                         mock_create_build_jenkins_comment, mock_create_install_jenkins_comment, resp, resp,
                         mock_exist_issues, RequestException, RequestException])
        self.assert_result()

    def test_write_back_operate_release_issue_failed(self):
        """
        write_back_operate_release_issue_failed
        """
        self.expect_str = self.read_file_content("write_back_operate_release_issue_failed.txt", folder=EXPECT_DATA_FILE,
                                                 is_json=False)
        self.command_params = ["--giteeid=Mary", "--token=example", "--type=requires", "--jenkinsuser=mary",
                               "--jenkinskey=marykey", "--ak=forexample", "--sk=forexample", "I40769"]
        resp = self.make_expect_data(200, 'checkpart.txt')
        self.prepare_jenkins_data()
        self.prepare_obs_data()
        mock_add_repo_r = self.make_need_content('mock_add_repo_success.txt', MOCK_DATA_FILE)
        mock_exist_issues = self.make_need_content('exist_issues.txt', MOCK_DATA_FILE)
        mock_repo_list_data = self.make_need_content('repo_list_data.txt', MOCK_DATA_FILE)
        mock_create_jenkins_comment = self.make_need_content('create_jenkins_comments_success.txt', MOCK_DATA_FILE)
        mock_create_install_jenkins_comment = self.make_need_content('create_install_jenkins_comments_success.txt',
                                                                     MOCK_DATA_FILE)
        mock_create_build_jenkins_comment = self.make_need_content('create_build_jenkins_comments_success.txt',
                                                                   MOCK_DATA_FILE)
        mock_create_build_issue = self.make_need_content('create_build_issue_success.txt', MOCK_DATA_FILE)
        mock_create_install_issue = self.make_need_content('create_install_issue_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, resp, resp, resp, resp, resp, resp, resp, mock_repo_list_data,
                         mock_create_jenkins_comment, resp, resp, resp, resp, mock_add_repo_r,
                         mock_create_build_jenkins_comment, mock_create_install_jenkins_comment, resp, resp,
                         mock_exist_issues, mock_create_build_issue, resp, resp, mock_create_build_issue,
                         RequestException, resp, resp, mock_exist_issues, mock_create_install_issue, resp,
                         mock_create_install_issue, RequestException])
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
        self.mock_jenkins_create_folder(return_value=True)
        self.mock_jenkins_job_exists(return_value=True)
        self.mock_jenkins_delete_job(return_value=True)
        self.mock_subprocess_check_output(return_value=b"published-everything-src")
        trigger_config = self.read_file_content('test_template_config_trigger.xml', folder=MOCK_DATA_FILE,
                                                is_json=False)
        aarch64_config = self.read_file_content('test_template_config_aarch64.xml', folder=MOCK_DATA_FILE,
                                                is_json=False)
        x86_64_config = self.read_file_content('test_template_config_x86.xml', folder=MOCK_DATA_FILE, is_json=False)
        self.mock_jenkins_get_job_config(
            side_effect=[trigger_config, aarch64_config, aarch64_config, aarch64_config, aarch64_config, aarch64_config,
                         x86_64_config, x86_64_config, x86_64_config, x86_64_config, x86_64_config])
        self.mock_jenkins_create_job(return_value=True)
        self.mock_jenkins_get_build_console_output(
            return_value=self.read_file_content('get_build_console_output.txt', folder=MOCK_DATA_FILE, is_json=False))

    def prepare_obs_data(self, file_name='mock_obs_data.json', list_status_code=200, delete_status_code=200,
                         get_objects_status_code=200):
        """
        prepare obs mock data
        """
        mock_obs_list_objects_r = self.make_need_obs_cloud_data(file_name, MOCK_DATA_FILE, list_status_code)
        mock_obs_delete_objects_r = self.make_need_obs_cloud_data(file_name, MOCK_DATA_FILE, delete_status_code)
        mock_getobjects_r = self.make_object_data(get_objects_status_code)
        self.mock_obs_cloud_get_objects(return_value=mock_getobjects_r)
        self.mock_obs_cloud_list_objects(return_value=mock_obs_list_objects_r)
        self.mock_obs_cloud_delete_object(return_value=mock_obs_delete_objects_r)
