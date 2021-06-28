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
Description: Base method for custom commands
Class: BaseCommand
"""

import argparse
from collections import namedtuple
from abc import abstractmethod

class BaseCommand():
    """
    Description: Basic attributes used for command invocation
    Attributes:
        params: Command line parameters
        subparsers: Subcommand parameters
        sub_args: namedtuple for generating subcommand parameters
    """

    parser = argparse.ArgumentParser(
        description="Just A Very Convenient Release Assistant", prog='javcra')
    subparsers = parser.add_subparsers(title='command',
                                       help='Just A Very Convenient Release Assistant',
                                       required=True,
                                       dest='subparser_name',
                                       metavar='start')

    def __init__(self):
        """
        Description: Instance initialization
        """
        self.params = []
        self.sub_parse = None
        self.sub_args = namedtuple(
            'sub_args',
            ['sub_command', 'help', 'default', 'action', 'nargs', 'required', 'choices']
            )

    @staticmethod
    def register_command(command):
        """
        Description: Registration of commands

        Args:
            command: commands for javcra

        Returns:
        Raises:

        """
        command.register()
        command.sub_parse.set_defaults(func=command.do_command)

    def register(self):
        """
        Description: Command line parameter registered
        Args:

        Returns:

        Raises:

        """
        for command_params in self.params:
            if command_params.required:
                self.sub_parse.add_argument(
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action,
                    required=command_params.required)
            elif command_params.choices:
                self.sub_parse.add_argument(
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action,
                    required=command_params.required,
                    choices=command_params.choices)
            else:
                self.sub_parse.add_argument(
                    command_params.sub_command,
                    help=command_params.help,
                    default=command_params.default,
                    action=command_params.action)

    @classmethod
    def args_parser(cls):
        """
        Description: argument parser
        Args:

        Returns:

        Raises:

        """
        for sub_cls in cls.__subclasses__():
            cls.register_command(sub_cls())

        args = cls.parser.parse_args()
        args.func(args)

    @abstractmethod
    def do_command(self, params):
        """
        Description: Method which wound need to be implemented by subcommands

        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
