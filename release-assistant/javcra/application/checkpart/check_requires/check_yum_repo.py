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
# Author: DisNight
# Create: 2021-06-29
# ******************************************************************************/

import unittest
import sys

from javcra.application.checkpart.check_requires import init_env
from dnf.cli import main

# need to install osc command rpm `dnf install osc`


class YumRepoChecker(unittest.TestCase):
    """
    use dnf command `dnf makecache --config xxx.repo` to verify yum repo file
    """

    DNF_SUCCEED_RTCODE = 0

    def _test_yum_repo(self, branch: str, predict: int) -> None:
        """
        use dnf command `dnf makecache --config xxx.repo` to verify yum repo file

        Attributes:
            pkg_list: source rpm list
            published_repos: published repo name list in /etc/yum.repo.d/xxx.repo (repo.openuler.org/xxx etc.)
            dev_repos: develop repo name list in /etc/yum.repo.d/xxx.repo (obs.repo/xxxx etc.)
            branch: branch in obs proj such as (openEuler:20.03:LTS:SP1, openEuler:20.03:LTS:SP1:EPOL, etc.)

        return:
            pkg_dict = {
                src_rpm: [bin_rpm],
                ...
            }
        """
        repo_file = init_env.get_yum_repo_file(branch, init_env.OPENEULER_BRANCH_MAP)
        exit_code = main.user_main(
            ["--config", repo_file, "makecache"], exit_code=False
        )
        sys.modules.clear()
        self.assertEqual(exit_code, predict)

    def test_oe2003lts_yum_repo(self):
        self._test_yum_repo("openEuler-20.03-LTS", self.DNF_SUCCEED_RTCODE)

    def test_oe2003ltssp1_yum_repo(self):
        self._test_yum_repo("openEuler-20.03-LTS-SP1", self.DNF_SUCCEED_RTCODE)
        
    def test_oe2003ltssp2_yum_repo(self):
        self._test_yum_repo("openEuler-20.03-LTS-SP2", self.DNF_SUCCEED_RTCODE)
        
    def test_oe2003ltssp3_yum_repo(self):
        self._test_yum_repo("openEuler-20.03-LTS-SP3", self.DNF_SUCCEED_RTCODE)


if __name__ == "__main__":
    suite = unittest.makeSuite(YumRepoChecker)
    unittest.TextTestRunner().run(suite)
