#! /usr/bin/env python
# coding=utf-8
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
# Origin author：https://gitee.com/gongzt
# Author: https://gitee.com/small_leek
# Create: 2022-03-17
# ******************************************************************************/

import requests
from requests.sessions import Session
from retrying import retry
from fake_useragent import UserAgent
from javcra.libs.log import logger
from javcra.libs.config import global_config


class http:
    """
    http的相关请求
    """

    def __init__(self) -> None:
        self.user_agent = UserAgent(path=global_config.USER_AGENT_JSON)
        self._request = Session()

    def __enter__(self):
        self.set_request(request=self._request)
        return self

    def __exit__(self, *args):
        self._request.close()

    def set_request(self, request):
        """
        set header info

        Args:
            request

        Returns:
        
        """

        request.headers.setdefault("User-Agent", self.user_agent.random)
        return request

    @retry(stop_max_attempt_number=3, stop_max_delay=1500)
    def _get(self, url, params=None, **kwargs):
        response = self._request.request(method="get", url=url, params=params, **kwargs)
        if response.status_code != 200:
            if response.status_code == 410:
                logger.warning("Please check the token!")
            logger.error(response)
            raise requests.HTTPError("")
        return response
    
    @retry(stop_max_attempt_number=3, stop_max_delay=1500)
    def _post(self, url, data, **kwargs):
        response = self._request.request(method="post", url=url, data=data, **kwargs)
        if response.status_code not in [200, 201]:
            logger.error(response)
            raise requests.HTTPError("")
        return response

    @classmethod
    def get(cls, url, params=None, **kwargs):
        """
        get  request

        Args:
            url: url of post request
            params: params of post request
        
        Returns:
            response
        
        """
        
        """http的get请求"""
        with cls() as _self:
            try:
                get_method = getattr(_self, "_get")
                response = get_method(url=url, params=params, **kwargs)
            except requests.HTTPError:
                response = requests.Response()
        return response
    
    @classmethod
    def post(cls, url, data, **kwargs):
        """
        post request

        Args:
            url: url of post request
            data: data of post request

        Returns:
            response
        
        """
        
        with cls() as _self:
            try:
                get_method = getattr(_self, "_post")
                response = get_method(url=url, data=data, **kwargs)
            except requests.HTTPError:
                response = requests.Response()
        return response
