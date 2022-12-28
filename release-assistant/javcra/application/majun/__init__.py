#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/


import datetime
import json
import os
import re
from enum import Enum, unique
from functools import wraps
import requests
from javcra.common.constant import MAJUN_CALLBACK_URL, BRANCH_LIST
from javcra.libs.log import logger


@unique
class MessageCode(Enum):
    SUCCESS_MESSAGE = "Operation succeeded"
    FAILURE_MESSAGE = "Operation failed"
    SUCCESS_CODE = "200"
    FAILED_CODE = "400"


def combine_content(content, majun_id, multip_start):
    """
    jenkins run result
    Args:
        content: jenkins run result
        majun_id: majun id
        multip_start: Whether to enable the multi-version start function
    Returns:
        content_dic: Send a combination of Majun's data
    """
    content_dic = {"data": content, "id": majun_id}
    if any([content, multip_start]):
        content_dic.update({"code": MessageCode.SUCCESS_CODE.value, "msg": MessageCode.SUCCESS_MESSAGE.value})
    else:
        content_dic.update({"code": MessageCode.FAILED_CODE.value, "msg": MessageCode.FAILURE_MESSAGE.value})
    return content_dic


def send_content_majun(content, majun_id, multip_start=False):
    """
    jenkins result sent to majun
    Args:
        content: Data sent to majun
        majun_id: majun id
        multip_start: Whether to enable the multi-version start function
    Returns:
        Sending data Results
    """
    new_content = combine_content(content, majun_id, multip_start)
    heard = {"access_token": os.getenv("majun_access_token")}
    try:
        resp = requests.post(
            url=MAJUN_CALLBACK_URL, data=json.dumps(new_content), headers=heard
        )
    except requests.RequestException as error:
        logger.error(f"Failed to send data, because {error}")
        return False
    if resp.status_code == requests.codes.ok:
        logger.info(f"The {new_content} data sent to majun was successful")
        return True
    return False


def get_product_version(task_title):
    """
    Parse the key information in the task name
    Args:
        task_title: Task Name

    Returns:
        branch_name: git branch name
        release_date: Version schedule date
        multi_content: Multiple versions of the specific information

    """
    base_re_str = r"^(.+)_([a-zA-Z]+)(\d+)"

    if "Multi" in task_title:
        re_content = re.compile(f"{base_re_str}_(.+)", re.MULTILINE).search(
            task_title
        )
        branch_name, release_date, multi_content = (
            re_content.group(1),
            re_content.group(3),
            re_content.group(4),
        )
    else:
        re_content = re.compile(base_re_str, re.MULTILINE).search(task_title)
        branch_name, release_date = (
            re_content.group(1),
            re_content.group(3),
        )
        multi_content = None
    if branch_name not in BRANCH_LIST:
        raise ValueError(f"This branch {branch_name} is not supported yet")
    if release_date.isdigit():
        freeze_date = (
                datetime.datetime.strptime(release_date, "%Y%m%d")
                + datetime.timedelta(days=2)
        ).strftime("%Y%m%d")

    else:
        re_release_date = re.compile(r"(\d+)(\D+)", re.MULTILINE).search(release_date)
        new_update_time, temporary_str = re_content.group(1), re_release_date.group(2)
        freeze_date = (datetime.datetime.strptime(new_update_time, "%Y%m%d") +
                       datetime.timedelta(days=2)).strftime(
            "%Y%m%d") + temporary_str
    return branch_name, freeze_date, multi_content


def catch_majun_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        """
        capture decorator
        """
        _, params = args
        try:
            if not os.getenv("majun_access_token"):
                raise ValueError(
                    "Failed to obtain the majun access token value."
                    "Please check the Settings of jenkins engineering environment variables"
                )
            return func(*args, **kwargs)
        except (
                ValueError,
                AttributeError,
                KeyError,
                TypeError,
                FileNotFoundError,
                IndexError
        ) as err:
            logger.error(f"repo {err}")
            return send_content_majun(False, params.id)

    return inner

