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

from javcra.cli.base import BaseCommand
from javcra.application.serialize.validate import validate_giteeid
from javcra.application.checkpart.checkentrance import CheckEntrance
from javcra.common.constant import PERMISSION_DICT

class CheckCommand(BaseCommand):
    """
    Description: start the check part
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(CheckCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            'check', help="release assistant of check part")
        self.add_issueid_arg()
        self.add_giteeid_arg()
        self.sub_parse.add_argument(
            '--type',
            help='the type of check part, \
                including cve, bugfix, requires, issue status and test result',
            action='store',
            nargs=None,
            required=True,
            choices=['cve', 'bug', 'status', 'requires', 'test']
            )

        self.sub_parse.add_argument(
            '--result',
            help='the check result, it would be yes or no',
            default='yes',
            action='store',
            nargs=None,
            required=False,
            choices=['yes', 'no']
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

        type_status = params.result
        type_dict = {
            'cve': CheckEntrance(issue_id, type_status).check_pkglist_result,
            'bug': CheckEntrance(issue_id, type_status).check_pkglist_result,
            'status': CheckEntrance(issue_id, type_status).check_issue_status,
            'requires': CheckEntrance(issue_id, type_status).check_requires,
            'test': CheckEntrance(issue_id, type_status).check_test_result
        }

        print("check part start", issue_id, gitee_id)
        type_dict.get(params.type)()
