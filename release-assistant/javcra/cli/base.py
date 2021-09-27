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

    def add_subcommand_communal_args(self, sub_command, help_desc):
        """
        Description: add subcommand with releaseIssueID and gitee ID and token as sub_parse argument
        Args:

        Returns:

        Raises:

        """
        self.sub_parse = BaseCommand.subparsers.add_parser(
            sub_command, help=help_desc)

        self.sub_parse.add_argument(
            'releaseIssueID',
            help='start release issue ID',
            action='store'
        )
        self.sub_parse.add_argument(
            '--giteeid',
            help='the Gitee ID who trigger this command',
            action='store',
            required=True
        )
        self.sub_parse.add_argument(
            "--token",
            type=str,
            help="a valid GiteeToken value",
            action="store",
            required=True,
        )

    def add_obs_ak_arg(self):
        """
        Description: add obs ak into sub_parse argument
        """

        self.sub_parse.add_argument(
            "--ak",
            type=str,
            help="provide your access key",
            action="store",
            required=True,
        )

    def add_obs_sk_arg(self):
        """
        Description: add obs ak into sub_parse argument
        """

        self.sub_parse.add_argument(
            "--sk",
            type=str,
            help="provide your secret key",
            action="store",
            required=True,
        )

    @staticmethod
    def create_comment(type_res, result, issue):
        """
        create comment for jenkins job
        """
        if not result:
            raise ValueError("%s: No comment information. The content is:  %s." % (type_res, result))

        comment_res = issue.create_jenkins_comment(result)
        if not comment_res:
            print("[ERROR] failed to create %s" % type_res)
        else:
            print("[INFO] successfully create %s" % type_res)

    @staticmethod
    def get_release_info(issue):
        branch_name = issue.get_update_issue_branch()
        if not branch_name:
            raise ValueError("failed to get branch name.")

        update_pkgs = issue.get_update_list()
        if not update_pkgs:
            raise ValueError("failed to get obs_pkgs.")

        release_date = issue.get_release_time()
        if not release_date:
            raise ValueError("can not get the release time, please check.")

        return branch_name, update_pkgs, release_date

    @staticmethod
    def register_command(command):
        """
        Description: Registration of commands

        Args:
            command: commands for javcra

        Returns:
        Raises:

        """
        command.sub_parse.set_defaults(func=command.do_command)

    @classmethod
    def args_parser(cls):
        """
        Description: argument parser
        Args:

        Returns:

        Raises:

        """
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
