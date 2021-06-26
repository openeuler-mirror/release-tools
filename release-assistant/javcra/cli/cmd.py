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
Description: register method for all commands
Class: JavcraCommand
"""

from javcra.cli.base import BaseCommand
from javcra.common.exc import Error
from javcra.cli.commands.startpart import StartCommand

class JavcraCommand(BaseCommand):
    """
    Description: Javcra command line
    Attributes:
        statistics: Summarized data table
        table: Output table
        columns: Calculate the width of the terminal dynamically
        params: Command parameters
    """

    @classmethod
    def args_parser(cls):
        """
        Description: argument parser
        Args:

        Returns:

        Raises:

        """
        cls.register_command(StartCommand())

        args = cls.parser.parse_args()
        args.func(args)


def main():
    """
    Description: entrance for all command line

    Raises:
        Error: An error occurred while executing the command
    """
    try:
        command = JavcraCommand()
        command.args_parser()
    except Error:
        print('Command execution error please try again')
