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
TestModify
"""
import os
from requests import RequestException
from javcra.cli.commands.modifypart import ModifyCommand
from test.base.basetest import TestMixin

MOCK_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mock_data")


class TestModify(TestMixin):
    """
    class for test TestModify

    """
    cmd_class = ModifyCommand

    def test_add_cve_success(self):
        """
        test add cve success
        """
        self.expect_str = """
[INFO] add I3AQ2G in cve successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_cve_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_r, mock_r, mock_final_r, mock_final_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_bugfix_success(self):
        """
        test add bugfix success
        """
        self.expect_str = """
[INFO] add I3AQ2G in bugfix successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_bugfix_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_r, mock_final_r, mock_final_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=bugfix", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_remain_success(self):
        """
        test add remain success
        """

        self.expect_str = """
[INFO] add I3AQ2G in remain successfully.
update remain issues successfully.
"""
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_remain_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, mock_r, mock_r, resp, resp, resp, mock_r, mock_r, mock_final_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=remain", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_cve_failed(self):
        """
        test add cve failed
        """
        self.expect_str = """
[ERROR] failed to add I3AQ2G in cve.        
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_r, mock_r, resp, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_bugfix_failed(self):
        """
        test add bugfix failed
        """

        self.expect_str = """
[ERROR] failed to add I3AQ2G in bugfix.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_r, mock_r, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=bugfix", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_remain_failed(self):
        """
        test add remain failed
        """

        self.expect_str = """
[ERROR] failed to add I3AQ2G in remain.
failed to update remain issues, please check whether the issue exist in cve and bugfix part.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, mock_r, mock_r, RequestException, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=remain", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_add_remain_not_in_cve_and_bugfix(self):
        """
        test add remain not in cve and bugfix
        """

        self.expect_str = """
[INFO] add I3AQ2G in remain successfully.
failed to update remain issues, please check whether the issue exist in cve and bugfix part.
        """
        resp = self.make_expect_data(200, 'add_remain_not_in_cve_and_bugfix.txt', folder=MOCK_DATA_FILE)
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_remain_not_in_cve_and_bugfix.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, mock_r, mock_r, resp, resp, resp, mock_r, mock_r, mock_final_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--add=remain", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_delete_cve_success(self):
        """
        test delete cve success
        """

        self.expect_str = """
[INFO] delete I3V9IG in cve successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_cve_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=cve", "--token=example", "--id=I3V9IG"]
        self.assert_result()

    def test_delete_bugfix_success(self):
        """
        test delete bugfix success
        """

        self.expect_str = """
[INFO] delete I3J655 in bugfix successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_bugfix_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=bugfix", "--token=example", "--id=I3J655"]
        self.assert_result()

    def test_delete_remain_success(self):
        """
        test delete remain success
        """

        self.expect_str = """
[INFO] delete I3SZRJ in remain successfully.
update remain issues successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_remain_success.txt', MOCK_DATA_FILE)
        mock_issue_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('delete_update_remain_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r, mock_r, mock_issue_r, mock_issue_r, mock_final_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id=I3SZRJ"]
        self.assert_result()

    def test_delete_cve_failed(self):
        """
        test delete cve failed
        """

        self.expect_str = """
[ERROR] failed to delete I3V9IG in cve.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        self.mock_request(side_effect=[resp, resp, resp, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=cve", "--token=example", "--id=I3V9IG"]
        self.assert_result()

    def test_delete_bugfix_failed(self):
        """
        test delete bugfix failed
        """

        self.expect_str = """
[ERROR] failed to delete I3J655 in bugfix.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        self.mock_request(side_effect=[resp, resp, resp, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=bugfix", "--token=example", "--id=I3J655"]
        self.assert_result()

    def test_delete_remain_failed(self):
        """
        test delete remain failed
        """

        self.expect_str = """
[ERROR] failed to delete I3SZRJ in remain.
failed to update remain issues, please check whether the issue exist in cve and bugfix part.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        self.mock_request(
            side_effect=[resp, resp, resp, RequestException, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id=I3SZRJ"]
        self.assert_result()

    def test_parameter_validation_failed(self):
        """
        test parameter validation failed
        """

        self.expect_str = """
Parameter validation failed
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id"]
        self.assert_result()

    def test_no_personnel_authority(self):
        """
        test_no_personnel_authority
        """
        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
"""
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'mock_issue.txt', folder=MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp])
        self.assert_result()

    def test_request_raise_requestexception(self):
        """
        test_request_raise_requestexception
        """

        self.expect_str = """
[ERROR] Failed to get the list of personnel permissions
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id=I3AQ2G"]
        self.mock_request(side_effect=[RequestException])
        self.assert_result()

    def test_update_remain_failed(self):
        """
        test_update_remain_failed
        """

        self.expect_str = """
[INFO] delete I3AQ2G in remain successfully.
failed to update remain issues, please check whether the issue exist in cve and bugfix part.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('add_issue_info.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r, mock_r, resp, resp, RequestException])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id=I3AQ2G"]
        self.assert_result()

    def test_delete_multiple_cve(self):
        """
        test delete multiple cve
        """

        self.expect_str = """
[INFO] delete I3V9IG,I3AQ2G in cve successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_multiple_cve_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=cve", "--token=example", "--id", "I3V9IG",
                               "I3AQ2G"]
        self.assert_result()

    def test_delete_multiple_bugfix(self):
        """
        test delete multiple bugfix
        """

        self.expect_str = """
[INFO] delete I3J655,I3AHLY in bugfix successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_multiple_bugfix_success.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, resp, mock_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=bugfix", "--token=example", "--id", "I3J655",
                               "I3AHLY"]
        self.assert_result()

    def test_delete_multiple_remain(self):
        """
        test delete multiple remain
        """

        self.expect_str = """
[INFO] delete I3SZRJ,I3OC6A in remain successfully.
update remain issues successfully.
        """
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_r = self.make_need_content('delete_multiple_remain_success.txt', MOCK_DATA_FILE)
        mock_final_1_r = self.make_need_content('delete_multiple_update_remain_success.txt', MOCK_DATA_FILE)
        mock_final_2_r = self.make_need_content('delete_multiple_update_remain_success2.txt', MOCK_DATA_FILE)
        mock_issue_1_r = self.make_need_content('mock_remain_issue_1_data.txt', MOCK_DATA_FILE)
        mock_issue_2_r = self.make_need_content('mock_remain_issue_2_data.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, mock_r, mock_r, mock_issue_1_r, mock_issue_1_r, mock_final_1_r, mock_r,
                         mock_issue_2_r, mock_issue_2_r, mock_final_2_r])
        self.command_params = ["I40769", "--giteeid=Mary", "--delete=remain", "--token=example", "--id", "I3SZRJ",
                               "I3OC6A"]
        self.assert_result()

    def test_old_body_is_none(self):
        """
        test old body is none
        """
        self.expect_str = """
[ERROR] failed to add I3AQ2G in cve.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_issue_body_is_none_r = self.make_need_content('mock_issue_is_none.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, resp, mock_issue_body_is_none_r])
        self.assert_result()

    def test_issue_body_is_none(self):
        """
        test issue body is none
        """
        self.expect_str = """
[ERROR] failed to add I3AQ2G in cve.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        self.mock_request(side_effect=[resp, resp, resp, RequestException])
        self.assert_result()

    def test_cve_basescore(self):
        """
        test cve basescore
        """
        self.expect_str = """
[INFO] add I3AQ2G in cve successfully.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_cve_basescore_r = self.make_need_content('mock_issue_basescore.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_cve_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, mock_cve_basescore_r, mock_cve_basescore_r, mock_final_r, mock_final_r])
        self.assert_result()

    def test_cve_no_score(self):
        """
        test cve no score
        """
        self.expect_str = """
[INFO] add I3AQ2G in cve successfully.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_cve_no_core_r = self.make_need_content('mock_issue_no_score.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_cve_no_score.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, mock_cve_no_core_r, mock_cve_no_core_r, mock_final_r, mock_final_r])
        self.assert_result()

    def test_cve_abi_yes(self):
        """
        test cve abi yes
        """
        self.expect_str = """
[INFO] add I3AQ2G in cve successfully.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_cve_abi_r = self.make_need_content('mock_issue_abi.txt', MOCK_DATA_FILE)
        mock_final_r = self.make_need_content('add_cve_abi_success.txt', MOCK_DATA_FILE)
        self.mock_request(
            side_effect=[resp, resp, resp, mock_cve_abi_r, mock_cve_abi_r, mock_final_r, mock_final_r])
        self.assert_result()

    def test_verify_start_update_failed(self):
        """
        test verify start update failed
        """
        self.expect_str = """
[ERROR] not allowed operation, please start release issue first.
        """
        self.command_params = ["I40769", "--giteeid=Mary", "--add=cve", "--token=example", "--id=I3AQ2G"]
        resp = self.make_expect_data(200, 'modifypart.txt')
        mock_verify_start_update_data = self.make_need_content('verify_start_update_failed.txt', MOCK_DATA_FILE)
        self.mock_request(side_effect=[resp, mock_verify_start_update_data])
        self.assert_result()
