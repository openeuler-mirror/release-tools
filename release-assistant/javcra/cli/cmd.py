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
import os
import sys

ABSPATH = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(os.path.dirname(__file__)))))
sys.path.insert(0, ABSPATH)

from javcra.cli.base import BaseCommand
from javcra.common.exc import Error


def main():
    """
    Description: entrance for all command line

    Raises:
        Error: An error occurred while executing the command
    """
    try:
        for sub_cls in BaseCommand.__subclasses__():
            # get the all subclass of BaseCommand and register the subcommand one by one
            BaseCommand.register_command(sub_cls())
        # add all arguments' attribution into instance
        BaseCommand().args_parser()
    except Error:
        print('Command execution error please try again')


if __name__ == '__main__':
    main()
