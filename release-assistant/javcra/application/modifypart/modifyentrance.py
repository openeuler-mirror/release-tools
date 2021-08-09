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


class Operation(Issue):
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

    def add_for_specific_block(self, body_str, issues, table_head, block_name):
        """
        add info in specific block

        Args:
            body_str: str, issue body
            issues: issues to be add
            table_head: list, table head
            block_name: block name

        Returns:
            processed issue body str
        """

        if not body_str:
            raise ValueError("no content of release issue body, failed to add.")

        issues_dict = dict()
        issues_info_list = list()

        # If the block is "requires", then get the md format str directly, like "|bluez|接口变更|"
        if "requires" in block_name:
            requires_md_str = self.convert_md_table_format(table_head, issues)
            if requires_md_str:
                issues_info_list.append(requires_md_str)
                issues_dict = {"requires_str": requires_md_str}
        else:
            # for other blocks, get detail issue info according to each issue id, then get the md format str
            # like "|#I41R53:CVE-2021-36222|krb5|已完成|7.5|1.18.2|否|"
            for issue_id in issues:
                single_issue_info = self.get_single_issue_info(issue_id, block_name)
                if single_issue_info:
                    issues_info_list.append(single_issue_info)
                    issue_info = self.convert_md_table_format(table_head, single_issue_info)
                    issues_dict.setdefault(issue_id, issue_info)

        # if all the info to be add are empty
        if not issues_info_list:
            raise ValueError("failed to add, please check whether the issues to be added exists.")

        return self.get_new_body_lines(
            body_str, append_info=issues_dict, start_flag=block_name, end_flag="\n"
        )

    def delete_for_specific_block(self, body_str, issues, block_name):
        """
        delete info in specific block

        Args:
            body_str: str, issue body
            issues: issues to be delete
            block_name:block name

        Returns:
            processed issue body str
        """
        if not body_str:
            raise ValueError("no content of release issue body, failed to delete.")

        res_str = body_str
        # delete each issue and then get new issue body lines
        for issue_id in issues:
            res_str = self.get_new_body_lines(
                res_str, delete_issue=issue_id, start_flag=block_name, end_flag="\n"
            )
        return res_str

    @staticmethod
    def __get_score(body_str):
        """
        get the score of cve

        Args:
            body_str: cve issue body str

        Returns:
            str: score value or no score
        """
        # to match openEuler评分 for cve
        euler_score_pattern = re.compile("openEuler评分.*?(?P<euler_score>[0-9\.]+)", flags=re.S)
        euler_res = euler_score_pattern.search(body_str)

        if euler_res:
            return euler_res["euler_score"]
        else:
            # to match BaseScore for cve
            base_score_pattern = re.compile("BaseScore[：:](?P<base_score>[0-9\.]+)")
            base_score = base_score_pattern.search(body_str)
            return base_score["base_score"] if base_score else "no score info"

    def __is_abi_change(self, body_str):
        """
        Parsing whether the abi has changed

        Args:
            body_str: cve issue body

        Returns:
            "是" or "否"
        """
        # to match whether the abi has changed of specific branch
        abi_content_pattern = re.compile("修复是否涉及abi变化.*?(?P<abi>.*)[\\n$]", flags=re.S)
        abi_res = abi_content_pattern.search(body_str)

        if not abi_res:
            logger.error("The abi pattern did not match the info")
            return "否"

        abi_info = abi_res["abi"]
        branch = self.get_update_issue_branch()
        if not branch:
            return "否"

        for line in abi_info.splitlines():
            if branch in line and "是" in line:
                return "是"
        return "否"

    def get_single_issue_info(self, issue_id, block_name):
        """
        get singe issue info for specific block

        Args:
            block_name: name of block
            issue_id: issue id

        Returns:
            list: issue info list
        """
        issue_content = self.get_issue_info(issue_number=issue_id)
        if not issue_content:
            logger.error("can not get the content of issue {}, perhaps this issue does not exist.".format(issue_id))
            return []

        repository = issue_content.get("repository", {})
        # for all the block, get the dict of repository and status for the issue
        issue_info = {
            "仓库": repository.get("name", "无仓库信息"),
            "status": issue_content.get("issue_state", "无状态信息")
        }

        block_names_list = ["## 2、bugfix", "# 3、安装、自编译问题", "# 4、遗留问题"]
        if block_name in block_names_list:
            issue_info["issue"] = "#" + issue_id

        if "遗留" in block_name:
            issue_info["type"] = issue_content.get("issue_type", "无type信息")
            issue_info["status"] = "遗留"

        elif "CVE" in block_name:
            issue_body = self.get_issue_body(issue_id)
            if not issue_body:
                logger.error("empty issue body for {}, can not get the info for {} block.".format(issue_id, block_name))
                return []

            version_pattern = re.compile("漏洞归属的版本[：:](?P<version>.*)")
            version = version_pattern.search(issue_body)
            issue_info["CVE"] = "#" + issue_id
            issue_info["score"] = self.__get_score(issue_body)
            issue_info["version"] = version["version"] if version else "no version info"
            issue_info["abi是否变化"] = self.__is_abi_change(issue_body)

        return [issue_info]

    def operate_for_specific_block(self, table_head, block_name, table_body=None, prefix="", operate="init",
                                   body_str=None, issues=None):
        """
        Process init, add, delete operations for specific block

        Args:
            table_head: list, table head
            block_name: str, block name like ""## 1、CVE""
            table_body: table_body of specific part for init, like [{..},{..},..].
            prefix: prefix of block, like "修复了bugfix xxx个"
            operate: init, add, delete
            body_str: issue body, str
            issues: issue id, list

        Raises:
            ValueError: not allowed operate

        Returns:
            processed release issue body str
        """
        if not table_body:
            table_body = []

        if operate == "init":
            return self.init_md_table(table_head, table_body, block_name, prefix)
        elif operate == "add":
            return self.add_for_specific_block(body_str, issues, table_head, block_name)
        elif operate == "delete":
            return self.delete_for_specific_block(body_str, issues, block_name)
        else:
            raise ValueError(
                "not allowed 'operate' value,expected in ['init','add','delete'],but given {}".format(operate)
            )

    def init(self):
        """
        init specific block

        Returns:
            init str
        """
        return self.get_new_issue_body(operate="init")

    def get_new_issue_body(self, operate="init", body_str=None, issues=None):
        raise NotImplementedError


class CveIssue(Operation):
    """
    operation CVE in issue
    """

    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def create_cve_list(self, user_email):
        """
        The CVE-Manager is triggered to generate the CVE list and archive it
        Args:
            user_email (str): gitee user email
        """
        # Take cve within three months
        start_time = (datetime.datetime.now() + datetime.timedelta(days=-90)).strftime('%Y-%m-%d')
        email_name = user_email.split('@')[0]
        url = "https://api.openeuler.org/cve-manager/v1/download/excel/triggerCveData?startTime=" + \
              start_time + "&typeName=" + email_name
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                logger.info("The CVE-Manager is triggered to generate the CVE list and archive the CVE list")
                return True
            logger.error("The CVE List file fails to be archived %s" % response.status_code)
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


class BugFixIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def get_new_issue_body(self, operate="init", body_str=None, issues=None):
        """
        get new issue body for bugfix block operation

        Args:
            operate: operate str. Defaults to "init".expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue id list.

        Returns:
            str: new issue body str
        """
        if not issues:
            issues = []

        table_head = ["issue", "仓库", "status"]
        block_name = "## 2、bugfix"
        bugfix_list = []
        bugfix_prefix = "修复bugfix {}个".format(len(bugfix_list))

        return self.operate_for_specific_block(
            table_head,
            block_name,
            prefix=bugfix_prefix,
            operate=operate,
            table_body=bugfix_list,
            body_str=body_str,
            issues=issues,
        )


class InstallBuildIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def get_new_issue_body(self, operate="init", body_str=None, issues=None):
        """
        get new issue body for install build block operation

        Args:
            operate: operate str. expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue id list.

        Returns:
            new issue body str
        """
        table_head = ["issue", "仓库", "status"]
        block_name = "# 3、安装、自编译问题"

        return self.operate_for_specific_block(
            table_head,
            block_name,
            operate=operate,
            body_str=body_str,
            issues=issues
        )


class RemainIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def get_new_issue_body(self, operate="init", body_str=None, issues=None):
        """
        get new issue body for remain block operation

        Args:
            operate: operate str. expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue id list.

        Returns:
            str: new issue body str
        """
        t_header = ["issue", "仓库", "status", "type"]
        block_name = "# 4、遗留问题"

        return self.operate_for_specific_block(
            t_header,
            block_name,
            operate=operate,
            body_str=body_str,
            issues=issues
        )
