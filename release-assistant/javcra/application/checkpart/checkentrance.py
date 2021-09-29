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
Description: check commands entrance
Class: CheckEntrance
"""
import json
import requests
from requests import RequestException
from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.libs.config.global_config import TEST_IP_PORT
from javcra.libs.log import logger


class CheckEntrance(IssueOperation):
    """
    class for CheckEntrance
    """

    def add_repo_in_table(self):
        """
        add repo in release issue table
        """
        start_flag = "# 2、测试repo源"
        end_flag = "\n"
        issue_body = self.get_issue_body(self.issue_num)
        if not issue_body:
            logger.error("can not get release issue body, failed to add repo in table.")
            return False

        issue_body_lines = issue_body.splitlines(keepends=True)
        try:
            repo_lines, start_idx, end_idx = self.get_block_lines(issue_body_lines, start_flag, end_flag)
            new_repo_lines = self.get_repo().splitlines(keepends=True)
            final_lines = self.modify_block_lines(issue_body_lines, new_repo_lines, start_idx, end_idx)
            body_str = "".join(final_lines)
            return True if self.update_issue(body=body_str) else False
        except ValueError as err:
            logger.error(err)
            return False

    def request_repo_url(self, repos_list):
        """
        whether the url can be accessed successfully
        args:
            repos_list: repo info list
        Returns:
            True or False
        """
        for repo_info in repos_list:
            url = repo_info.get("url")
            if not self.gitee_api_request("get", url):
                logger.error("the repo url: %s can not access." % url)
                return False
        return True

    def send_repo_info(self):
        """
        to send repo info

        Returns:
            True or False
        """
        try:
            branch = self.get_update_issue_branch()
            if not branch:
                logger.error("failed to send repo info due to the empty branch.")
                return False

            repo_list = self.get_repo(md_type=False)
            if not self.request_repo_url(repo_list):
                logger.error("failed to send repo info because cannot access repo url.")
                return False

            # branch demo: openEuler-20.03-LTS-SP1
            branch_info = branch.split("-", 1)
            pkg_list = self.get_update_list()

            if not pkg_list:
                logger.error("failed to send repo info because cannot get pkgs from release issue.")
                return False

            update_data = {
                "product": branch_info[0],
                "version": branch_info[1],
                "pkgs": pkg_list
            }

            for repo_info in repo_list:
                if repo_info.get("repo_type") == "standard":
                    update_data["base_update_url"] = repo_info.get("url")
                else:
                    update_data["epol_update_url"] = repo_info.get("url")

            url_for_test = "http://" + TEST_IP_PORT + "/api/tce/testsuite/run"
            headers = {"Content-Type": "application/json; charset=utf8"}
            resp = requests.post(url_for_test, data=json.dumps(update_data), headers=headers, timeout=3)

            if not resp or resp.status_code != 200:
                logger.error("failed to send repo info.")
                return False

            if json.loads(resp.text).get("error_code") != 200:
                logger.error("failed to send repo info. Response: %s." % json.loads(resp.text))
                return False

        except (ValueError, IndexError, RequestException, json.JSONDecodeError) as err:
            logger.error("error in sending repo info, %s" % err)
            return False
        else:
            return True
