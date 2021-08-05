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
The cloud downloads the file and reads the data inside
"""

import os
import shutil
import uuid

import pandas as pd

from javcra.api.obscloud import ObsCloud
from javcra.common.constant import CVE_MANAGE_BUCKET_NAME
from javcra.common.constant import CVE_MANAGE_SERVER
from javcra.common.constant import CVE_UPDATE_INFO
from javcra.libs.log import logger


def read_excel_xlsx(curr_path):
    """
    to read excel file content
    Args:
        curr_path: curr_path
    Returns:

    """
    df = pd.read_excel(curr_path, sheet_name="cve_list")
    df.fillna("", inplace=True)
    df_list = []
    for i in df.index.values:
        df_line = df.loc[i, ['cve编号', 'issue编号', 'issue所属仓库',
                             'score', "version", "abi是否变化"]].to_dict()
        df_list.append(df_line)
    out_list = []
    for data_dict in df_list:
        df_dict = {
            "CVE": "#" +
                   data_dict.get("issue编号") +
                   ":" +
                   data_dict.get("cve编号"),
            "abi是否变化": data_dict.get("abi是否变化"),
            "score": data_dict.get("score"),
            "version": data_dict.get("version"),
            "仓库": data_dict.get("issue所属仓库"),
            "status": "已完成",
        }
        out_list.append(df_dict)

    return out_list


def download_file(now_time, file_name):
    """
    download file content
    Args:
        now_time: now_time
        file_name: file_name
    Returns:
        cve_list:
    """
    file_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    temp_path = os.path.join(file_path, "tmp{}".format(str(uuid.uuid1().hex)))
    try:
        obs_client = ObsCloud(os.getenv("ak"), os.getenv("sk"), CVE_MANAGE_SERVER, CVE_MANAGE_BUCKET_NAME)
        # Determine whether the file to be downloaded is in the object of the bucket
        files = obs_client.bucket_list("{}/{}".format(CVE_UPDATE_INFO, now_time))
        file_object = ""
        for file in files:
            if "{CVE_UPDATE_INFO}/{date}/{title}".format(
                    CVE_UPDATE_INFO=CVE_UPDATE_INFO, date=now_time, title=file_name) == file:
                file_object = file
        if not file_object:
            logger.error("The object does not exist in the bucket")
            return []
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        file_path = os.path.join(temp_path, 'Temporary_Files.xlsx')

        # The download file
        res = obs_client.down_load_file(file_object, file_path)
        if not res:
            logger.error("The object does not exist in the bucket %s" % file_path)
            return []

        # Read the file contents in Excel
        cve_list = read_excel_xlsx(file_path)
        return cve_list
    except (OSError, FileNotFoundError) as error:
        logger.error(error)
        return []
    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
