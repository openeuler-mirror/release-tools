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
Description: check method's entrance for custom commands
Class:CheckCommand
"""

from javcra.api.jenkins_api import JenkinsJob
from javcra.application.checkpart.checkentrance import CheckEntrance
from javcra.application.checkpart.checktest import CheckTest
from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.application.serialize.serialize import CheckSchema
from javcra.cli.base import BaseCommand

from javcra.cli.commands import parameter_permission_validate
from javcra.common import constant
from javcra.common.constant import (
    GITEE_REPO,
    MAX_PARAL_NUM,
    REALSE_TOOLS_BUCKET_NAME,
    REALSE_TOOLS_SERVER,
    X86_FRAME, CHECK_COMMENT_DICT, EPOL_DICT)

from javcra.api.obscloud import ObsCloud


class CheckCommand(BaseCommand):
    """
    Description: start the check part
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(CheckCommand, self).__init__()
        self.add_subcommand_communal_args('check', help_desc="release assistant of check part")
        self.sub_parse.add_argument(
            "--type",
            help="the type of check part, \
                including requires, issue status and test result",
            action="store",
            nargs=None,
            required=True,
            choices=["status", "requires", "test"],
        )
        self.sub_parse.add_argument(
            "--ak",
            type=str,
            help="provide obs access key",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--sk",
            type=str,
            help="provide obs secret key",
            action="store",
            required=True,
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

    @staticmethod
    def jenkins_server(params, paral_num, branch_name, release_date):
        """
        Description: to get the jenkins server
        Args:
            params: Command line parameters
            paral_num: paral num of jenkins job
            branch_name: branch name of release issue
            release_date: date of release

        Returns:
            jenkins server object
        """

        jenkins_server = JenkinsJob(
            constant.JENKINS_BASE_URL,
            params.jenkinsuser,
            params.jenkinskey,
            paral_num,
            branch_name,
            release_date,
        )
        return jenkins_server

    @staticmethod
    def check(params):
        """
        Description: to get check object
        Args:
            params: Command line parameters

        Returns:
            check object
        """
        check = CheckTest(GITEE_REPO, params.token, params.releaseIssueID)
        return check

    @staticmethod
    def issue(params):
        """
        Description: to get issue object
        Args:
            params: Command line parameters

        Returns:
            issue object
        """
        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)
        return issue

    @staticmethod
    def check_issue(params):
        """
        Description: to get check_issue object
        Args:
            params: Command line parameters

        Returns:
            check_issue object
        """
        check_issue = CheckEntrance(GITEE_REPO, params.token, params.releaseIssueID)
        return check_issue

    def test_operation(self, params):
        """
        Description: the operation for test
        Args:
            params: Command line parameters

        Returns:
            True or False
        """
        review_res = self.check(params).people_review()
        if not review_res:
            print("[ERROR] failed to operate test in check part.")
            return False
        print("[INFO] successfully operate test in check part.")
        return True

    def status_operation(self, params):
        """
        Description: operation for status
        Args:
            params: Command line parameters

        Raises:
            ValueError: throw an exception when the function call returns false
        """
        issue = self.issue(params)
        check_issue = self.check_issue(params)

        # check whether all the issue status is incomplete
        status_res = issue.check_issue_state()
        if not status_res:
            raise ValueError("failed to update status in check part.")
        print("[INFO] successfully update status in check part.")

        # statistics of the status of all issues
        count_res = issue.count_issue_status()
        if not count_res:
            raise ValueError("the status of the issue is not all completed, please complete first")
        print("[INFO] All issues are completed, the next step is sending repo to test platform.")

        # send repo info
        resp = check_issue.send_repo_info()
        if not resp:
            print("[ERROR] failed to send repo info.")
            return
        print("[INFO] successfully to send repo info.")

    def requires_operation(self, params):
        """
        Description: operation for get requires
        Args:
            params: Command line parameters

        Returns:
        """

        def transfer_pkg_rpm(obs_project, pkg_family, pkgs, obs_action):
            """
            transfer the rpm package to the server, and comment on the Jenkins
            job result on the release issue
            """
            obs_job_params = {
                "ScanOSSAPIURL": constant.JENKINS_API_URL,
                "ScanOSSResultRepo": constant.JENKINS_SERVER_REPO,
                "action": obs_action,
                "obs_project": obs_project,
                "update_dir": "update_" + release_date,
                "package_family": pkg_family,
                "pkgnamelist": ",".join(pkgs),
            }
            jenkins_obs_res = jenkins_server.get_specific_job_comment(
                obs_job_params, constant.OBS_RELEASE_JOB
            )
            return jenkins_obs_res

        def verify_selfbuild():
            """
            verify selfbuild for update pkg_list

            """
            jenkins_server.delete_jenkins_job(
                constant.JENKINS_PATH_PREFIX
                + "/"
                + branch_name
            )
            created_res = jenkins_server.create_selfbuild_jenkins_jobs(update_pkgs)
            if not created_res:
                raise ValueError("failed to create selfbuild jenkins job.")

            build_status_res = jenkins_server.get_selfbuild_job_comment()
            return build_status_res

        def verify_install(epol_flag, install_pkgs):
            """
            verify install for pkgs list
            """
            install_jobs_params = {
                "ScanOSSAPIURL": constant.JENKINS_API_URL,
                "ScanOSSResultRepo": constant.JENKINS_SERVER_REPO,
                "ARCH": X86_FRAME,
                "EPOL": epol_flag,
                "UPDATE_TIME": release_date,
                "BRANCH": branch_name,
                "PKGLIST": ",".join(install_pkgs)
            }
            install_status_res = jenkins_server.get_specific_job_comment(
                install_jobs_params, constant.INSTALL_JOB_PREFIX + branch_name
            )
            return install_status_res

        def issue_write_back(install_or_build, pkgs):
            """
            create issue when install or selfbuild failed, and then write back to release issue
            """
            install_or_build_dict = {"build_list": "build", "install_list": "install"}
            for pkg in pkgs:
                issue_id = issue.create_install_build_issue(
                    install_or_build_dict.get(install_or_build), pkg
                )
                if not issue_id:
                    print("failed to create %s issue for %s." % (install_or_build, pkg))
                else:
                    write_res = issue.operate_release_issue(
                        operation="add",
                        operate_block="install_build",
                        issues=[issue_id],
                    )
                    if not write_res:
                        print("failed to write back to install_build issue %s in release issue" % issue_id)

        issue = self.issue(params)
        check_issue = self.check_issue(params)
        branch_name, update_pkgs, release_date = self.get_release_info(issue)

        standard_list, epol_list = issue.get_standard_epol_list(branch_name, update_pkgs)

        # get parallel jenkins job num according to length of pkg_list and max parallel num
        paral_num = min(MAX_PARAL_NUM, len(update_pkgs))

        # get jenkins_server and cloud server
        jenkins_server = self.jenkins_server(params, paral_num, branch_name, release_date)
        cloud_server = ObsCloud(
            params.ak, params.sk, REALSE_TOOLS_SERVER, REALSE_TOOLS_BUCKET_NAME
        )

        # delete install and build archive in hw cloud
        res = cloud_server.delete_dir("install_build_log/{}".format(branch_name))
        if not res:
            raise ValueError("obs cloud delete last archived file failed")

        # verify that the dependencies and write back the missing dependencies to the issue description
        check_res = issue.operate_release_issue(
            operation="add", operate_block="requires"
        )
        if not check_res:
            print("[ERROR] failed to get requires.")
        else:
            print("[INFO] successfully get requires.")

        # upload or update the rpm package to the server
        action = "create"
        repo_list = check_issue.get_repo(md_type=False)
        if check_issue.request_repo_url(repo_list):
            print("already exists the repo url, then update the pkglist in repo.")
            action = "update"

        obs_prj = branch_name.replace("-", ":")
        stand_transfer_res = transfer_pkg_rpm(obs_prj, "standard", standard_list, action)
        self.create_comment("transfer standard rpm jenkins res", stand_transfer_res, issue)

        pkg_family = EPOL_DICT.get(branch_name)
        if not pkg_family:
            raise ValueError("failed to get epol name of jenkins job for %s." % branch_name)

        if epol_list:
            obs_prj = obs_prj + ":" + "Epol"
            epol_transfer_res = transfer_pkg_rpm(obs_prj, pkg_family, epol_list, action)
            self.create_comment("transfer epol rpm jenkins res", epol_transfer_res, issue)

        # add the repo content to the release issue
        add_res = check_issue.add_repo_in_table()
        if not add_res:
            raise ValueError("failed to add repo in release issue.")
        print("[INFO] successful to add repo in release issue.")

        # self-build verification
        selfbuild_res = verify_selfbuild()
        self.create_comment("selfbuild jenkins res", selfbuild_res, issue)

        # installation verification
        stand_install_res = verify_install("false", standard_list)
        self.create_comment("standard install jenkins res", stand_install_res, issue)
        if epol_list:
            epol_install_res = verify_install("true", epol_list)
            self.create_comment("epol install jenkins res", epol_install_res, issue)

        # obtain and analyze the self-build installation results from file server
        parsed_install_build_res = cloud_server.parse_install_build_content(branch_name)

        # If the selfbuild or install fails, create issue and then write the issue_id back to the release issue
        for issue_type, pkg_list in parsed_install_build_res.items():
            issue_write_back(issue_type, pkg_list)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters

        """
        comment = CHECK_COMMENT_DICT.get(params.type)
        if not comment:
            print("[ERROR] not allowed operation, please check.")
            return

        param_dict = {
            "issueid": params.releaseIssueID,
            "giteeid": params.giteeid,
            "type": params.type,
            "token": params.token,
            "ak": params.ak,
            "sk": params.sk,
            "jenkinsuser": params.jenkinsuser,
            "jenkinskey": params.jenkinskey,
        }
        validate_result = parameter_permission_validate(
            CheckSchema, param_dict, comment
        )
        if not validate_result:
            return
        try:
            getattr(self, "{}_operation".format(params.type))(params)
        except ValueError as error:
            print("during the operation %s, a failure occurred, "
                  "and the cause of the error was %s" % (params.type, error))
