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
Description: modify entrance
"""
import datetime
import re

import requests

from javcra.api.gitee_api import Issue
from javcra.libs.log import logger
from javcra.libs.read_excel import download_file


class Operation:
    """
    md operation for release issue description
    """

    def init_md_table(self, t_head=None, body_info=None, block_title="", prefix="", suffix=""):
        """
        initialize the md table of specific part like "CVE part" for release issue

        Args:
            t_head: table head. e.g.["CVE", "仓库", "status"]
            body_info: table body
            block_title: title of block. e.g: "## 1.CVE"
            prefix: table prefix. e.g.: "修复cve xx 个"
            suffix: characters between the end of the table and the next block.

        Raises:
            ValueError: The thead must be a list or tuple

        Returns:
            str: markdown table str
        """
        if not t_head:
            t_head = []

        if not isinstance(t_head, (list, tuple)):
            raise ValueError("The thead must be a list or tuple.")

        thead_str = "|" + "|".join(t_head) + "|\n" + "|-" * len(t_head) + "|\n"
        tbody_str = self.convert_md_table_format(t_head, body_info)
        table_str = thead_str + tbody_str

        if prefix:
            table_str = prefix + "\n" + table_str
        return "\n".join([block_title, table_str, suffix])

    @staticmethod
    def convert_md_table_format(table_head, issue_info):
        """
        get markdown table body according to table_head and issue_info

        Args:
            table_head: table head like ["issue","status",...]
            issue_info: issue info like [{"issue":...,"status":...},....]

        Returns:
            markdown table str
        """
        if not issue_info:
            issue_info = []

        table_body_str = ""
        for info in issue_info:
            table_body_str += "|"
            for word in table_head:
                table_body_str += str(info.get(word)) + "|"

            table_body_str += "\n"
        return table_body_str

    @staticmethod
    def get_block_lines(issue_body_lines, start_flag, end_flag):
        """
        get block lines of specific part from issue body lines

        Args:
            issue_body_lines: the lines of issue body
            start_flag: start flag of specific part, like ""## 1、CVE""
            end_flag: end flag of specific part, like "\n"

        Returns: block_lines: lines in specific part like "cve part"
                 block_start_idx: start index of specific part
                 block_end_idx: end index of specific part

        """
        block_start_idx = 0
        block_end_idx = 0
        flag = 0

        # get block lines
        for idx, line in enumerate(issue_body_lines):
            if not flag and line.startswith(start_flag):
                # represents the start of block
                flag = 1
                block_start_idx = idx
                continue

            if flag and line == end_flag:
                block_end_idx = idx
                break

        return issue_body_lines[block_start_idx:block_end_idx], block_start_idx, block_end_idx

    @staticmethod
    def modify_block_lines(origin_lines, block_lines, block_start, block_end):
        """
        modify block lines for add or delete operation

        Args:
            origin_lines: list, issue body splitlines
            block_lines: list, block str splitlines
            block_start: start index of block
            block_end: end index of block

        Returns:
            new lines for issue body, list
        """
        # to get count and then modify str "修复CVE xxx个"
        fix_line_idx = -1
        count = 0
        for index, cur_line in enumerate(block_lines):
            # demo: 修复CVE xxx个
            if cur_line.startswith("修复"):
                fix_line_idx = index

            # demo: |#I41R53:CVE-2021-36222|krb5|
            if cur_line.startswith("|#"):
                count += 1

        if fix_line_idx != -1:
            block_lines[fix_line_idx] = re.sub(
                "\d+", str(count), block_lines[fix_line_idx]
            )

        # modify block lines
        origin_lines[block_start:block_end] = block_lines
        return origin_lines

    @staticmethod
    def __append_info_in_specific_block(append_info, block_lines):
        """
        append info in specific block for add operation

        Args:
            append_info: issue info or requires info, dict
            block_lines: lines of specific block

        Returns:
                block_lines: block lines after append
        """

        for key, value in append_info.items():
            # if the issue to be added is already in the table, then continue
            if any([key in line for line in block_lines]):
                logger.info("issue {} already exists in body content.".format(key))
                continue

            # if the requires info to be added already in the table, then not add
            value_lines = value.splitlines(keepends=True)
            append_value_lines = []
            for line in value_lines:
                if line not in block_lines:
                    append_value_lines.append(line)

            value = "".join(append_value_lines)
            block_lines.append(value)

        return block_lines

    @staticmethod
    def __delete_issue_in_specific_block(delete_issue, block_lines):
        """
        delete issue in specific block for delete operation

        Args:
            block_lines: lines of specific block
            delete_issue: issue to delete

        Returns:
            block_lines: block lines after delete
        """
        to_remove_idx = -1
        for idx, block_line in enumerate(block_lines):
            if delete_issue in block_line:
                to_remove_idx = idx
                break

        if to_remove_idx != -1:
            block_lines.pop(to_remove_idx)
        else:
            logger.info("The issue {} does not exist in release issue description."
                        "".format(delete_issue))
        return block_lines

    def get_new_body_lines(self, old_issue_body, append_info=None, delete_issue=None,
                           start_flag="", end_flag="\n"):
        """
        generating a new issue body by add and delete operation

        Args:
            old_issue_body: old issue body
            append_info: issues to add. like {issue_id:{"repo":..,"status":...},...}
            delete_issue: issues to delete.
            start_flag: start flag of block
            end_flag: end flag of block.

        Raises:
            ValueError:
                append_info、 delete_info need at least one

        Returns:
            new body lines
        """
        if not any((append_info, delete_issue)):
            raise ValueError("append_info and delete_info need at least one")

        issue_body_lines = old_issue_body.splitlines(keepends=True)
        block_lines, block_start_idx, block_end_idx = self.get_block_lines(
            issue_body_lines, start_flag, end_flag)

        if append_info:
            block_lines = self.__append_info_in_specific_block(append_info, block_lines)
        else:
            block_lines = self.__delete_issue_in_specific_block(delete_issue, block_lines)

        final_lines = self.modify_block_lines(issue_body_lines, block_lines, block_start_idx,
                                              block_end_idx)
        return "".join(final_lines)


class CveIssue(Issue, Operation):
    """
    operation cVE in issue
    """
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def create_cve_list(self, user_email):
        """
        The CVE-Manager is triggered to generate the CVE list and archive it
        Args:
            user_email (str): gitee user email
        """
        start_time = datetime.date(datetime.date.today().year, datetime.date.today().month - 3,
                                   datetime.date.today().day).strftime('%Y-%m-%d')
        email_name = user_email.split('@')[0]
        url = "https://api.openeuler.org/cve-manager/v1/download/excel/triggerCveData?startTime=" + \
              start_time + "&typeName=" + email_name
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                logger.info("The CVE-Manager is triggered to generate the CVE list and archive the cVE list")
                return True
            return False
        except requests.RequestException as error:
            logger.error("The CVE List file fails to be archived because %s " % error)
            return False

    def get_cve_list(self):
        """
        Obtain cVE-related information provided by the CVE-Manager.
        Returns:
            cve_list: Data in Excel in dictionary form
        """

        now_time = datetime.date(datetime.date.today().year, datetime.date.today().month,
                                 datetime.date.today().day).strftime('%Y-%m-%d')
        branch_name = self.get_update_issue_branch()
        if not branch_name:
            logger.error("Failed to obtain branch")
            return []
        cve_list = download_file(now_time, "{}_updateinfo.xlsx".format(branch_name))
        if not cve_list:
            logger.error("Failed to obtain CVE data")
            return []
        return cve_list

