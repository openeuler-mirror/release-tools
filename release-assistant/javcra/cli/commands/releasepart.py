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

from javcra.cli.base import BaseCommand
from javcra.application.serialize.validate import validate_giteeid
from javcra.application.releasepart.releaseentrance import ReleaseEntrance
from javcra.common.constant import PERMISSION_DICT


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
        self.add_subcommand_communal_args('release', help_desc="release assistant of release part")
        self.sub_parse.add_argument(
            '--type',
            help='Specify the release check type, only allow checkok and cvrfok',
            action='store',
            choices=['checkok', 'cvrfok']
        )

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
        issue_id = params.releaseIssueID
        gitee_id = params.giteeid
        permission = validate_giteeid(issue_id, gitee_id, PERMISSION_DICT.get(params.type))
        if not permission:
            return

        print("release part", issue_id, gitee_id)
        ReleaseEntrance().release_check()
