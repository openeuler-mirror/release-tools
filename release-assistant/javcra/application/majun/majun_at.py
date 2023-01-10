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
"""
at use-case results assist in obtaining
"""
import re
import datetime
import requests
from javcra.common.constant import (
    DAYLIBUILD_URL,
    ISO_ARCH_MAP,
    MAX_PARAL_NUM,
    OBS_KEY_NAMES,
    OBS_VALUES_NAMES,
    VM_IP_MAP,
    MAX_ISO_BUILD_WAIT_TIME,
    ISO_BUILD_JOB_MAP
)
from javcra.application.majun import (
    ConstantNumber,
    catch_majun_error,
    get_product_version,
    send_content_majun,
)
from javcra.application.majun.majun_operate import MajunOperate


class MaJunAt:
    def __init__(self) -> None:
        self.task_title = None
        self.iso_build_first_info = None
        self.iso_build_last_info = None
        self.jenkins_server_obj = None
        self.iso_build_url = None
        self.headers = {
            "Content-Type": "application/json; charset=utf8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        }

    @staticmethod
    def get_iso_single_build_time(branch_name, arch_url):
        """
        The iso address of the single arch
        Args:
            branch_name: branch name
            arch_url: arch name url

        Returns:
            iso_build_url: iso build url

        """
        try:
            resp = requests.get(f"{DAYLIBUILD_URL}{branch_name}/{arch_url}/release_iso")
        except requests.RequestException as error:
            raise ValueError(
                f"An error occurred at the parse iso build time, because {error}"
            ) from error
        if not resp or resp.status_code != requests.codes.ok:
            raise ValueError("Failed to obtain the iso compile time. Procedure")
        iso_build_url = resp.text.rstrip()
        base_re = r"^(.+)(openeuler-)([\d|-]+)(.+)"
        openeuler_build_time = re.compile(base_re).search(iso_build_url)
        iso_build_time = datetime.datetime.strptime(
            openeuler_build_time.group(3),
            "%Y-%m-%d-%H-%M-%S",
        )
        return iso_build_url, iso_build_time

    @staticmethod
    def jenkins_param(branch_name):
        """
        Compose jenkins task parameters
        Args:
            branch_name: branch name

        Returns:
            base_param: jenkins parameters after composition
        """
        # jenkins parameter combination with multiple constants of the numbers 1 and 0, 
        # which are obtained using the enumeration class
        base_param = {
            "set_release_dir": ConstantNumber.CON_NUMBER_ONE.value,
            "update_release_info": ConstantNumber.CON_NUMBER_ZERO.value,
            "make_iso": ConstantNumber.CON_NUMBER_ONE.value,
            "make_docker_image": ConstantNumber.CON_NUMBER_ONE.value,
            "make_iso_everything": ConstantNumber.CON_NUMBER_ONE.value,
            "make_iso_everysrc": ConstantNumber.CON_NUMBER_ONE.value,
            "make_debug_everything": ConstantNumber.CON_NUMBER_ONE.value,
            "make_hmi": ConstantNumber.CON_NUMBER_ONE.value,
            "make_netinst_iso": ConstantNumber.CON_NUMBER_ONE.value,
            "make_raspi_image": ConstantNumber.CON_NUMBER_ONE.value,
        }
        base_param.update(dict(vm_ip=VM_IP_MAP.get(branch_name)))
        base_param.update(dict(zip(OBS_KEY_NAMES, OBS_VALUES_NAMES.get(branch_name))))
        return base_param

    def all_iso_time(self, branch_name):
        """
        Get the iso urls for the different arch
        Args:
            branch_name: branch name

        Returns:
            all_iso_info: iso addresses for different architectures
        """
        all_iso_info = dict()
        for arch_name, arch_url in ISO_ARCH_MAP.items():
            iso_build_url, iso_build_time = self.get_iso_single_build_time(
                branch_name, arch_url
            )
            all_iso_info[arch_name] = dict(
                iso_build_url=iso_build_url, iso_build_time=iso_build_time
            )
        return all_iso_info

    @catch_majun_error
    def run(self, params):
        """
        Function main entry
        Args:
            params: Parameter from the command line

        Returns:
            Send the results to majun
        """
        self.task_title = params.task_title
        branch_name, freeze_date, _ = get_product_version(self.task_title)
        # Gets the first build time of the iso build.
        self.iso_build_first_info = self.all_iso_time(branch_name)
        self.jenkins_server_obj = MajunOperate.jenkins_server(
            params, MAX_PARAL_NUM, branch_name, freeze_date
        )
        jenkins_params = self.jenkins_param(branch_name)
        jenkins_job = ISO_BUILD_JOB_MAP.get(branch_name)
        res = self.jenkins_server_obj.get_jenkins_job_build_result(
            jenkins_params, jenkins_job, MAX_ISO_BUILD_WAIT_TIME
        )
        if not res or res[0].get("status") != "SUCCESS":
            raise ValueError(
                "The iso construction fails. Check the cause of the failure"
            )
        # Gets the last build time of the iso build.
        self.iso_build_last_info = self.all_iso_time(branch_name)
        iso_urls = list()
        for arch_name, iso_info in self.iso_build_last_info.items():
            if (
                iso_info.get("iso_build_time")
                - self.iso_build_first_info.get(arch_name).get("iso_build_time")
            ).seconds <= 0:
                raise ValueError(
                    "The iso url is not updated. Check the cause manually"
                )
            else:
                iso_urls.append(iso_info.get("iso_build_url"))
        return send_content_majun(";".join(iso_urls), params.id)
