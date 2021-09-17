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
from javcra.application.modifypart.modifyentrance import IssueOperation
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
