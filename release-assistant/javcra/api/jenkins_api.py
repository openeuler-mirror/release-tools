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
Description: conver multiple Jenkins restful APIs to python methods
Class:
"""
from collections import defaultdict
import jenkins
from javcra.libs.log import logger
from requests.exceptions import RequestException
from javcra.common.constant import AARCH_FRAME, X86_FRAME, JENKINS_PATH_PREFIX


class JenkinsJob(object):
    """
    conver multiple Jenkins restful APIs to python methods
    """

    def __init__(self, base_url, jenkins_user, jenkins_passwd,
                 paral_num, branch, update_time):
        self.server = jenkins.Jenkins(base_url, username=jenkins_user,
                                      password=jenkins_passwd)
        self.paral_job_num = paral_num
        self.branch = branch
        self.release_date = update_time

    @staticmethod
    def get_path_prefix():
        """
        get the prefix of jenkins job path
        Returns:
            path_prefix
        """
        if not JENKINS_PATH_PREFIX:
            raise ValueError("failed to get jenkins path prefix.")
        return JENKINS_PATH_PREFIX

    def get_base_path(self):
        """
        get base path of parallel jenkins jobs
        Returns:
            base_path
        """
        path_prefix = self.get_path_prefix()
        base_path = path_prefix + "/update_" + self.release_date
        return base_path

    def create_folder(self):
        """
        create folder for jenkins job
        """
        prefix = self.get_path_prefix()
        base_path = self.get_base_path()
        folder_list = [prefix, base_path, base_path + "/" + AARCH_FRAME,
                       base_path + "/" + X86_FRAME]
        
        for folder_name in folder_list:
            # If the folder name already exists, it will not to created
            self.server.create_folder(folder_name, ignore_failures=True)

    def generate_parallel_job_name(self):
        """
        generate the parallel jenkins job name for self-build
        Returns:
            parallel_job_dict: like {"aarch64": [...], "x86": [...]}
        """
        parallel_job_dict = {AARCH_FRAME: [], X86_FRAME: []}
        base_path = self.get_base_path()
        for index in range(1, self.paral_job_num + 1):
            parallel_job_dict[AARCH_FRAME].append(base_path + "/" + AARCH_FRAME + "/" +
                                                  self.branch + "_" + str(index))
            parallel_job_dict[X86_FRAME].append(base_path + "/" + X86_FRAME + "/" +
                                                self.branch + "_" + str(index))
        return parallel_job_dict

    @staticmethod
    def get_job_pkg_dict(packages, jobs):
        """
        get the dict that which jenkins job process which packages
        Args:
            packages: parallel pkgs
            jobs: parallel jobs

        Returns:
            job_pkg_dict
        """
        job_num = len(jobs)
        job_pkg_dict = defaultdict(list)

        for idx, pkg in enumerate(packages):
            job_name = jobs[idx % job_num]
            job_pkg_dict[job_name].append(pkg)
        return job_pkg_dict

    def get_jobs_to_create(self, template_job):
        """
        get the jobs to create according to the template_job
        Args:
            template_job: template job name

        Returns:
            jobs to create, list
        """
        base_path = self.get_base_path()
        paral_job_dict = self.generate_parallel_job_name()

        if "trigger" in template_job:
            return [base_path + "/trigger"]
        elif "aarch64" in template_job:
            return paral_job_dict[AARCH_FRAME]
        elif "x86" in template_job:
            return paral_job_dict[X86_FRAME]
        else:
            raise ValueError("wrong template job name: %s , failed to "
                             "create new jenkins job." % template_job)

    def create_new_job(self, job_name, job_config):
        """
        create new jenkins job

        Args:
            job_name: jenkins job name
            job_config: xml config

        Returns:
            True or False
        """
        try:
            self.server.create_job(job_name, job_config)
            return True
        except jenkins.JenkinsException as err:
            logger.error("failed to create the jenkins job: %s. %s", (job_name, err))
            return False

    def build_jenkins_job(self, job_name, params=None, retry=3):
        """
        build the jenkins job
        Args:
            job_name: name of job
            params: params to build the jenkins job
            retry: default to 3

        Returns:
            queue_item: a queue item number

        """
        try:
            queue_item = self.server.build_job(job_name, params)

            # If the task of build jenkins job fails, then retry
            count = 0
            while not queue_item and count < retry:
                queue_item = self.server.build_job(job_name, params)
                count += 1
                logger.error("failed to build the job: %s, retrying %s." % (job_name, count))
            return queue_item

        except RequestException:
            logger.error("Bad Request for url, please check the job name and parameters for trigger building.")
            return None

    def get_output_hyperlink(self, job_name, build_id):
        """
        convert output url into hyperlinks
        Args:
            job_name: name of jenkins job
            build_id: build id

        Returns:
            hyperlinks of jenkins job output
        """
        job_build_url = self.server.build_job_url(job_name)
        output_hyperlink = None
        try:
            if job_build_url:
                output_url = job_build_url.rsplit('/', 1)[0]
                # convert links into hyperlinks
                output_hyperlink = "[#" + str(build_id) + "](" + output_url + "/" + str(build_id) + "/console)"
        except IndexError:
            logger.error("Error in getting the output url of %s." % job_name)
        return output_hyperlink

    def delete_jenkins_job(self, job_name):
        """
        delete jenkins job according to the job_name
        Args:
            job_name: name of jenkins job

        """
        job_exists = self.server.job_exists(job_name)
        if job_exists:
            self.server.delete_job(job_name)
        else:
            logger.info("when going to delete %s, it is found that the job does not exist" % job_name)
