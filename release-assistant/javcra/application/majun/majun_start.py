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

import datetime
import requests
from pytz import timezone
from retrying import retry
from javcra.libs.log import logger
from javcra.libs.read_excel import download_file
from javcra.application.checkpart.check_requires.shell_api_tool import ShellCmdApi
from javcra.application.majun import (
    send_content_majun,
    get_product_version,
    catch_majun_error,
)
from javcra.common.constant import WAIT_NUMBER, WAIT_TIME, CVE_MANAGE_URL


class MaJunStart:
    """
    cve-manage archiving is triggered to read archived data and send it to majun platform
    """

    def __init__(self) -> None:
        self.headers = {"Content-Type": "application/json; charset=utf8"}

    @staticmethod
    def cve_list_recombine(cve_list):
        """
        cve list Data regroup
        Args:
            cve_list: cve list

        Returns:
            The combined data
        """
        new_cve_list = list()
        if not cve_list:
            return new_cve_list
        for cve in cve_list[:]:
            if "abi是否变化" in cve.keys():
                cve.update({"abiChange": cve.pop("abi是否变化")})
            if "仓库" in cve.keys():
                cve.update({"software": cve.pop("仓库")})
            new_cve_list.append(cve)
        return new_cve_list

    def trigger_cve_archive(self, user_email):
        """
        cve-manage archiving is triggered
        Args:
            user_email: user email

        Returns:
            cve-manage archiving is triggered
        """
        # Take cve within three months
        start_time = (
                datetime.datetime.now(tz=timezone("Asia/Shanghai"))
                + datetime.timedelta(days=-90)
        ).strftime("%Y-%m-%d")
        try:
            email_name = user_email.split("@")[0]
        except AttributeError as error:
            logger.error("The CVE List file fails to be archived because %s " % error)
            return False
        parameter = {"startTime": start_time, "typeName": email_name}
        try:
            response = requests.get(CVE_MANAGE_URL, headers=self.headers, params=parameter)
        except requests.RequestException as error:
            logger.error("The CVE List file fails to be archived because %s " % error)
            return False
        if response.status_code == 200 and "a task being processed" in response.text:
            logger.info(
                "The CVE-Manager is triggered to generate the CVE list and archive the CVE list"
            )
            return True
        logger.error(
            "The CVE List file fails to be archived,"
            "The response status code is %s,"
            "the response body is %s" % (response.status_code, response.text)
        )
        return False

    @retry(
        stop_max_attempt_number=WAIT_NUMBER,
        wait_incrementing_start=WAIT_TIME,
        wait_incrementing_increment=WAIT_TIME,
    )
    def get_cve_list(self, branch_name, obs_ak, obs_sk):
        """
        Obtain CVE-related information provided by the CVE-Manager.
        Returns:
            cve_list: Data in Excel in dictionary form
        """
        now_time = datetime.datetime.now(tz=timezone("Asia/Shanghai")).strftime(
            "%Y-%m-%d"
        )
        cve_list = download_file(
            now_time, "{}_updateinfo.xlsx".format(branch_name), obs_ak, obs_sk
        )
        if not cve_list:
            logger.error("Failed to obtain CVE data")
            raise ValueError("Failed to obtain CVE data")
        return cve_list

    @catch_majun_error
    def send_cve_list_to_majun(self, params):
        """
        start function general entry
        Args:
            params: Command line argument
        Returns:
            Data sent to majun results
        """
        # Gets the branch and the date
        user_email, obs_ak, obs_sk, task_title, majun_id = (
            params.useremail,
            params.ak,
            params.sk,
            params.task_title,
            params.id,
        )
        # openEuler-20.03-LTS-SP1_update20221013.
        branch_name, _, multi_content = get_product_version(task_title)
        if not branch_name:
            logger.error("Failed to obtain branch")
            return send_content_majun([], majun_id)
        # trigger cve_manger to archive
        resp = self.trigger_cve_archive(user_email)
        if not resp:
            raise ValueError("trigger cve-manege archive failure")
        cve_list = []
        try:
            cve_list = self.get_cve_list(branch_name, obs_ak, obs_sk)
        except ValueError as e:
            logger.error("get cve list failed!")
        new_cves = self.cve_list_recombine(cve_list)
        if not new_cves:
            logger.info("new_cves is empty,send it to majun")
            return send_content_majun(new_cves, majun_id, multip_start=True)
        if multi_content:
            obs_project = f"{branch_name.replace('-', ':')}:{multi_content}"
            all_multi_packages = ShellCmdApi.call_subprocess(
                ["osc", "ls", obs_project]
            ).splitlines()
            new_cves = [
                new_cve
                for new_cve in new_cves[:]
                if new_cve.get("software") in all_multi_packages
            ]
            return send_content_majun(new_cves, majun_id, multip_start=True)
        else:
            return send_content_majun(new_cves, majun_id)
