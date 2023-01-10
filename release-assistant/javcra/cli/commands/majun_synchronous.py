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
from javcra.cli.base import BaseCommand
from javcra.application.majun.majun_operate import MajunOperate


class MajunSynchronousCommand(BaseCommand):
    """
    Description: start the release assistant
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(MajunSynchronousCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            "majunsync", help="updateinfo synchronization and cvrf synchronization"
        )
        self.sub_parse.add_argument(
            "--choice",
            type=str,
            help="synchronous data platform",
            action="store",
            required=True,
            choices=["cvrf", "updateinfo", "all"],
        )
        self.sub_parse.add_argument(
            "--jenkinsuser",
            type=str,
            help="provide your jenkinsuser",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--jenkinskey",
            type=str,
            help="provide your jenkins key",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--server",
            type=str,
            help="The distribution store background background",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--bucketname",
            type=str,
            help="name of the bucket where the object is stored",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--cvrffilename",
            type=str,
            help="directory file name",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--updatefilename",
            type=str,
            help="directory file name",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--ipaddr",
            type=str,
            help="IP address of the publishing machine",
            action="store",
            required=False,
        )
        self.sub_parse.add_argument(
            "--id",
            type=str,
            help="uuid",
            action="store",
            required=True,
        )

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """

        check_majun = MajunOperate()
        check_majun.synchronous_info(params)
