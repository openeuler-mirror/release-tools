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
import argparse
from collections import namedtuple

class BaseCommand():
    parser = argparse.ArgumentParser(description="Automatic Release Tool", prog='oe-art')
    subparsers = parser.add_subparsers(title='command',
                                        help='auto release tool', 
                                        required=True,
                                        dest='subparser_name',
                                        metavar='start|release')

    def __init__(self):
        self.params = []
        self.sub_args = namedtuple('sub_args', ['sub_command', 'help', 'default', 'action', 'nargs', 'required', 'choices'])

    @staticmethod
    def register_command(command):
        command.register()

    def register(self):
        for command_params in self.params:
            if command_params.required:
                self.sub_parse.add_argument(  # pylint: disable=E1101
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action,
                    required=command_params.required)            
            elif command_params.choices:
                self.sub_parse.add_argument(  # pylint: disable=E1101
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action,
                    required=command_params.required,
                    choices=command_params.choices)            
            else:
                self.sub_parse.add_argument(  # pylint: disable=E1101
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action)            
