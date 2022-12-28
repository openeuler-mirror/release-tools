#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from javcra.api.gitee_api import Issue
from javcra.common.constant import (
    CVE_UPDATE_INFO_JOB_NAME,
    CVRF_JOB_NAME,
    EPOL_DICT,
    MAX_PARAL_NUM,
    MULTI_VERSION_BRANCHS,
    OBS_PROJECT_MULTI_VERSION_MAP,
    REPO_BASE_URL,
    TEST_MILESTONE_URL,
)
from javcra.application.majun import (
    catch_majun_error,
    get_product_version,
    send_content_majun,
)
from javcra.api.jenkins_api import JenkinsJob
from javcra.common import constant
from javcra.libs.log import logger


class MajunOperate:
    """
    Operation jenkins sends data to majun
    """

    def __init__(self) -> None:
        self.task_title = None
        self.pkglist = None
        self.jenkins_server_obj = None
        self.headers = {
            "Content-Type": "application/json; charset=utf8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        }

    @staticmethod
    def get_repo(branch_name, release_date, pkglist):
        """
        get repo according to branch 、date and epol
        Args:
            branch_name: branch name
            release_date: Release date
            pkglist: package names

        Returns:
            repos: Addresses of all generated repo
            standard_list: standard package names
            epol_list: epol package names
        """
        standard_list, epol_list = Issue.get_standard_epol_list(branch_name, pkglist)
        base_url = REPO_BASE_URL + branch_name
        repos = [{"repo_type": "standard", "url": f"{base_url}/update_{release_date}/"}]
        if epol_list:
            repo_dict = dict()
            repo_dict["repo_type"] = "epol"
            if any(mul_branch in branch_name for mul_branch in MULTI_VERSION_BRANCHS):
                repo_dict["url"] = f"{base_url}/EPOL/update_{release_date}/main/"
            else:
                repo_dict["url"] = f"{base_url}/EPOL/update_{release_date}/"
            repos.append(repo_dict)
        return repos, standard_list, epol_list

    @staticmethod
    def judge_result(transfer_res):
        """
        Determine jenkins running results
        Args:
            transfer_res: jenkins results

        Returns:
            Return true on success and false on failure
        """
        return True if transfer_res and transfer_res[0].get("status") == "SUCCESS" else False
        
    @staticmethod
    def jenkins_server(
        params,
        paral_num=MAX_PARAL_NUM,
        release_date="",
        branch_name="",
    ):
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

    def send_data_test_platform(self, update_data, majun_id):
        """
        Send data to the test platform and get milestones
        Args:
            update_data: Data sent to the test platform
            majun_id: majub id

        Returns:
            The result of sending the data to majun
        """

        try:
            resp = requests.post(
                TEST_MILESTONE_URL, data=json.dumps(update_data), headers=self.headers
            )
        except requests.RequestException as error:
            raise ValueError(f"Request test failed, {error}") from error
        try:
            res_text = json.loads(resp.text)
        except json.JSONDecodeError as error:
            raise ValueError(f"JSONDecodeError,because {error}") from error
        if not resp or resp.status_code != 200 or res_text.get("error_code") != "2000":
            raise ValueError(f"Request test failed,{resp.status_code} and {resp.text}")
        else:
            logger.info("Successful milestone acquisition")
            return send_content_majun(
                res_text.get("data", {}).get("milestone_name"), majun_id
            )

    @catch_majun_error
    def send_repo_info(self, params):
        """
        to send repo info
        Args:
            params: Command line argument
        Returns:
            True or False
        """
        majun_id, self.pkglist, self.task_title = (
            params.id,
            params.pkglist,
            params.task_title,
        )
        branch_name, release_date, multi_content = get_product_version(self.task_title)
        product_version = branch_name.split("-", 1)
        update_data = {
            "product": product_version[0],
            "version": product_version[1],
            "pkgs": self.pkglist,
        }
        if not multi_content:
            # The normal version sends data
            repo_list, _, _ = self.get_repo(branch_name, release_date, self.pkglist)
            # branch demo: openEuler-20.03-LTS-SP1
            for repo_info in repo_list:
                if repo_info.get("repo_type") == "standard":
                    update_data["base_update_url"] = repo_info.get("url")
                else:
                    update_data["epol_update_url"] = repo_info.get("url")
        else:
            # Multiple versions send data
            multi_contents = multi_content.rsplit(":", 2)
            folder_name = f"{multi_contents[-1]}/{multi_contents[-2]}"

            update_data[
                "base_update_url"
            ] = f"{REPO_BASE_URL}{branch_name}/update_{release_date}/"
            update_data[
                "epol_update_url"
            ] = f"{REPO_BASE_URL}{branch_name}/EPOL/update_{release_date}/multi_version/{folder_name}/"
        return self.send_data_test_platform(update_data, majun_id)

    def transfer_pkg_rpm(self, *args, pkgs=None):
        """
        transfer the rpm package to the server, and comment on the Jenkins
        job result on the release issue
        """
        obs_project, pkg_family, obs_action, release_date = args
        obs_job_params = {
            "ScanOSSAPIURL": constant.JENKINS_API_URL,
            "ScanOSSResultRepo": constant.JENKINS_SERVER_REPO,
            "action": obs_action,
            "obs_project": obs_project,
            "update_dir": "update_" + release_date,
            "package_family": pkg_family,
        }
        if pkgs:
            obs_job_params.update({"pkgnamelist": ",".join(pkgs)})
        jenkins_obs_res = self.jenkins_server_obj.get_specific_job_comment(
            obs_job_params, constant.OBS_RELEASE_JOB
        )
        return jenkins_obs_res

    @catch_majun_error
    def operate_repo(self, params):
        """
        Manipulate the main entry to the repo source
        Args:
            params: Command line argument

        Returns:
            result to majun
        """
        self.task_title = params.task_title
        branch_name, release_date, multi_content = get_product_version(self.task_title)
        if multi_content:
            obs_project = f"{branch_name.replace('-', ':')}:{multi_content}"
            multi_contents = multi_content.rsplit(":", 2)
            folder_name = f"{multi_contents[-1]}/{multi_contents[-2]}"
        else:
            obs_project = branch_name.replace("-", ":")
            folder_name = None
        # get jenkins_server object
        self.jenkins_server_obj = self.jenkins_server(
            params, MAX_PARAL_NUM, branch_name, release_date
        )
        if params.action in ["create", "del_pkg_rpm", "update"]:
            # The create del_pkg_rpm update action is mandatory according to pkglist
            if not multi_content:
                # Daily version operation
                return self._normal_repo(branch_name, release_date, obs_project, params)
            else:
                # Multiversion operation
                return self._multi_repo(
                    branch_name, release_date, obs_project, params, folder_name
                )
        else:
            # del_update_dir
            stand_transfer_res = self.transfer_pkg_rpm(
                obs_project, params.package_family, params.action, release_date
            )
            return send_content_majun(self.judge_result(stand_transfer_res), params.id)

    @catch_majun_error
    def synchronous_info(self, params):
        """
        Call cvrf synchronization and updateinfo to synchronize the jenkins project
        Args:
            params: Incoming parameter

        Returns:
            jenkins runs the result back to majun
        """
        self.jenkins_server_obj = self.jenkins_server(params)
        jenkins_params = dict(
            server=params.server, bucketname=params.bucketname, ipaddr=params.ipaddr
        )
        sync_func_map = {"cvrf": "single", "updateinfo": "single", "all": "all"}
        return getattr(self, "_{}_sync".format(sync_func_map.get(params.choice)))(
            params, jenkins_params
        )

    def _all_sync(self, params, jenkins_params):
        """
        Call both the cvrf and update info tasks
        Args:
            params: Incoming parameter
            jenkins_params: jenkins task parameter

        Returns:
            Send data to majun
        """
        new_params = copy.deepcopy(jenkins_params)
        jenkins_params.update({"filename": params.cvrffilename})
        new_params.update({"filename": params.updatefilename})
        with ThreadPoolExecutor(max_workers=2) as pool:
            cvrf_future = pool.submit(
                self.jenkins_server_obj.get_specific_job_comment,
                jenkins_params,
                CVRF_JOB_NAME,
            )
            updateinfo_future = pool.submit(
                self.jenkins_server_obj.get_specific_job_comment,
                new_params,
                CVE_UPDATE_INFO_JOB_NAME,
            )
            jenkins_result = all(
                [
                    self.judge_result(future.result())
                    for future in as_completed([cvrf_future, updateinfo_future])
                ]
            )
            # Send data to majun
            return send_content_majun(jenkins_result, params.id)

    def _normal_repo(self, branch_name, release_date, obs_project, params):
        """
        Daily operation  repo
        Args:
            branch_name: branch name
            release_date: release data
            obs_project: obs project name
            params: Command line argument

        Returns:
            Send data to majun result
        """
        repos, standard_packages, epol_packages = self.get_repo(
            branch_name, release_date, params.pkglist
        )
        stand_transfer_res = self.transfer_pkg_rpm(
            obs_project, "standard", params.action, release_date, pkgs=standard_packages
        )
        if not self.judge_result(stand_transfer_res):
            return send_content_majun(False, params.id)
        if epol_packages:
            pkg_family = EPOL_DICT.get(branch_name)
            if not pkg_family:
                raise ValueError(
                    f"failed to get epol name of jenkins job for {branch_name}"
                )
            obs_project = obs_project + ":" + "Epol"
            epol_transfer_res = self.transfer_pkg_rpm(
                obs_project, pkg_family, epol_packages, params.action, release_date
            )
            if not self.judge_result(epol_transfer_res):
                return send_content_majun(False, params.id)
        if params.action == "create":
            data = {repo.get("repo_type"): repo.get("url") for repo in repos}
        elif params.action == "del_pkg_rpm":
            data = ",".join(params.pkglist)
        else:
            data = True
        return send_content_majun(data, params.id)

    def _multi_repo(self, *args):
        """
        Multi-version operation repo
        Args:
            branch_name: branch name
            release_date: release data
            obs_project: obs project name
            params: Command line argument
            folder_name: folder name

        Returns:
            Send data to majun
        """
        branch_name, release_date, obs_project, params, folder_name = args
        if obs_project not in OBS_PROJECT_MULTI_VERSION_MAP.keys():
            raise ValueError(
                "If the package has multiple versions, package_family must have a value"
            )
        package_family = "EPOL-multi_version"
        _transfer_res = self.transfer_pkg_rpm(
            obs_project,
            package_family,
            params.action,
            release_date,
            pkgs=params.pkglist,
        )
        if not self.judge_result(_transfer_res):
            return send_content_majun(False, params.id)
        if params.action == "create":
            data = {
                "epol": f"{REPO_BASE_URL}{branch_name}/EPOL/update_{release_date}/multi_version/{folder_name}"
            }
        elif params.action == "del_pkg_rpm":
            data = ",".join(params.pkglist)
        else:
            data = True
        return send_content_majun(data, params.id)

    def _single_sync(self, params, jenkins_params):
        """
        cvrf or update info jenkins job
        Args:
            params: incoming params
            jenkins_params: jenkins params

        Returns:
            send data to majun
        """
        if params.choice == "cvrf":
            jenkins_params.update({"filename": params.cvrffilename})
        else:
            jenkins_params.update({"filename": params.updatefilename})
        jenkins_job = (
            CVRF_JOB_NAME if params.choice == "cvrf" else CVE_UPDATE_INFO_JOB_NAME
        )
        jenkins_obs_res = self.jenkins_server_obj.get_specific_job_comment(
            jenkins_params, jenkins_job
        )
        return send_content_majun(self.judge_result(jenkins_obs_res), params.id)
