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
from javcra.common.constant import MAX_PARAL_NUM, GITEE_REPO


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
            choices=['checkok', 'cvrfok']
        )
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

    def checkok_operation(self, params):
        """
        Description: operation for check ok
        Args:
            params: Command line parameters
        Returns:
        """

        def publish_rpms(obs_project, pkg_family):
            """
            publish the rpm package
            """
            obs_job_params = {
                "ScanOSSAPIURL": constant.JENKINS_API_URL,
                "ScanOSSResultRepo": constant.JENKINS_SERVER_REPO,
                "action": "release",
                "obs_project": obs_project,
                "update_dir": "update_" + release_date,
                "package_family": pkg_family,
            }
            jenkins_obs_res = jenkins_server.get_specific_job_comment(
                obs_job_params, constant.OBS_RELEASE_JOB
            )
            return jenkins_obs_res

        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)
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

        # publish pkg rpms
        obs_prj = branch_name.replace("-", ":")
        standard_list, epol_list = issue.get_standard_epol_list(branch_name, update_pkgs)
        stand_transfer_res = publish_rpms(obs_prj, "standard")
        self.create_comment("transfer standard rpm jenkins res", stand_transfer_res, issue)

        if epol_list:
            obs_prj = obs_prj + ":" + "Epol"
            epol_transfer_res = publish_rpms(obs_prj, "EPOL")
            self.create_comment("transfer epol rpm jenkins res", epol_transfer_res, issue)

    def cvrfok_operation(self, params):
        """
        Description: operation for cvrf ok
        Args:
            params: Command line parameters

        Returns:

        """

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
