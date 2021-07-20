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

from .shell_api_tool import ShellCmdApi, RpmNameParser

class OscApi(ShellCmdApi):
    @staticmethod
    def ls_binaries_list(
        proj,
        pkg,
        repo="standard_aarch64",
        arch="aarch64",
        rt_err=False,
    ):
        """
        get binaries list from obs
        user need to set osc config before use this api
        Args:
            proj: proj
            pkg: pkg
            repo: repo
            arch: arch
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            retult: stdout of `osc ls -b proj pkg repo arch`
        """
        if not proj or not pkg:
            return []
        cmd = f"osc ls -b {proj} {pkg} {repo} {arch}".split()
        return OscApi.call_subprocess(cmd, rt_err)

    @staticmethod
    def get_binaries(
        save_dir, proj, pkg, repo="standard_aarch64", arch="aarch64", rt_err=False
    ):
        """
        download bin rpms from obs
        user need to set osc config before use this api
        Args:
            save_dir: save dir
            proj: proj
            pkg: pkg
            repo: repo
            arch: arch
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            result: stdout of `osc getbinaries proj pkg repo arch --debug -d save_dir`
        """
        if not save_dir:
            save_dir = pkg + "_bin"
        # osc getbinaties will create dir if not exist
        cmd = (
            f"osc getbinaries {proj} {pkg} {repo} {arch} --debug -d {save_dir}".split()
        )
        return OscApi.call_subprocess(cmd, rt_err)

    @staticmethod
    def get_pkg_nvr(
        pkg_name, proj, repo="standard_aarch64", arch="aarch64", rt_err=False
    ):
        """
        parse src.rpm full-name to get package name version release
        Args:
            pkg_name: pkg_name
            proj: proj
            repo: repo
            arch: arch
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            name: name
            ver: ver
            rel: rel
        """
        stdout = OscApi.ls_binaries_list(proj, pkg_name, repo, arch, rt_err)
        name = pkg_name
        ver = ""
        rel = ""
        for line in stdout.splitlines():
            if line.strip().endswith(".src.rpm"):
                rpmver = RpmNameParser(line.strip(), auto_parse=True)
                ver, rel = rpmver.version, rpmver.release # RpmNameParser解析失败日志报错，且version/release失败默认赋值空字符串
        return name, ver, rel

    @staticmethod
    def get_all_bin_name_list(data):
        """
        parse binaries list from [osc ls -b] result
        Args:
            data: data

        Returns:
            result: list of bin rpm name
        """
        if data is None:
            logging.error("input is None, parse name failed")
            return []
        result = []
        for line in data:
            bin_name = RpmNameParser(line, auto_parse=True).name
            if bin_name:
                result.append(bin_name)
        return result

    @staticmethod
    def has_python3_subpkg(pkg_name, proj, rt_err=False):
        """
        has python3 subpkg
        Args:
            pkg_name: pkg_name
            proj: proj
            rt_err: True, return stdout and stderr; False only return stdout

        Returns:
            True or False
        """
        stdout = OscApi.ls_binaries_list(proj, pkg_name, rt_err=rt_err)
        bin_list = OscApi.get_all_bin_name_list(stdout.splitlines())
        for bin_name in bin_list:
            if "python3" in bin_name:
                return True
        return False
