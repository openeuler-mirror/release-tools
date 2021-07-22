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

    def gitee_api_request(self, method, url, params=None, retry=3):
        """
        requesting gitee api

        Args:
            method : http request method
            url : request url
            params : request params
            retry: retry count

        Returns:
            resp: response of request
        """
        if not params:
            params = {}
        success_code = {201, 200}

        try:
            resp = requests.request(method.lower(), url, params=params, headers=self.headers)

            retry_count = 0
            while resp.status_code == 408 and retry_count < retry:
                logger.error("api request timed out, retrying %s.", retry_count)
                resp = requests.request(method.lower(), url, params=params, headers=self.headers)
                retry_count += 1

            if resp.status_code not in success_code:
                return None
        except RequestException as e:
            logger.error("RequestException occurred. %s" % e)
            return None
        return resp

    def __get_gitee_api_url(self, url_name, **kwargs):

        url_prefix = "https://gitee.com/api/v5/"

        url_dict = {
            "pkg_issues_url": url_prefix + "repos/{owner}/{repo}/issues?access_token={access_token}&state=open"
                .format(owner=self.owner, repo=kwargs.get("pkg"), access_token=self.token),

            "issue_url": url_prefix + "enterprises/{enterprise}/issues/{number}?access_token={token}".format(
                enterprise=kwargs.get("owner"), number=kwargs.get("issue_id"), token=self.token),

            "create_issue_url": url_prefix + "repos/{owner}/issues".format(owner=kwargs.get("owner")),

            "update_issue_url": url_prefix + "repos/{owner}/issues/{number}".format(owner=self.owner,
                                                                                    number=self.issue_num),

            "create_comment_url": url_prefix + "repos/{owner}/{repo}/issues/{number}/comments".format(
                owner=self.owner, repo=self.repo, number=self.issue_num)
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

    def create_issue(self, params):
        """
        create issue in gitee
        Args:
            params: parameters to create issue

        Returns:
            created_issue_id
        """
        # get all the open state issue's title
        exist_issues = self.__get_pkg_issues(params.get("repo"))
        exist_issue_title_dict = dict()
        for issue in exist_issues:
            issue_id = issue.get("number")
            issue_title = issue.get("title")
            exist_issue_title_dict[issue_id] = issue_title

        issue_title = params.get("title")

        # if already exist the same title issue, then return the existed issue id
        if issue_title in exist_issue_title_dict.values():
            for created_issue_id, title in exist_issue_title_dict.items():
                if title == issue_title:
                    logger.info("already exists the issue: {}, issue number is {}.".format(
                        issue_title, created_issue_id))
                    return created_issue_id
        else:
            prj_issue_url = self.__get_gitee_api_url("create_issue_url", owner=params["owner"])
            post_res = self.gitee_api_request("post", prj_issue_url, params)
            if not post_res:
                logger.error("failed to create the issue: {}".format(issue_title))
                return None

            resp_content = json.loads(post_res.text)
            created_issue_id = resp_content["number"]
            return created_issue_id

    def update_issue(self, **kwargs):
        """
        call the gitee api to update the issue for release issue

        Returns:
            update issue result
        """
        params = self.__generate_request_params(**kwargs)
        update_issue_url = self.__get_gitee_api_url("update_issue_url")

        return self.gitee_api_request(
            "patch",
            url=update_issue_url,
            params=params
        )

    def create_issue_comment(self, comment):
        """
        method to create issue comment for release issue

        Args:
            comment (str): comment str
        """
        url = self.__get_gitee_api_url("create_comment_url")
        params = {"body": comment, "access_token": self.token}
        resp = self.gitee_api_request("post", url=url, params=params)
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
            logger.warning("not found %s content when getting pkglist from specific part.", block_name)
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

    def parsing_body(self):
        """
        Unable to get the issue description information
        Returns:
            personnel_authority: A dictionary of personnel information
        """
        body = self.get_issue_body(self.issue_num)
        if not body:
            logger.error("The description information of issue is not obtained")
            return {}
        personnel_access = {}
        try:
            for con in body.split("\n"):
                colon = "：" if "：" in con else ":"
                if "版本经理{colon}".format(colon=colon) in con:
                    personnel_access["version_manager"] = con.split(colon)[1]
                elif "安全委员会{colon}".format(colon=colon) in con:
                    personnel_access["security_committee"] = con.split(colon)[1]
                elif "开发人员{colon}".format(colon=colon) in con:
                    personnel_access["developer"] = con.split(colon)[1]
                elif "测试人员{colon}".format(colon=colon) in con:
                    personnel_access["tester"] = con.split(colon)[1]
                elif "tc{colon}".format(colon=colon) in con:
                    personnel_access["tc"] = con.split(colon)[1]
                elif "release{colon}".format(colon=colon) in con:
                    personnel_access["release"] = con.split(colon)[1]
                elif "qa{colon}".format(colon=colon) in con:
                    personnel_access["qa"] = con.split(colon)[1]
            return personnel_access
        except IndexError as error:
            logger.error("Error parsing issue description information %s" % error)
            return {}

    def people_review(self):
        """
        relevant people make an issue comment
        Returns:
            True: Let the relevant person issue comment successfully
            False: Let the relevant person issue comment failed
        """
        personnel_access = self.parsing_body()
        if not personnel_access:
            logger.error("No personnel information obtained,"
                         "Please make sure that there is personnel information in the issue")
            return False
        roles = ["tc", "release", "qa", "security_committee", "version_manager"]
        names = list()
        for role in roles:
            if personnel_access.get(role):
                names.append(personnel_access.get(role))
        if not names:
            logger.error("No information of relevant personnel was obtained")
            return False
        personnels = " ".join(set([personnel for name in names for personnel in
                                   name.strip().split()])).replace("\n", "")
        res = self.create_issue_comment(personnels + "  Please review this issue")
        if not res:
            logger.error("Failed to notify relevant personnel for comment")
            return False
        logger.info("%s Relevant personnel have been informed for comment" % personnels)
        return True
