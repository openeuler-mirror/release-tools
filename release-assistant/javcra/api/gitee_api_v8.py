#!/usr/bin/python3
#******************************************************************************
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
This is a helper script for working with gitee.com
"""
import os
import stat
import sys
import json
import yaml
from javcra.libs.log import logger
from javcra.common import constant
from javcra.libs.config import global_config
from javcra.libs.http_base import http


class GiteeAPI(object):
    """
    Gitee is a helper class to abstract gitee.com api
    """
    R_FLAG = os.O_RDONLY
    R_MODES = stat.S_IRUSR
    W_FLAG = os.O_WRONLY | os.O_CREAT
    W_MODES = stat.S_IWUSR | stat.S_IRUSR

    def __init__(self, enterprise, version):
        """
        Initialization

        Args:
            enterprise: id of enterprise
            version: version of gitee api
        
        Returns:
        
        """
        
        self._enterprise = enterprise
        self._api_version = version
        self._token = ''
        self._issue_type = dict()

        gitee_config_path = os.path.expanduser(global_config.GITEE_API_CONFIG)
        if os.path.exists(gitee_config_path):
            try:
                with os.fdopen(os.open(gitee_config_path, self.R_FLAG, self.R_MODES), "r") as fout:
                    yaml_data = yaml.safe_load(fout)
                    self._token = yaml_data['access_token']
                    self._issue_type = yaml_data['gitee_api_common_id']['issue_type']
            except (TypeError, KeyError) as err:
                logger.error(f"target: access_token / gitee_api_common_id NOT FOUND!")
        else:
            logger.error(f"{gitee_config_path} is not exist")

    def _post_gitee(self, url, data):
        """
        Post new issue

        Args:
            url: url of post request
            data: data of post request

        Returns:
            dict_resp

        """

        dict_resp = dict()
        response = http.post(url, data)
        if response.status_code != 200 and response.status_code != 201:
            logger.warning(f"post {data} to {url} failed: {response.status_code}")
            return dict_resp
        
        if response.content:
            try:
                dict_resp = json.loads(response.content)
            except json.JSONDecodeError:
                logger.error("Unexpected UTF-8 BOM (decode using utf-8-sig)")
            except json.TypeError:
                logger.error("the json object must be str, bytes or bytearray")
            
        return dict_resp
    
    def get_gitee_json(self, url):
        """
        get and load gitee json response

        Args:
            url: url of get request
        
        Returns:
            json_resp
        
        """
        
        json_resp = []
        resp = self._get_gitee(url)
        if resp:
            try:
                json_resp = json.loads(resp)
            except json.JSONDecodeError:
                logger.error("Unexpected UTF-8 BOM (decode using utf-8-sig)")
            except json.TypeError:
                logger.error("the json object must be str, bytes or bytearray")
            
        return json_resp
        
    def _get_gitee(self, url):
        """
        get data from url

        Args:
            url: url of get request
        
        Returns:
        
        """
        
        response = http.get(url)
        if response.status_code != 200:
            logger.warning(f"get data form {url} failed: {response.status_code}")
            return None
        return response.content

    def get_gitee_dict(self, url, param, with_token = True):
        """
        get data of dictionary from gitee api

        Args:
            url: url: url of get request
            param: parameters
            with_token: token of request
        
        Returns:
            dict_resp

        """
        
        dict_resp = dict()
        final_params = []
        final_url = url
        if param is not None:
            for key, value in param.items():
                final_params.append(f'{key}={value}')
        if with_token:
            final_params.append(f'access_token={self._token}')
            
        params = '&'.join(final_params)
        final_url = final_url + params
        dict_resp = self.get_gitee_json(final_url)
        return dict_resp

    def get_enterprise_target_id(self, target, target_key, search):
        """
        get target id from enterprise

        Args:
            target: projects/milestones/members
            target_key: the key of dict data from api
            search: Keywords provided to narrow the query scope

        Returns:
        
        """

        target_id = 'NA'
        url = f"https://api.gitee.com/enterprises/{self._enterprise}/{target}?"
        para = {"search":search}
        pkgs_info = self.get_gitee_dict(url, para)
        
        try:
            pkgs_info_data = pkgs_info['data']
            for data in pkgs_info_data:
                if data[target_key] == search:
                    return data['id']
        except (TypeError, KeyError) as err:
            logger.error(f"target: {search} NOT FOUND!")
        return target_id


    def get_openeuler_member_id(self, gitee_username):
        """
        get id of member of openeuler

        Args:
            gitee_username: gitee username
        
        Returns:
            gitee_user_id: id of gitee_username
        
        """
        if not os.path.exists(global_config.GITEE_OPENEULER_MEMBERS_ID_YAML):
            logger.warning(f"local {global_config.GITEE_OPENEULER_MEMBERS_ID_YAML} not exist")
        else:
            with os.fdopen(os.open(global_config.GITEE_OPENEULER_MEMBERS_ID_YAML, self.R_FLAG, self.R_MODES), "r") as fout:
                yaml_data = yaml.safe_load(fout)
                try:
                    for key, value in yaml_data.items():
                        if key == gitee_username:
                            return value['id']
                except KeyError as err:
                    logger.warning(f"local {global_config.GITEE_OPENEULER_MEMBERS_ID_YAML} no found: {gitee_username}")

        return self.get_enterprise_target_id('members', 'username', gitee_username)

    def refresh_openeuler_member_ids(self):
        """
        refresh all members's ids and write to yaml

        Args:
        
        Returns:
        
        """

        api_url = f'https://api.gitee.com/enterprises/{self._enterprise}/members?'
        members_info = dict()
        members = self.get_gitee_dict(api_url, None)
        members_data = []
        try:
            members_data = members['data']
        except KeyError as err:
            logger.error(f"Refresh {global_config.GITEE_OPENEULER_MEMBERS_ID_YAML} failed: {err}")
            return

        for data in members_data:
            try:
                member_user = data['username']
                members_info[member_user] = {'id':data['id'], 'email':data['email']}
            except KeyError as err:
                logger.error(f"Refresh {global_config.GITEE_OPENEULER_MEMBERS_ID_YAML} failed: {err}")
                return

        with os.fdopen(os.open(global_config.GITEE_OPENEULER_MEMBERS_ID_YAML, self.W_FLAG, self.W_MODES), "w") as fout:
            yaml.dump(members_info, fout)
        
        logger.info(f"Refresh {global_config.GITEE_OPENEULER_MEMBERS_ID_YAML} finshed!")


    def get_issue_type_id(self, issue_type):
        """
        get id of specific issue type

        Args:
            issue_type: the type of issue
        
        Returns:
            issue_type_id
        
        """
        
        issue_type_id = self._issue_type.get(issue_type, 'NA')
        if issue_type_id == 'NA':
            try:
                logger.warning(f"{issue_type} is invalid")
                return self._issue_type['bug']
            except KeyError as err:
                logger.error(f"target: issue_type NOT FOUND! {err}")
        return issue_type_id
        

    def get_issues(self, milestone, author = None):
        """
        get issues info

        Args:
            milestone: milestone name
            author: the author of issue

        Returns:
        
        """

        zero_issue = 'NA'
        api_url = f"https://api.gitee.com/enterprises/{self._enterprise}/issues?"
        milestone_id = self.get_enterprise_target_id('milestones', 'title', milestone)
        if milestone_id == 'NA':
            return zero_issue
        author_id = self.get_openeuler_member_id(author)
        if author_id == 'NA':
            paras = {"milestone_id":milestone_id}
        else:
            paras = {"milestone_id":milestone_id, 'author_id':author_id}
        issues_dict = self.get_gitee_dict(api_url, paras)
        zero_issue = issues_dict['data']
        return zero_issue

    def create_issue(self, package, mile_stone, issue_type, assignee, parameters):
        """
        Create issue under the specified package in gitee

        Args:
            package: package name
            mile_stone: milestone name
            issue_type: the type of issue
            assignee: maintainer name
            parameters: optioanl parameters
        Returns:
        
        """
        
        issue_url = 'NA'
        url = f"https://api.gitee.com/enterprises/{self._enterprise}/issues"
        package_id = self.get_enterprise_target_id('projects', 'name', package)
        if package_id == 'NA':
            logger.warning(f"No package_id found for {package}")
            return issue_url
        milestone_id = self.get_enterprise_target_id('milestones', 'title', mile_stone)
        if milestone_id == 'NA':
            logger.warning(f"No milestone_id found for {mile_stone}")
            return issue_url
        assignee_id = self.get_openeuler_member_id(assignee)
        if assignee_id == 'NA':
            logger.warning(f"No assignee_id found for {assignee}")
            return issue_url
        issue_type_id = self.get_issue_type_id(issue_type)
        if issue_type_id == 'NA':
            logger.warning(f"No issue_type_id found for {issue_type}")
            return issue_url
        
        necessary_paras = dict()
        necessary_paras["access_token"] = self._token
        necessary_paras['project_id'] = package_id
        necessary_paras['milestone_id'] = milestone_id
        necessary_paras['issue_type_id'] = issue_type_id
        necessary_paras['assignee_id'] = assignee_id

        parameters.update(necessary_paras)
        logger.info(parameters)

        result = self._post_gitee(url, parameters)
        try:
            issue_url = result['issue_url']
        except KeyError as ke:
            logger.error(f'No valid issue_url return')
        return issue_url