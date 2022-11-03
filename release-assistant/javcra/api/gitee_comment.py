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
add a comment for the address of jenkins in the comment section of issue
"""
import csv
import sys
import os
import argparse
from datetime import datetime
from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.api.jenkins_api import JenkinsJob
from javcra.common.constant import GITEE_REPO, JENKINS_BASE_URL, LTS_BRANCH, MAX_PARAL_NUM, VERSION_TABLE_HEADER
from javcra.common.constant import CHECK_RESULT_CSV_PATH
from javcra.libs.log import logger

ABSPATH = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(os.path.dirname(__file__)))))
sys.path.insert(0, ABSPATH)


class Comment(IssueOperation, JenkinsJob):
    """
    add a comment for the address of jenkins in the comment section of issue
    """

    def __init__(self, repo, token, issue_num, base_url, jenkins_user, jenkins_password, now_time):
        IssueOperation.__init__(self, repo, token, issue_num)
        JenkinsJob.__init__(self, base_url, jenkins_user, jenkins_password, MAX_PARAL_NUM, LTS_BRANCH, now_time)

    def create_comment(self, jenkins_job_name, jenkins_build_id):
        """
        add a comment for the address of jenkins in the comment section of issue
        Args:
            jenkins_job_name: jenkins job name
            jenkins_build_id: jenkins build id

        Returns:
            comment_res: comment response
        """
        output_hyperlink = self.get_output_hyperlink(jenkins_job_name, jenkins_build_id)
        if not output_hyperlink:
            logger.error("Error in getting the output url of %s." % jenkins_job_name)
            return False
        table_top = ["job_name", "output"]
        comment_body = [
            {
                "job_name": jenkins_job_name,
                "output": output_hyperlink
            }
        ]
        comment_content = self.init_md_table(table_top, comment_body)
        comment_res = self.create_issue_comment(comment_content)
        if not comment_res:
            logger.error("Failed to create Jenkins' comment message %s" % comment_res)
            return False
        return True

    def version_check_comment(self, init_path):
        """
        add a comment for the result of the check versions.
        Args:
            init_path: path of the check result

        Returns:
            comment_res: comment response
        """
        csv_path = os.path.join(init_path, CHECK_RESULT_CSV_PATH)
        if os.path.getsize(csv_path) == 0:
            comment_content = self.init_md_table(["packages_version_check_Result"],
                                                 [{"packages_version_check_Result": "All packages up to date."}])
        else:
            with open(csv_path, "r") as version_file:
                reader = csv.reader(version_file)
                table_body = self.version_table_generator(reader)
            comment_content = self.init_md_table(VERSION_TABLE_HEADER, table_body)
        comment_res = self.create_issue_comment(comment_content)
        if not comment_res:
            logger.error("Failed to create Jenkins' comment message %s" % comment_res)
            return False
        return True

    def version_table_generator(self, reader):
        """
        Generate version info of packages on gitee and obs.
        Args:
            reader: cvs reader
        Returns:
            list: list of packages' version
        """
        table_body = []
        for row in reader:
            table_comment = {VERSION_TABLE_HEADER[0]: row[1],  # package_name
                             VERSION_TABLE_HEADER[1]: row[2],  # gitee-sp1 version
                             VERSION_TABLE_HEADER[2]: row[3],  # obs-sp1 version
                             VERSION_TABLE_HEADER[3]: row[5],  # gitee-sp3 version
                             VERSION_TABLE_HEADER[4]: row[6],  # obs-sp3 version
                             VERSION_TABLE_HEADER[5]: row[8],  # gitee-sp2203 version
                             VERSION_TABLE_HEADER[6]: row[9]}  # obs-sp2203 version
            table_body.append(table_comment)
        return table_body


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="create gitee comments")
    parser.add_argument("--token", required=True, type=str, help="gitee tonken")
    parser.add_argument("--issue_num", required=True, type=str, help="gitee number")
    parser.add_argument("--jenkins_user", required=True, type=str, help="jenkins user")
    parser.add_argument("--jenkins_password", required=True, type=str, help="jenkins password")
    parser.add_argument("--jenkins_job_name", required=True, type=str, help="jenkins job name")
    parser.add_argument("--build_id", required=True, type=int, help="build id")
    parser.add_argument("--init_path", required=False, type=str, help="init path of the jenkins job")

    parser.add_argument("--comment_type",
                        required=False,
                        type=str,
                        help="comment_type",
                        default="normal",
                        choices=["normal", "check"])

    args = parser.parse_args()
    create_time = datetime.now().strftime("%Y-%m-%d")
    comment = Comment(GITEE_REPO, args.token, args.issue_num, JENKINS_BASE_URL, args.jenkins_user,
                      args.jenkins_password, create_time)

    if args.comment_type == "normal":
        resp = comment.create_comment(args.jenkins_job_name, args.build_id)
    else:
        resp = comment.version_check_comment(args.init_path)
    if resp:
        print("Successfully created an issue about jenkins information comment")
