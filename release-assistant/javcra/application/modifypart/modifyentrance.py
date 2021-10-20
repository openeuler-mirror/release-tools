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
import json
import re
import requests
from retrying import retry
from javcra.api.gitee_api import Issue
from javcra.common.constant import REPO_BASE_URL, RELEASE_URL
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

    @staticmethod
    def __update_info_in_specific_block(update_info, block_lines):
        """
        update info in specific block for update operation
        Args:
            update_info: issue to update
            block_lines: lines of specific block
        Returns:
            block_lines: new lines of specific block
        """
        for issue_id, issue_content in update_info.items():
            if not issue_content:
                continue
            for idx, ln in enumerate(block_lines):
                if issue_id in ln:
                    block_lines[idx] = issue_content
                    break
        return block_lines

    def get_new_body_lines(self, old_issue_info, append_info=None, delete_info=None,
                           update_info=None, start_flag="", end_flag="\n"):
        """
        generating a new issue body by add or delete or update operation

        Args:
            old_issue_info: old issue info
            append_info: issues to add. like {issue_id:{"repo":..,"status":...},...}
            delete_info: issues to delete.
            update_info: issues to update.
            start_flag: start flag of block
            end_flag: end flag of block.

        Raises:
            ValueError:
                append_info、 delete_info need at least one

        Returns:
            new body lines
        """
        if not any((append_info, delete_info, update_info)):
            raise ValueError("append_info or delete_info or update info need at least one")

        issue_body_lines = old_issue_info.splitlines(keepends=True)
        block_lines, block_start_idx, block_end_idx = self.get_block_lines(
            issue_body_lines, start_flag, end_flag)

        if append_info:
            block_lines = self.__append_info_in_specific_block(append_info, block_lines)
        elif delete_info:
            block_lines = self.__delete_issue_in_specific_block(delete_info, block_lines)
        else:
            block_lines = self.__update_info_in_specific_block(update_info, block_lines)

        final_lines = self.modify_block_lines(issue_body_lines, block_lines, block_start_idx,
                                              block_end_idx)
        return "".join(final_lines)

    def create_jenkins_comment(self, jenkins_result):
        """method to create issue comment

        Args:
            jenkins_result: jenkins result
        Returns:
            comment_res: Success and failure in creating a comment
        """
        for result in jenkins_result:
            if not result.get("status"):
                logger.error("failed to obtain jenkins_result")
                return
        th = ["name", "status", "output"]
        comment = self.init_md_table(th, jenkins_result)
        comment_res = self.create_issue_comment(comment)
        if not comment_res:
            logger.error("Failed to create Jenkins' comment message %s" % comment)
            return
        return comment_res

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
                res_str, delete_info=issue_id, start_flag=block_name, end_flag="\n"
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

    def update_for_specific_block(self, body_str, issues, table_head, block_name):
        """
        Update specific table modules
        Args:
            body_str: body info
            issues: list of issue numbers
            table_head: table head
            block_name: block name

        Returns:
            get_new_body_lines: The new issue of body
        """
        if not body_str:
            raise ValueError("no content of release issue, failed to update")
        to_update = {}
        for issue_id in issues:
            # latest issue status
            single_issue_info = self.get_single_issue_info(issue_id, block_name)
            to_update.setdefault(
                issue_id, self.convert_md_table_format(table_head, single_issue_info)
            )

        return self.get_new_body_lines(
            body_str, update_info=to_update, start_flag=block_name, end_flag="\n"
        )

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
        elif operate == "update":
            return self.update_for_specific_block(body_str, issues, table_head, block_name)
        else:
            raise ValueError(
                "not allowed 'operate' value,expected in ['init','add','delete','update'],but given {}".format(operate)
            )

    def init(self, *args):
        """
        init specific block

        Returns:
            init str
        """
        return self.get_new_issue_body(operate="init", *args)

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
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
        except (requests.RequestException, AttributeError) as error:
            logger.error("The CVE List file fails to be archived because %s " % error)
            return False

    def get_cve_list(self, *args):
        """
        Obtain cVE-related information provided by the CVE-Manager.
        Returns:
            cve_list: Data in Excel in dictionary form
        """
        user_email, obs_ak, obs_sk = args

        # trigger cve_manger to archive
        resp = self.create_cve_list(user_email)
        if not resp:
            return []

        @retry(stop_max_attempt_number=5, wait_fixed=60000)
        def get_list():
            """
            Get archived files
            Returns:
                cve_list: document content
            """
            now_time = datetime.date(
                datetime.date.today().year,
                datetime.date.today().month,
                datetime.date.today().day,
            ).strftime("%Y-%m-%d")
            branch_name = self.get_update_issue_branch()
            if not branch_name:
                logger.error("Failed to obtain branch")
                return []
            cve_list = download_file(
                now_time, "{}_updateinfo.xlsx".format(branch_name), obs_ak, obs_sk
            )
            if not cve_list:
                logger.error("Failed to obtain CVE data")
                raise ValueError("Failed to obtain CVE data")
            return cve_list

        cve_list = get_list()
        return cve_list

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
        """
        get new issue body for cve block operation

        Args:
            operate: operate str. Defaults to "init".expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue id list.

        Returns:
            new issue body str
        """
        if not issues:
            issues = []

        t_head = ["CVE", "仓库", "status", "score", "version", "abi是否变化"]
        block_name = "## 1、CVE"
        logger.info("Start to obtain cve archive information, it may take a few minutes.")
        cve_list = [] if operate != "init" else self.get_cve_list(*args)
        cve_prefix = "修复CVE {}个".format(len(cve_list))

        return self.operate_for_specific_block(t_head, block_name, prefix=cve_prefix, operate=operate,
                                               table_body=cve_list, body_str=body_str, issues=issues)


class BugFixIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
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


class RequiresIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    @staticmethod
    def get_requires_list():
        """
        get requires list

        Returns:
            requires list, like [{"仓库":..., "引入原因":...},...]
        """
        # since the code that generates pkg requires is not in the repository,
        # so it is assumed that the return value is []
        return []

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
        """
        get new issue body for requires block operation

        Args:
            operate. Defaults to "init".expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue list

        Returns:
            new issue body str
        """

        t_head = ["仓库", "引入原因"]
        block_name = "## 3、requires"

        if operate not in ["init", "add"]:
            raise ValueError("requires block operation only allowed in ['init', 'add'].")

        issues = self.get_requires_list()
        return self.operate_for_specific_block(
            t_head, block_name, operate=operate, body_str=body_str, issues=issues
        )


class InstallBuildIssue(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
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

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
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


class IssueOperation(Operation):
    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)
        args = (repo, token, issue_num)
        self.cve_object = CveIssue(*args)
        self.bugfix_object = BugFixIssue(*args)
        self.requires_object = RequiresIssue(*args)
        self.install_build_object = InstallBuildIssue(*args)
        self.remain_object = RemainIssue(*args)

    def init_repo_table(self):
        """
        init repo table

        return:
            md table str
        """
        block_name = "# 2、测试repo源"
        table_head = ["repo_type", "url"]
        table_str = self.init_md_table(table_head)
        return block_name + table_str

    def create_install_build_issue(self, failed_type, pkg_name):
        """
        create issue when install failed or build failed

        Args:
            failed_type: install failed or build failed
            pkg_name: package name

        return:
            issue_id
        """
        branch = self.get_update_issue_branch()
        if not branch:
            logger.error("failed to create install build issue because the release issue branch not found.")
            return None

        release_time = self.get_release_time()
        if not release_time:
            logger.error("failed to create install build issue because the release time not found.")
            return None

        params = {
            "repo": pkg_name,
            "owner": self.owner,
            "access_token": self.token,
            "title": "[{brh}] {pkg} {verify_type} failed {release_date}".format(pkg=pkg_name, verify_type=failed_type,
                                                                                brh=branch, release_date=release_time)
        }

        command = ""
        if failed_type == "build":
            command = "rpmbuild --rebuild"
        elif failed_type == "install":
            command = "yum install"

        params["body"] = """Branch: {brh}
                   Component: {pkg}
                   Instructions to reappear the problem : {command}
                   Expected results: successfully {_type}
                   Actual results: failed to {_type}""".format(brh=branch, pkg=pkg_name, command=command,
                                                               _type=failed_type)
        issue_id = self.create_issue(params)
        return issue_id

    def get_update_version_info(self):
        """
        Get update target and personnel information

        Returns:
            update version info
        """
        issue_body = self.get_issue_body(self.issue_num)
        if issue_body:
            if re.compile("1、CVE.*?\\n\\n", re.S).search(issue_body):
                logger.error("Issue has CVE content, maybe you already have operated start update command.")
                return None

            if "代码冻结" not in issue_body:
                logger.error("the code freeze time is not in release issue body.")
                return None

            if not issue_body.endswith("\n"):
                issue_body += "\n"
            return issue_body
        return None

    def get_release_time(self):
        """
        get the date for release
        Returns:
            release_date
        """
        issue_body = self.get_issue_body(self.issue_num)
        if not issue_body:
            logger.error("no content of release issue body.")
            return None

        date_info = re.compile("(?P<release_date>代码冻结.*?\\n\\n)", re.S).search(issue_body)
        if not date_info:
            logger.error("the code freeze time is not in release issue body.")
            return None

        split_date_info = re.split(r":|：", date_info["release_date"].strip())
        try:
            release_date = split_date_info[1].strip()
            # The length of the date including year, month, and day is 8
            if release_date.isdigit() and len(release_date) == 8:
                return release_date

            logger.error("The format of the code freeze date: %s does not meet the requirements." % release_date)
            return None

        except IndexError:
            logger.error("error in getting code freeze date.")
            return None

    def get_repo(self, md_type=True):
        """
        get repo according to branch 、date and epol
        """
        branch = self.get_update_issue_branch()
        if not branch:
            raise ValueError("can not get the branch, please check.")

        release_date = self.get_release_time()
        if not release_date:
            raise ValueError("can not get the release time, please check.")

        base_url = REPO_BASE_URL + branch
        repos = []
        repo_dict = {
            "repo_type": "standard",
            "url": base_url + "/update_" + release_date + "/"
        }
        repos.append(repo_dict)

        pkglist = self.get_update_list()
        _, epol_list = self.get_standard_epol_list(branch, pkglist)
        if epol_list:
            repo_dict = dict()
            repo_dict["repo_type"] = "epol"
            if "sp2" in branch or "SP2" in branch:
                repo_dict["url"] = base_url + "/EPOL/update_" + release_date + "/main/"
            else:
                repo_dict["url"] = base_url + "/EPOL/update_" + release_date + "/"
            repos.append(repo_dict)

        if md_type:
            t_header = ["repo_type", "url"]
            block_name = "# 2、测试repo源"
            return self.init_md_table(t_head=t_header, body_info=repos, block_title=block_name)
        return repos

    @staticmethod
    def _process_issue_id(body):
        """
        Process the MD string to get the issue ID
        Args:
            body (str): block body
        Returns:
            set: current block repos
        """
        content = re.compile("#[a-zA-Z0-9]+", re.S).findall(body)
        if not content:
            return content
        return [con.replace("#", "") for con in content]

    def _get_install_build_bugfix_issue_id(self, issue_body):
        """
        Gets the corresponding block element with regular,
        Args
            issue_body: issue body str

        Returns:
            issue number: issue number list
        """

        def update_set(res_obj):
            # Call the _process_issue_id function to return the issue number
            res_set = set()
            issue_list = self._process_issue_id(res_obj)
            res_set.update(issue_list)
            return res_set

        def update_res(issue_res, choice):
            # If this table object exists,
            # the final issue is fetched based on the selection
            issues = set()
            if issue_res:
                issues = update_set(issue_res[choice])
            return issues

        # Installs the compiled table information object
        install_build_res = re.compile("(?P<install_build>3、安装、自编译问题.*?\\n\\n)",
                                       re.S).search(issue_body)
        # Table information object for bugfix
        bugfix_res = re.compile("(?P<bugfix>2、bugfix.*?\\n\\n)", re.S).search(issue_body)

        # cve table information object
        cve_res = re.compile("(?P<cve>1、CVE.*?\\n\\n)", re.S).search(issue_body)

        install_build_issues = update_res(install_build_res, "install_build")
        bugfix_issues = update_res(bugfix_res, "bugfix")
        cve_issues = update_res(cve_res, "cve")
        if not all([install_build_issues, bugfix_issues, cve_issues]):
            logger.info("Block has no related issues  install_build_issues:%s, "
                        "bugfix_issues: %s,cve_issues: %s " % (install_build_issues, bugfix_issues, cve_issues))
        return list(install_build_issues), list(bugfix_issues), list(cve_issues)

    def update_remain_issue_state(self, issue_list, action):
        """
        Change the issue in bugfix and cve according to
        whether the command is left
        Args:
           issue_list: issues
           action: add or delete
        Returns:
            True or False
        """
        try:
            if action not in ["add", "delete"]:
                raise ValueError("action parameter errors must be in add and delete")
            issue_body = self.get_issue_body(self.issue_num)
            if not issue_body:
                raise ValueError("failed to obtain the issue description")
            _, bugfix_issues, cve_issue = self._get_install_build_bugfix_issue_id(issue_body)
            to_update = {}
            not_exist_issues = []
            for issue in issue_list:
                if issue not in bugfix_issues and issue not in cve_issue:
                    not_exist_issues.append(issue)
                    logger.warning("issue %s not exist in cve and bugfix part" % issue)
                    continue
                if issue in bugfix_issues:
                    t_head = ["issue", "仓库", "status"]
                    operate_ins = getattr(self, "bugfix" + "_object")
                    block_name = '## 2、bugfix'
                    new_con = operate_ins.get_single_issue_info(issue, block_name)[0]
                else:
                    t_head = ["CVE", "仓库", "status", "score", "version", "abi是否变化"]
                    operate_ins = getattr(self, "cve" + "_object")
                    block_name = '## 1、CVE'
                    new_con = operate_ins.get_single_issue_info(issue, block_name)[0]
                if action == "add":
                    new_con["status"] = "遗留"
                to_update.setdefault(
                    issue, self.convert_md_table_format(t_head, [new_con])
                )
                body_str = self.get_new_body_lines(
                    issue_body, update_info=to_update, start_flag=block_name, end_flag="\n"
                )
                res = self.update_issue(body=body_str)
                if not res:
                    raise ValueError("failed to %s action issue status,issue is %s" % (action, issue))
        except (ValueError, AttributeError, IndexError, TypeError, KeyError) as error:
            logger.error("In the %s operation, the reasons for the error are as follows: %s" % (action, error))
            return False
        if issue_list == not_exist_issues:
            return False
        return True

    def get_remain_issues(self):
        """
        get issues in remain block
        Returns:
            remain issues
        """
        issue_body = self.get_issue_body(self.issue_num)
        if not issue_body:
            logger.error("empty body of release issue.")
            return []

        remain_res = re.compile("(?P<remain>4、遗留问题.*?\\n\\n)", re.S).search(issue_body)
        if not remain_res:
            logger.error("can not find remain issues label in release issue.")
            return []

        remain_issues = self._process_issue_id(remain_res["remain"])
        if not remain_issues:
            logger.info("can not find any remain issues in release issue.")
        return list(set(remain_issues))

    def get_remain_packages(self):
        """
        get packages in remain block
        Returns:
            remain package list
        """
        remain_issues = self.get_remain_issues()
        remain_pkgs = []

        for issue_number in remain_issues:
            issue_content = self.get_issue_info(issue_number=issue_number)
            if not issue_content:
                logger.error("can not get the content of issue %s, perhaps this issue not exist." % issue_number)
                continue

            repository = issue_content.get("repository", {})
            if repository.get("name"):
                remain_pkgs.append(repository.get("name"))

        return list(set(remain_pkgs))

    def check_issue_state(self):
        """
        Check the issue status under the bugfix and install_build headers
        Returns:
            True: update the status of the issue to the latest status successfully
            False: failed to update the status of the issue to the latest status
        """
        try:
            body = self.get_issue_body(self.issue_num)
            if not body:
                raise ValueError("failed to get issue description information")
            # get the bugfix and the issue number under the install_build and cve table headers
            install_build_issues, bugfix_issues, _ = self._get_install_build_bugfix_issue_id(body)
            remain_issues = self.get_remain_issues()
            if install_build_issues:
                install_build_issues = [issue for issue in install_build_issues if issue not in remain_issues]
                self.operate_release_issue(operation="update", operate_block="install_build",
                                           issues=install_build_issues)
            if bugfix_issues:
                bugfix_issues = [issue for issue in bugfix_issues if issue not in remain_issues]
                self.operate_release_issue(operation="update", operate_block="bugfix",
                                           issues=bugfix_issues)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            logger.error("failed to update the status of the issue, the specific reason is %s" % error)
            return False
        return True

    def init_issue_description(self, *args):
        """
        initialize the release issue body when commenting "start-update" command

        Returns:
            True or False
        """
        update_info = self.get_update_version_info()
        if not update_info:
            return False

        release_range = "# 1、发布范围\n"
        cve_block_str = self.cve_object.init(*args)
        bugfix_block_str = self.bugfix_object.init()
        requires_block_str = self.requires_object.init()
        repo_block_str = self.init_repo_table()
        install_build_block_str = self.install_build_object.init()
        remain_block_str = self.remain_object.init()

        body_str = (
                update_info
                + release_range
                + cve_block_str
                + bugfix_block_str
                + requires_block_str
                + repo_block_str
                + install_build_block_str
                + remain_block_str
        )

        return True if self.update_issue(body=body_str) else False

    def get_new_issue_body(self, *args, operate="init", body_str=None, issues=None):
        """
        get new issue body for specific operation

        Args:
            operate: operate str. Defaults to "init".expected [init,add,delete]
            body_str: gitee issue body str.
            issues: issue id list.

        Returns:
            new issue body str
        """
        old_body_str = self.get_issue_body(self.issue_num)
        if not old_body_str:
            logger.error("The current issue has no content, please start first.")
            return False

        update_block = args[0]
        # get the block object, like cve block object, and then call
        # "get_new_issue_body" for this block
        operate_object = getattr(self, update_block + "_object")
        body_str = operate_object.get_new_issue_body(
            operate=operate, body_str=old_body_str, issues=issues)
        return body_str

    def update_issue_description(self, operate, update_block, issues=None):
        """
        to update issue description

        Args:
            operate: operate in {add,delete}.
            update_block: block name, like cve or bugfix,
            issues: issue list.

        returns:
                True or False
        """
        if not issues:
            issues = []

        old_body_str = self.get_issue_body(self.issue_num)
        if not old_body_str:
            logger.error(
                "The current issue has no content, please start first.")
            return False

        body_str = self.get_new_issue_body(update_block, operate=operate, issues=issues)

        if not body_str:
            logger.error(
                "after update issue description, got empty new release issue body.")
            return False

        return True if self.update_issue(body=body_str) else False

    def count_issue_status(self):
        """
        statistics of the status of all issues
        Returns:
            true: the status of all issue is completed
            false: there is an unfinished issue
        """
        try:
            body = self.get_issue_body(self.issue_num)
            # obtain the issue number under installation, compilation and bugfix
            install_build_issues, bugfix_issues, _ = self._get_install_build_bugfix_issue_id(body)
            issues = install_build_issues + bugfix_issues
            unfinished_issues = []
            if not issues:
                logger.info("no issue in install_build and bugfix block.")
                return True

            # traverse all issues, get the status of the issue,
            # and add the unfinished ones to the unfinished list
            for issue_number in issues:
                issue_content = self.get_issue_info(issue_number)
                if not issue_content:
                    logger.error("failed to get the issue info of %s. " % issue_number)
                    continue
                if issue_content.get("issue_state") != "已完成":
                    unfinished_issues.append(issue_number)
            if unfinished_issues:
                logger.info("The following issue status is not complete %s" % ",".join(unfinished_issues))
                return False
        except (ValueError, TypeError) as error:
            logger.error("an error occurred while counting the status of the issue. "
                         "The error is %s" % error)
            return False
        return True

    @staticmethod
    def release_announcement(user_name, password):
        """
        release announcement
        Args:
            user_name: user name
            password: password

        Returns:
            return true on success, false on failure
        """
        try:
            response = requests.post(RELEASE_URL, data={"username": user_name,
                                                        "password": password})
            if response.status_code == 200:
                if "successfully" in json.loads(response.text):
                    logger.info("release announcement successfully")
                    return True
                logger.error(response.text)
                return False
            logger.error("failed to request the announcement address: %s ,"
                         "because of the response status code is %s "
                         "response body is %s " % (RELEASE_URL, response.status_code, response.text))
            return False
        except (requests.RequestException, AttributeError, json.JSONDecodeError) as error:
            logger.error("failed to request the announcement address: %s ,"
                         "because of %s" % (RELEASE_URL, error))
            return False

    def operate_release_issue(self, *args, operation="init", operate_block=None, issues=None):
        """
        modify entrance of the release issue

        Args:
            operation: {init,add,delete}
            operate_block: block to operate
                           when the operation is "init", operate_block=None
            issues: issue list

        Returns:
            True or False
        """
        try:
            if operation == "init":
                return self.init_issue_description(*args)
            else:
                return self.update_issue_description(
                    operate=operation, update_block=operate_block, issues=issues
                )
        except ValueError as e:
            logger.error(e)
            return False
