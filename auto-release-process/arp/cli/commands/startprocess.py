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

from collections import namedtuple

from arp.cli.base import BaseCommand
from arp.application.start.startprocess import StartProcess

class StartProcessCommand(BaseCommand):

    def __init__(self):
        super(StartProcessCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            'start', help="start auto release process")
        self.params = [
            self.sub_args('releaseIssueID', 'start release process issue ID', True, 'store', None, None, None),
            self.sub_args('--giteeid', 'the Gitee ID who trigger this command', True, 'store', None, True, None)
        ]

    def register(self):
        super(StartProcessCommand, self).register()
        self.sub_parse.set_defaults(func=self.do_command)

    def do_command(self, params):
        issueID = params.releaseIssueID
        giteeID = params.giteeid
        print("release process", issueID, giteeID)
        StartProcess().get_pkg_list()
