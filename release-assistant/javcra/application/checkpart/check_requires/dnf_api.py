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
# Author: Jiachen Fan
# Create: 2021-7-13
# ******************************************************************************/

import logging
import os

from .shell_api_tool import ShellCmdApi, RpmNameParser

class DnfApi(ShellCmdApi):
    @staticmethod
    def generate_repo_condition(repo_list):
        """
        generate dnf repo condition
        Args:
            repo_list: repo_list

        Returns:
            repo_cmd: ["--repo", repo_name, ...]
        """
        if not repo_list:
            return []
        repo_cmd = []
        for repo in repo_list:
            repo_cmd.extend(["--repo", repo])
        return repo_cmd

    @staticmethod
    def generate_repo_file_condition(repo_file):
        """
        generate dnf repo file condition
        Args:
            repo_file: repo_file

        Returns:
            repo_file_cmd = ["-c", repo_file, ...]
        """
        if not repo_file or not os.path.exists(repo_file):
            return []
        return ["-c", repo_file]

    @staticmethod
    def get_pkg_version(pkg_name, repos=None, repo_file=None, rt_err=False):
        """
        use command [dnf list (--repo repo_name)* | grep pkg_name.src] to get [e:v-r] format version
        return epoch, version, release
        Args:
            pkg_name: pkg_name
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            epoch: epoch
            version: version
            release: release
        """
        cmd = ["dnf", "list"]
        repo_condition = DnfApi.generate_repo_condition(repos)
        cmd.extend(repo_condition)
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend(["|", "grep", f"{pkg_name}.src"])
        
        stdout = DnfApi.call_subprocess(cmd, rt_err)
        release = ""
        epoch = "0"
        for line in stdout.splitlines(False):
            if not line:
                continue
            pkg_info = line.split()
            if len(pkg_info) != 3: # `dnf list` result: <rpm_name> <full-ver> <repo> has 3 attribute
                continue
            # pkg_info[1] -> <full-ver> -> <version>-<release>.<dist>
            # pkg_info[1].rsplit(".", 1) -> [<version>-<release>, <dist>]
            # pkg_info[1].rsplit(".", 1)[0] -> <version>-<release>
            ver_info = pkg_info[1].rsplit(".", 1)[0]
            [epoch, version, release] = RpmNameParser.parse_rpm_evr(ver_info)
        return [epoch, version, release]

    @staticmethod
    def download(down_dir, bin_name, repos=None, repo_file=None, rt_err=False):
        """
        download rpms by dnf download need upgrade yum
        Args:
            down_dir: down_dir
            bin_name: bin_name
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: stdout of `dnf download bin_name --downloaddir=down_dir`
        """
        if not down_dir:
            logging.error("Failed to donwnload rpm, down_dir is None!")
            return ""
        if not os.path.exists(down_dir): 
            os.makedirs(down_dir)
        cmd = ["dnf", "download"]
        repo_condition = DnfApi.generate_repo_condition(repos)
        cmd.extend(repo_condition)
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend([bin_name, f"--downloaddir={down_dir}"])
        return DnfApi.call_subprocess(cmd, rt_err)

    @staticmethod
    def get_info_grep_by_key(bin_name, key, repos=None, repo_file=None, rt_err=False):
        """
        grep dnf info source field to get src name of bin rpm
        Args:
            bin_name: bin_name
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: stdout of `dnf info bin_name | grep key`
        """
        cmd = ["dnf", "info"]
        repo_condition = DnfApi.generate_repo_condition(repos)
        cmd.extend(repo_condition)
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend([bin_name, "|", "grep", key])
        return DnfApi.call_subprocess(cmd, rt_err)

    @staticmethod
    def find_what_requires(bin_name, repos=None, repo_file=None, rt_err=False):
        """
        find install bedepended of bin rpm
        Args:
            bin_name: bin_name
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: list of bin rpm name
        """
        cmd = ["dnf", "repoquery"]
        repo_condition = DnfApi.generate_repo_condition(repos)
        cmd.extend(repo_condition)
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend(["--nvr", "--whatrequires", bin_name])
        stdout = DnfApi.call_subprocess(cmd, rt_err)
        data = stdout.split("\n")
        result_set = set()
        for element in data:
            if not element.strip():
                continue
            name = element.strip()
            result_set.add(name)
        return list(result_set)

    @staticmethod
    def find_update_install_rpms(
        pkg_name, rpm_dir, repos=None, repo_file=None, rt_err=False
    ):
        """
        find all install requires which need update
        Args:
            pkg_name: pkg_name
            rpm_dir: rpm_dir
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: list of bin rpm name
        """
        if not os.path.isdir(rpm_dir) or not repos:
            logging.warning(f"localdir: [{rpm_dir}] or repos: [{repos}] is None")
            return set()
        install_rpms = os.path.abspath(rpm_dir) + "/*"
        repo_name = repos[0]
        cmd = ["dnf", "install"]
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend([install_rpms, "--assumeno", "|", "grep", repo_name])
        stdout = DnfApi.call_subprocess(cmd, rt_err)
        data = stdout.split("\n")
        result = set()
        logging.info("finding %s installed requires", pkg_name)
        for line in data:
            if not repo_name in line:
                continue
            bin_name = line.strip().split()[0]
            logging.info("[%s] install require [%s] need update", pkg_name, bin_name)
            result.add(bin_name)
        return result

    @staticmethod
    def is_dnf_install_succeed(pkg_name, repos=None, repo_file=None, rt_err=True):
        """
        use dnf install pkg --assumeno to judeg repos' complete
        Args:
            pkg_name: pkg_name
            repos: repos
            repo_file: repo_file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            True or False
        """
        cmd = ["dnf", "install"]
        repo_condition = DnfApi.generate_repo_condition(repos)
        cmd.extend(repo_condition)
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        cmd.extend([pkg_name, "--assumeno"])

        stdout = DnfApi.call_subprocess(cmd, rt_err)
        if "Dependencies resolved" in stdout:
            return False
        return True

    @staticmethod
    def get_all_repolist(repo_file=None, rt_err=False):
        """
        get all set repo in /etc/yum.repo.d/*.repo
        Args:
            repo_file: path of repo file
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: list of repo name
        """
        cmd = ["dnf", "repolist", "--all"]
        repo_file_condition = DnfApi.generate_repo_file_condition(repo_file)
        cmd.extend(repo_file_condition)
        stdout = DnfApi.call_subprocess(cmd, rt_err)
        data = stdout.split("\n")
        result = set()
        if len(data) > 1:
            for line in data[1:]:
                if not line.strip():
                    continue
                result.add(line.strip().split()[0].strip())
        return result
