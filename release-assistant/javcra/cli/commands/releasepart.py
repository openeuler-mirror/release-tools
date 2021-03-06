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
Description: release method's entrance for custom commands
Class:ReleaseCommand
"""

from javcra.api.jenkins_api import JenkinsJob
from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.application.serialize.serialize import ReleaseSchema
from javcra.cli.base import BaseCommand
from javcra.cli.commands import parameter_permission_validate
from javcra.common import constant
from javcra.common.constant import MAX_PARAL_NUM, GITEE_REPO, EPOL_DICT, COMMENT_DICT


class ReleaseCommand(BaseCommand):
    """
    Description: start the release part
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(ReleaseCommand, self).__init__()
        self.add_subcommand_communal_args('release', help_desc="release assistant of release part")
        self.sub_parse.add_argument(
            '--type',
            help='Specify the release check type, only allow checkok and cvrfok',
            action='store',
            choices=['checkok', 'cvrfok'])
        self.sub_parse.add_argument(
            "--jenkinsuser",
            type=str,
            help="provide your jenkinsuser",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--jenkinskey",
            type=str,
            help="provide your jenkins key",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--publishuser",
            type=str,
            help="provide your publishuser",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--publishkey",
            type=str,
            help="provide your publish key",
            action="store",
            required=True,
        )

    def judge_test_comment(self, issue, params):
        """
        Description: judge whether /test-ok in comment area
        Args:
            issue: issue object
            params: Command line parameters

        Returns:
            True or False
        """
        comment_params = {"owner": "openEuler", "repo": GITEE_REPO, "issue_id": params.releaseIssueID}
        comment_list = [COMMENT_DICT.get("test")]
        judge_res = issue.judge_specific_comment_exists(comment_list, comment_params)
        if not judge_res:
            print("[ERROR] test not OK, please check.")
            return False
        return True

    def checkok_operation(self, params):
        """
        Description: operation for check ok
        Args:
            params: Command line parameters
        Returns:
        """

        def publish_or_delete_rpms(obs_project, pkg_family, action, pkgname_list=None):
            """
            publish the rpm package
            """
            obs_job_params = {
                "ScanOSSAPIURL": constant.JENKINS_API_URL,
                "ScanOSSResultRepo": constant.JENKINS_SERVER_REPO,
                "action": action,
                "obs_project": obs_project,
                "update_dir": "update_" + release_date,
                "package_family": pkg_family,
            }

            if action == "del_pkg_rpm":
                obs_job_params["pkgnamelist"] = ",".join(pkgname_list)

            jenkins_obs_res = jenkins_server.get_specific_job_comment(
                obs_job_params, constant.OBS_RELEASE_JOB
            )
            return jenkins_obs_res

        def process_stand_epol_rpms(pkg_list, obs_prj_name, action):
            """
            process standard and epol pkg rpms
            """
            standard_list, epol_list = issue.get_standard_epol_list(branch_name, pkg_list)
            stand_transfer_res = publish_or_delete_rpms(obs_prj_name, "standard", action, standard_list)
            self.create_comment("{action} standard rpm jenkins res".format(action=action), stand_transfer_res, issue)

            pkg_family = EPOL_DICT.get(branch_name)
            if not pkg_family:
                raise ValueError("failed to get epol name of jenkins job for %s." % branch_name)

            if epol_list:
                obs_prj_name = obs_prj_name + ":" + "Epol"
                epol_transfer_res = publish_or_delete_rpms(obs_prj_name, pkg_family, action, epol_list)
                self.create_comment("{action} epol rpm jenkins res".format(action=action), epol_transfer_res, issue)

        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)

        judege_res = self.judge_test_comment(issue, params)
        if not judege_res:
            return

        branch_name, update_pkgs, release_date = self.get_release_info(issue)

        # get parallel jenkins job num according to length of pkg_list and max parallel num
        paral_num = min(MAX_PARAL_NUM, len(update_pkgs))

        # get jenkins_server
        jenkins_server = JenkinsJob(
            constant.JENKINS_BASE_URL,
            params.jenkinsuser,
            params.jenkinskey,
            paral_num,
            branch_name,
            release_date,
        )
        obs_prj = branch_name.replace("-", ":")

        # delete remain pkg rpms
        remain_pkgs = issue.get_remain_packages()
        if remain_pkgs:
            print("remain issues exists, need to delete rpms for repo.")
            process_stand_epol_rpms(remain_pkgs, obs_prj, "del_pkg_rpm")

        # publish pkg rpms
        process_stand_epol_rpms(update_pkgs, obs_prj, "release")

    def cvrfok_operation(self, params):
        """
        Description: operation for cvrf ok
        Args:
            params: Command line parameters

        Returns:

        """
        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)
        judege_res = self.judge_test_comment(issue, params)
        if not judege_res:
            return

        release_resp = IssueOperation.release_announcement(params.publishuser, params.publishkey)
        if not release_resp:
            raise ValueError("failed to publish announcement")
        print("successful announcement")

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        """
        param_dict = {
            "issueid": params.releaseIssueID,
            "giteeid": params.giteeid,
            "type": params.type,
            "token": params.token,
            "jenkinsuser": params.jenkinsuser,
            "jenkinskey": params.jenkinskey,
            "publishuser": params.publishuser,
            "publishkey": params.publishkey
        }

        release_type = params.type
        comment = "/" + release_type[:-2] + "-" + release_type[-2:]

        validate_result = parameter_permission_validate(
            ReleaseSchema, param_dict, comment
        )
        if not validate_result:
            return

        try:
            getattr(self, "{}_operation".format(params.type))(params)
        except ValueError as error:
            print("during the operation %s, a failure occurred, "
                  "and the cause of the error was %s" % (params.type, error))
