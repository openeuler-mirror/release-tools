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


class Operation:

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

            if flag:
                if line == end_flag:
                    block_end_idx = idx
                    break

        return issue_body_lines[block_start_idx:block_end_idx], block_start_idx, block_end_idx
