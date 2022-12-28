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

import re
import collections
import requests
from pyrpm.spec import Spec, replace_macros
from requests import RequestException
from javcra.application.checkpart.check_requires.shell_api_tool import ShellCmdApi
from javcra.application.majun import get_product_version, send_content_majun
from javcra.common.constant import BRANCH_MAP, OBS_PROJECT_MULTI_VERSION_MAP
from javcra.libs.log import logger


class PackageVersion:
    def __init__(self) -> None:
        self.pkglist = None
        self.majun_id = None
        self.branch_map = collections.OrderedDict(BRANCH_MAP)
        self.task_title = None
        self.repo_arch_map = {"arm": "aarch64", "x86": "x86_64"}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        }

    @staticmethod
    def osc_ls_binaries_list(proj, pkg, arch):
        """
        Get the binary files archived on OBS
        Args:
            proj: project name
            pkg: package name
            arch: arch or x86

        Returns:
            Binary package list
        """
        cmd = "osc ls -b {proj} {pkg} {repo} {arch}".format(
            proj=proj, pkg=pkg, repo=f"standard_{arch}", arch=arch
        )
        stout = ShellCmdApi.call_subprocess(cmd.split())
        return stout

    def parse_spec_version(self, spec_format_url):
        """
        Parse spec content
        Args:
            spec_format_url: repo spec url

        Returns:
            version: Package Version
            release: package release
        """
        version, release = "", ""
        try:
            response = requests.get(spec_format_url, headers=self.headers)
        except RequestException as error:
            logger.error(f"An error occurred parsing spec contents {error}")
            return version, release
        if response.status_code != requests.codes.ok or not response.text:
            return version, release
        try:
            spec = Spec.from_string(response.text)
        except AttributeError as error:
            logger.error(f"An error occurred parsing spec contents {error}")
            return version, release
        version = replace_macros(spec.version, spec)
        release = replace_macros(spec.release, spec)
        return version, release

    def git_package_version(self, packagename, branch_name):
        """
        Get the contents in the spec on the git repository
        Args:
            packagename: package name
            branch_name: branch name

        Returns:
            package_versions: eg{"22.03":"CUnit-5.3.0"}
        """
        package_versions = {}
        spec_format_url = f"https://gitee.com/src-openeuler/{packagename}/raw/{branch_name}/{packagename}.spec"
        version, release = self.parse_spec_version(spec_format_url)
        version, release = (version, release) if version else ("unknow", "unknow")
        package_versions[packagename] = {branch_name: f"{version}-{release}"}
        return package_versions

    def gitee_package_version(self, branch_name):
        """
        gitee repo package name
        Args:
            branch_name: branch name

        Returns:
            packages_version
        """
        packages_version = dict()
        for packagename in self.pkglist:
            packages_version.update(self.git_package_version(packagename, branch_name))
        return packages_version

    def get_osc_pkg_version(self, pkg_name, project, arch):
        """

        Args:
            pkg_name: package name
            project:  project name
            arch: Compile structure

        Returns:
            version: package version
            release: package release
        """
        version, release = "", ""
        stdout = self.osc_ls_binaries_list(project, pkg_name, arch)
        if not stdout:
            return version, release
        for line in stdout.splitlines():
            if line.strip().endswith(".src.rpm"):
                nvr = line.strip().rsplit(".", 2)[0]
                nvr_list = nvr.rsplit("-", 2)
                version = nvr_list[1] if len(nvr_list) > 1 else ""
                release = (
                    re.split("\.oe\d+", nvr_list[2])[0] if len(nvr_list) > 2 else ""
                )
        return version, release

    def branch_package_version(self, pkg_name, obs_branch):
        """
        Software package information of multiple architectures
        Args:
            pkg_name: pcakage name
            obs_branch: obs project name

        Returns:
             version: version
             release: release
        """
        version, release = "", ""
        for arch in self.repo_arch_map.values():
            version, release = self.get_osc_pkg_version(pkg_name, obs_branch, arch)
            if version:
                return version, release
        return version, release

    def arch_package_version(self, pkg_name, branch_name):
        """
        Obtain the binary package of the software package on OBS,
        and obtain the version and release information of the source code package
        Args:
            pkg_name: package name
            branch_name: branch name

        Returns:
            package_versions: package name version release
        """
        package_versions = {}
        obs_branchs = self.branch_map.get(branch_name)
        main_package_version, main_package_release = self.branch_package_version(
            pkg_name, obs_branchs[0]
        )
        if main_package_version:
            package_versions[pkg_name] = {branch_name: f"{main_package_version}-{main_package_release}"}

        else:
            epol_package_version, epols_package_release = self.branch_package_version(
                pkg_name, obs_branchs[1]
            )
            package_versions[pkg_name] = {branch_name: f"{epol_package_version}-{epols_package_release}"}
        return package_versions

    def obs_package_version(self, branch_name):
        """
        obs package version
        Args:
            branch_name: branch name

        Returns:
            packages_version: package version
        """
        packages_version = dict()
        for pkg_name in self.pkglist:
            packages_version.update(self.arch_package_version(pkg_name, branch_name))
        return packages_version

    def mutil_obs_package(self, obs_project, branch_name):
        """
        Multi-version software package information
        Args:
            obs_project: obs  project
            branch_name: branch name

        Returns:
            mutil packages version release
        """
        mutil_packages_version = dict()
        for pkg_name in self.pkglist:
            package_versions = {}
            package_version, package_release = self.branch_package_version(
                pkg_name, obs_project
            )
            package_versions[pkg_name] = {branch_name: f"{package_version}-{package_release}"}
            mutil_packages_version.update(package_versions)
        return mutil_packages_version

    def run(self, params):
        """
        Check the software package version
        Args:
            params: params

        Returns:
            send data to majun
        """
        self.majun_id, self.pkglist, self.task_title = (
            params.id,
            params.pkglist,
            params.task_title,
        )
        branch_name, _, multi_content = get_product_version(self.task_title)
        if branch_name not in self.branch_map.keys():
            raise ValueError(f"[ERROR]: This branch {branch_name} is not supported")
        if multi_content:
            obs_project = f"{branch_name.replace('-', ':')}:{multi_content}"
            branch_name = OBS_PROJECT_MULTI_VERSION_MAP.get(obs_project)
            if not branch_name:
                raise ValueError(f"[ERROR]: This branch {obs_project} is not supported")
            obs_packages = self.mutil_obs_package(obs_project, branch_name)
        else:
            obs_packages = self.obs_package_version(branch_name)
        gitee_packages = self.gitee_package_version(branch_name)
        _package_dict = dict([(pkg, []) for pkg in self.pkglist])
        for _package, branch_and_version in gitee_packages.items():
            _gitee_package_version = branch_and_version.get(branch_name)
            _obs_package_version = obs_packages.get(_package, {}).get(branch_name)
            if "unknow" not in _gitee_package_version and _gitee_package_version == _obs_package_version:
                compare_result = "same"
            else:
                compare_result = "unknow"
            _package_dict[_package] = compare_result

        return send_content_majun(_package_dict, self.majun_id)
