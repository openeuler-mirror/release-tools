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
Description: conver multiple gitee restful APIs to python methods
Class:
"""

import json
import re
import time
import requests
from requests.exceptions import RequestException

from javcra.application.checkpart.check_requires import init_env
from javcra.application.checkpart.check_requires.dnf_api import DnfApi
from javcra.application.checkpart.check_requires.shell_api_tool import ShellCmdApi
from javcra.common.constant import BRANCH_LIST, LTS_BRANCH, REPO_EP_NAME, REPO_STA_NAME, EPOL_SRC_NAME
from javcra.libs.log import logger


class Issue:
    """cover gitee APIs to python methods"""

    def __init__(self, repo, token, issue_num):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW 64; rv:50.0) "
                          "Gecko/20100101 Firefox/50.0"
        }
        self.repo = repo
        self.owner = "src-openeuler"
        self.token = token
        self.issue_num = issue_num
        self.date = time.strftime("%Y%m%d", time.localtime())

    def __generate_request_params(self, **kwargs):
        """

        generate request parameters

        Returns:
            dict: requests params
        """
        params = {"repo": self.repo, "access_token": self.token}
        params.update(**kwargs)
        return params

    def gitee_api_request(self, method, url, data=None, params=None, retry=3):
        """
        requesting gitee api

        Args:
            method : http request method
            url : request url
            params : request params
            data: request data
            retry: retry count

        Returns:
            resp: response of request
        """
        if not params:
            params = {}
        success_code = {201, 200}

        try:
            resp = requests.request(method.lower(), url, params=params, data=data, headers=self.headers)

            retry_count = 0
            while resp.status_code == 408 and retry_count < retry:
                logger.error("api request timed out, retrying %s." % retry_count)
                resp = requests.request(method.lower(), url, params=params, data=data, headers=self.headers)
                retry_count += 1

            if resp.status_code not in success_code:
                logger.error("api request failed, url: %s, response: %s." % (url, resp.text))
                return None
        except RequestException as e:
            logger.error("RequestException occurred. %s" % e)
            return None
        return resp

    def __get_gitee_api_url(self, url_name, **kwargs):
        """
        get specific gitee api url

        Args:
            url_name(string) : url name
            kwargs(dict): params to get url

        Returns:
            gitee api url
        """

        url_prefix = "https://gitee.com/api/v5/"

        url_dict = {
            "pkg_issues_url": url_prefix + "repos/{owner}/{repo}/issues?access_token={access_token}&state=all"
                .format(owner=self.owner, repo=kwargs.get("pkg"), access_token=self.token),

            "issue_url": url_prefix + "enterprises/{enterprise}/issues/{number}?access_token={token}".format(
                enterprise=kwargs.get("owner"), number=kwargs.get("issue_id"), token=self.token),

            "create_issue_url": url_prefix + "repos/{owner}/issues".format(owner=kwargs.get("owner")),

            "update_issue_url": url_prefix + "repos/{owner}/issues/{number}".format(owner=kwargs.get("owner"),
                                                                                    number=self.issue_num),

            "create_comment_url": url_prefix + "repos/{owner}/{repo}/issues/{number}/comments".format(
                owner=kwargs.get("owner"), repo=self.repo, number=self.issue_num),

            "get_issue_comments": url_prefix + "repos/{owner}/{repo}/issues/{number}/comments?access_token={token}"
                                               "&page=1&per_page=100&order=asc".format(
                owner=kwargs.get("owner"), repo=kwargs.get("repo"), number=kwargs.get("issue_id"), token=self.token),

            "update_issue_status": url_prefix + "repos/{owner}/issues/{number}".format(owner=kwargs.get("owner"),
                                                                                       number=kwargs.get("issue_id")),

            "creat_issue_label_url": url_prefix + "repos/{owner}/{repo}/issues/{number}/labels?access_token={token}"
                                                  "".format(owner=kwargs.get("owner"), repo=kwargs.get("repo"),
                                                            number=kwargs.get("issue_id"), token=self.token)
        }

        return url_dict.get(url_name)

    def __get_pkg_issues(self, pkg):
        """
        list all open issues of pkg
        Args:
            pkg: package name

        Returns:
            issue list of specific pkg repository
        """
        issue_url = self.__get_gitee_api_url("pkg_issues_url", pkg=pkg)
        resp = self.gitee_api_request("get", issue_url)
        if resp:
            issues = json.loads(resp.text)
            return issues
        else:
            logger.error("failed to get the issue info of pkg %s." % pkg)
        return []

    def get_issue_info(self, issue_number, owner="open_euler"):
        """
        get info of specified issue in enterprise repository

        Args:
            issue_number: issue id
            owner: enterprise repository

        Returns:

        """
        issue_url = self.__get_gitee_api_url("issue_url", owner=owner, issue_id=issue_number)
        resp = self.gitee_api_request("get", issue_url)
        if resp:
            return json.loads(resp.text)

        logger.error("failed to get the issue info of %s. " % issue_number)
        return None

    def _issue_state(self, data, issue_title, created_issue_id):
        """
        Determine whether to update the status of the issue
        Args:
            data: data
            issue_title: issue_title
            created_issue_id:created_issue_id

        Returns:

        """

        def judge_false_positive(issue_comments_resp):
            """
            Determine if the false positive is in the comment
            Args:
                issue_comments_resp: issue_comments_resp

            Returns:
                True: exists
                False: not in
            """
            for comment in issue_comments_resp:
                if "误报" in comment.get("body"):
                    return True
            return False

        kwargs = {"owner": "src-openeuler", "repo": data.get("repo"), "issue_id": created_issue_id}
        issue_comments_url = self.__get_gitee_api_url(
            "get_issue_comments", **kwargs
        )
        issue_comments = self.gitee_api_request("get", url=issue_comments_url)
        if not issue_comments:
            logger.error("failed to get the comment of the issue, the route is %s" % issue_comments_url)
            return created_issue_id
        try:
            issue_comments_resp = json.loads(issue_comments.text)
        except json.JSONDecodeError as error:
            logger.error("failed to parse json data, the reason for the error is %s" % error)
            return created_issue_id
        # determine whether the false positive is in the comment information
        if judge_false_positive(issue_comments_resp):
            logger.info("An issue with the same content already exists,"
                        "a false positive was detected in the comment area,"
                        "and the issue number is %s" % created_issue_id)
        else:
            logger.info(
                "There is an issue with the same content, no false positives are detected in "
                "the comment area, the status is updated to agent, the issue number is %s"
                % created_issue_id)
            update_issue_status_url = self.__get_gitee_api_url("update_issue_status", **kwargs)
            update_res = self.gitee_api_request("patch", url=update_issue_status_url,
                                                data={"access_token": self.token, "repo": data.get("repo"),
                                                      "state": "open"})
            if not update_res:
                logger.error("failed to update the issue: %s" % issue_title)
        return created_issue_id

    def create_issue(self, data):
        """
        create issue in gitee
        Args:
            data: data to create issue

        Returns:
            created_issue_id
        """
        # get all the open state issue's title
        exist_issues = self.__get_pkg_issues(data.get("repo"))
        exist_issue_title_dict = dict()
        for issue in exist_issues:
            issue_id = issue.get("number")
            issue_title = issue.get("title")
            exist_issue_title_dict[issue_id] = issue_title

        issue_title = data.get("title")

        # If an issue with the same title already exists,
        # and there is no false positive in the comment information,
        # change the status of the issue to open.
        # If there is a false positive in the comment, it will not be processed,
        # and the issue id will be returned.
        if issue_title in exist_issue_title_dict.values():
            for created_issue_id, title in exist_issue_title_dict.items():
                if title == issue_title:
                    return self._issue_state(data, issue_title, created_issue_id)
        else:
            prj_issue_url = self.__get_gitee_api_url("create_issue_url", owner=data["owner"])
            post_res = self.gitee_api_request("post", prj_issue_url, data=data)
            if not post_res:
                logger.error("failed to create the issue: {}".format(issue_title))
                return None

            resp_content = json.loads(post_res.text)
            created_issue_id = resp_content["number"]
            logger.info("an issue with %s id has been created" % created_issue_id)
            return created_issue_id

    def update_issue(self, owner="openEuler", **kwargs):
        """
        call the gitee api to update the issue for release issue

        Returns:
            update issue result
        """
        data = self.__generate_request_params(**kwargs)
        update_issue_url = self.__get_gitee_api_url("update_issue_url", owner=owner)

        return self.gitee_api_request(
            "patch",
            url=update_issue_url,
            data=data
        )

    def create_issue_comment(self, comment):
        """
        method to create issue comment for release issue

        Args:
            comment (str): comment str
        """
        url = self.__get_gitee_api_url("create_comment_url", owner="openeuler")
        data = {"body": comment, "access_token": self.token}
        resp = self.gitee_api_request("post", url=url, data=data)
        return resp

    def get_update_issue_branch(self):
        """
        get branch from issue title for making update repo

        Returns:
            update issue branch

        """
        branch = None
        issue_content = self.get_issue_info(self.issue_num)
        try:
            if issue_content:
                title = issue_content["title"]

                # verify weather the title is correct, title demo: openxxxx-20.03-LTS-SP1 Update 2021/4/23 release
                title_content = title.strip().split()
                if len(title_content) != 4:
                    logger.error("incorrect title, please check. Title: %s" % title)
                    return None
                branch = title.strip().split()[0]
                if branch not in BRANCH_LIST:
                    logger.error("branch %s not in qualified branch_list: %s" % (branch, BRANCH_LIST))
                    return None
        except IndexError:
            logger.error("failed to get update issue branch.")
        return branch

    def get_issue_body(self, issue_id):
        """
        get issue body content for release issue

        Returns:
            str: issue body str
        """
        issue_content = self.get_issue_info(issue_id)
        if not issue_content:
            logger.error("can not get issue content for %s ,please check!" % issue_id)
            return None
        body = issue_content.get("body", "")
        if not body:
            logger.error(" %s empty issue body,please check." % issue_id)
        return body

    @staticmethod
    def __process_body_for_pkglist(body, block_name):
        """
        process the md string of cve bugfix requires for pkg_list

        Args:
            body: block body
            block_name: given [cve,bugfix,req]

        Returns:
            current pkgs in block
        """
        # using regular to match the specific issue content in the table
        content = re.compile("\|\-\|\\n(?P<content>.*)", re.S).search(body)
        if not content:
            content = ""
        else:
            content = content["content"]

        repos = set()
        # If the part is cve or bugfix, then the second column is pkgname
        pkgname_index_dict = {"cve": 2, "bugfix": 2, "req": 1}

        for line in content.splitlines():
            if not line:
                continue
            try:
                repo_idx = pkgname_index_dict.get(block_name)
                repo_info = line.split("|")[repo_idx]
            except IndexError:
                logger.error("can not get pkg info in {} block".format(block_name))
            else:
                repos.add(repo_info)
        return repos

    def __get_pkglist_from_specific_part(self, block_res, block_name, pkg_set):
        """
        get pkglist from cve part、bugfix part、requires part

        Args:
            block_res: cve part res、bugfix part res、requires part res
            block_name: cve、bugfix、requires
            pkg_set: set of pkglist

        Returns:
            pkg_set
        """
        # If exists specific part, then get packages
        if block_res:
            pkg_set.update(self.__process_body_for_pkglist(block_res[block_name], block_name=block_name))
        else:
            logger.warning("not found %s content when getting pkglist from specific part." % block_name)
        return pkg_set

    def get_update_list(self):
        """
        use regular to get pkglist

        Args:
            issue_body: issue body str

        Returns:
            list: pkg list
        """
        issue_body = self.get_issue_body(self.issue_num)

        if issue_body:
            pkgs = set()

            # using regular to get the contents of the specified part
            cve_res = re.compile("(?P<cve>1、CVE.*?\\n\\n)", re.S).search(issue_body)
            bugfix_res = re.compile("(?P<bugfix>2、bugfix.*?\\n\\n)", re.S).search(issue_body)
            req_res = re.compile("(?P<req>3、requires.*?\\n\\n)", re.S).search(issue_body)

            # get packages from cve、bugfix、requires table
            cve_pkgs = self.__get_pkglist_from_specific_part(cve_res, "cve", pkgs)
            cve_bugfix_pkgs = self.__get_pkglist_from_specific_part(bugfix_res, "bugfix", cve_pkgs)
            cve_bugfix_req_pkgs = self.__get_pkglist_from_specific_part(req_res, "req", cve_bugfix_pkgs)

            return list(cve_bugfix_req_pkgs)
        else:
            logger.error("empty content of issue body, can not get update list.")
            return []

    @staticmethod
    def get_standard_epol_list(branch, pkg_list):
        """get standard epol list

        Args:
            branch: branch name
            pkg_list: package list from release issue
        Returns:
            pkglist_standard: standard pkg list
            pkglist_epol: epol pkg list
        """

        def shell_cmd(basis_cmd, repo_file_condition, repo_conditions):
            """
            execute shell cmd
            """
            basis_cmd.extend(repo_file_condition)
            basis_cmd.extend(repo_conditions)
            # package info str
            output = ShellCmdApi.call_subprocess(basis_cmd)
            if not output:
                return False
            for repo_condition in repo_conditions:
                # whether the repo in package info str
                if repo_condition in output:
                    return True
            return False

        if branch not in BRANCH_LIST:
            raise ValueError("not supporting branch: %s, which not in %s." % (branch, BRANCH_LIST))

        if branch == LTS_BRANCH:
            repo_epol = EPOL_SRC_NAME
        else:
            repo_epol = REPO_EP_NAME
        repo_standard = REPO_STA_NAME

        # get repo according to the branch
        repofile = init_env.get_yum_repo_file(branch)

        # repo file condition like ["-c", "repo file path"]
        repo_file_condition = DnfApi.generate_repo_file_condition(repofile)

        # generate repo cmd like ["--repo", "repo_name"]
        standard_repo_condition = DnfApi.generate_repo_condition(repo_standard)
        epol_repo_condition = DnfApi.generate_repo_condition(repo_epol)

        pkglist_standard = []
        pkglist_epol = []
        for pkg in pkg_list:
            basis_cmd = ["dnf", "info", pkg]
            # use "dnf" to query package info of specific repo
            if shell_cmd(basis_cmd, repo_file_condition, standard_repo_condition):
                pkglist_standard.append(pkg)
            elif shell_cmd(basis_cmd, repo_file_condition, epol_repo_condition):
                pkglist_epol.append(pkg)
        return pkglist_standard, pkglist_epol

    def get_issue_comments(self, params):
        """
        get comments according to params

        Args:
            params: comment params
        Returns:
            comment_list: comment list in release issue
        """
        issue_comments_url = self.__get_gitee_api_url(
            "get_issue_comments", **params
        )
        issue_comments = self.gitee_api_request("get", url=issue_comments_url)
        if not issue_comments:
            logger.error("failed to get the comment of the issue, the route is %s" % issue_comments_url)
            return []
        try:
            comment_list = []
            issue_comments_resp = json.loads(issue_comments.text)
            for comment_dict in issue_comments_resp:
                if comment_dict.get("body"):
                    comment_list.append(comment_dict.get("body").strip())
            return comment_list

        except json.JSONDecodeError as error:
            logger.error("failed to parse json data %s" % error)
            return []

    def judge_specific_comment_exists(self, comment_list, issue_params):
        """
        judge whether the specific comment exists

        Args:
            comment_list: comment list in release issue
            issue_params: params for issue

        Returns:
            True or False
        """
        issue_comments = self.get_issue_comments(issue_params)
        if not issue_comments:
            return False

        lower_comment_list = [comment.lower() for comment in issue_comments]
        for comment in comment_list:
            if comment not in lower_comment_list:
                logger.info("%s not in issue comments." % comment)
                return False

        return True

    def create_issue_label(self, label_list, params):
        """
        create label for release issue

        Args:
            label_list: labels to create
            params: params for issue

        Returns:
            True or False
        """
        create_label_url = self.__get_gitee_api_url("creat_issue_label_url", **params)
        json_data = json.dumps(label_list)
        resp = self.gitee_api_request("post", url=create_label_url, data=json_data)
        return True if resp else False

