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

import sys
import argparse
from arp.cli.base import BaseCommand
from arp.cli.commands.startprocess import StartProcessCommand

class ReleaseCommand(BaseCommand):
    
    def __init__(self):
        super(ReleaseCommand, self).__init__()


    @classmethod
    def args_parser(cls):
        """
        arguments parser
        """
        cls.register_command(StartProcessCommand())

        args = cls.parser.parse_args()
        args.func(args)

def main():
    try:
        command = ReleaseCommand()
        command.args_parser()
    except Exception:
        print('Command execution error please try again')

