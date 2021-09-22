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
Description: get 'check test' restult, it would be yes or no
Class:
"""
from javcra.api.gitee_api import Issue
from javcra.common.constant import ROLE_DICT
from javcra.common.constant import ROLES
from javcra.libs.log import logger


class CheckTest(Issue):
    """
    check test
    Attributes:
        repo: repo
        token: token
        issue_num: issue_num
    """

    def __init__(self, repo, token, issue_num):
        super().__init__(repo, token, issue_num)

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
            # get personnel permissions from the issue body and get personnel
            # permissions dict from the issue body, like{"version_manager":"@xxx", ...}
            for con in body.split("\n"):
                colon = "：" if "：" in con else ":"
                for role, people in ROLE_DICT.items():
                    if people + colon not in con:
                        continue
                    personnel_access[role] = con.split(people + colon)[1]
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
        # To use it, go to @tc\release\qa\security_committee\version_manager after check -ok
        names = list()
        for role in ROLES:
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
