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
Description: start commands entrance
Class: StartEntrance
"""
import json
from datetime import datetime, timedelta, timezone
from javcra.api.gitee_api import Issue
from javcra.common.constant import BRANCH_LIST, VERSION_MANAGER, DEVELOPER, SECURITY_COMMITTEE, TESTER
from javcra.libs.log import logger


class UpdateIssue(Issue):
    def __init__(self, repo, token, issue_num=None):
        super().__init__(repo, token, issue_num=issue_num)

    def create_update_issue(self, branch):
        """
        Description: create update issues automatically.
        Args:
            branch: branch name of openEuler in src-openEuler

        Returns:
            params(dict):dictionary of issue body
        """
        base_date = (datetime.now(tz=timezone.utc) + timedelta(hours=8))
        release_date = base_date.strftime('%Y/%m/%d')
        frozen_date = (base_date + timedelta(days=2)).strftime('%Y%m%d')
        params = {
            "repo": self.repo,
            "owner": "openeuler",
            "access_token": self.token,
            "title": "{brh} Update {release_date} release".format(brh=branch, release_date=release_date)}

        remind_str = "说明：此issue为机器自动创建update发布issue"
        params["body"] = "版本目标: CVE、软件包引入升级和Bugfix修复\n版本: {brh}\n例行CVE冻结: {frozen_date}\n" \
                         "代码冻结: {frozen_date}\n\n版本发布负责人\n版本经理：{vm}\n开发人员：{dev}\n" \
                         "安全委员会：{sec}\n测试人员：{te}\n\n" \
            .format(brh=branch, frozen_date=frozen_date, vm=VERSION_MANAGER,
                    dev=DEVELOPER, sec=SECURITY_COMMITTEE, te=TESTER, remind_str=remind_str)
        return params

    def create_issue(self, data):
        """
        Description: create issue in gitee
        Args:
            data: data to create issue

        Returns:
            created_issue_id(str)
        """
        # get all the open state issue's title
        issue_title = data.get("title")

        prj_issue_url = self.externel_gitee_api_url("create_issue_url", owner=data["owner"])
        post_res = self.gitee_api_request("post", prj_issue_url, data=data)
        if not post_res:
            logger.error("failed to create the issue: {}".format(issue_title))
            return "error_issue_id"

        resp_content = json.loads(post_res.text)
        created_issue_id = resp_content["number"]
        logger.info("an issue with %s id has been created" % created_issue_id)
        return created_issue_id

    def create_update_release(self):
        """
        Description:  create release issues of all branches
        Returns:
            boolean
        """
        release_issue_dict = {}
        for branch in BRANCH_LIST:
            params = self.create_update_issue(branch)
            if len(params['body']) == 204: # length of the template body
                release_issue_dict[branch] = "error_issue_id"
                logger.error("%s create failed due to invalid issue body", branch)
                continue

            issue_id = self.create_issue(params)
            if issue_id == "error_issue_id":
                logger.error("%s create issue failed, please try again, please check", branch)
                release_issue_dict[branch] = issue_id

        if all(_ == "error_issue_id" for _ in release_issue_dict.values()):
            logger.error("All branches created failed, please check former errors,")
            return False
        logger.info("The result of issue is: {}".format(release_issue_dict))
        return True
