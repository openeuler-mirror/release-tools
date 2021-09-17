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
import math
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from functools import wraps
import gevent
import jenkins
from gevent import monkey

monkey.patch_all(ssl=False)
from requests.exceptions import RequestException
from javcra.libs.log import logger
from javcra.common.constant import AARCH_FRAME
from javcra.common.constant import X86_FRAME
from javcra.common.constant import JENKINS_PATH_PREFIX
from javcra.common.constant import TRIGGER_TM_JOB
from javcra.common.constant import AARCH64_TM_JOB
from javcra.common.constant import X86_TM_JOB
from javcra.common.constant import ACTUATOR_DICT


def catch_jenkins_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        """
        capture decorator
        """
        try:
            return func(*args, **kwargs)
        except RequestException as err:
            logger.error("error occurred when requesting: %s" % err)
        except (jenkins.JenkinsException, jenkins.NotFoundException) as err:
            logger.error("error occurred of jenkins: %s" % err)
        except (RequestException, ValueError, AttributeError, KeyError, TypeError) as err:
            logger.error("error in processing jenkins data: %s" % err)
        return False

    return inner


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

    @staticmethod
    def update_trigger_config(config_root, parallel_jobs):
        """
        update the config of trigger job
        trigger config script demo: parallel(
                                        'self_build_0': { build job: '1', propagate: false},
                                        )
        Args:
            config_root: config of template job
            parallel_jobs: parallel jobs
        Returns:
            root

        """
        # modify the setting of trigger by changing the script
        ele_cmd = config_root.find("definition/script")
        if ele_cmd is None:
            logger.error("failed to get script of trigger job.")
            return None

        script = ele_cmd.text
        script_lines = script.splitlines()
        start_index = None
        end_index = None

        for idx, line in enumerate(script_lines):
            # find the start and the end of setting
            if line.strip() == "parallel(":
                start_index = idx
            if start_index and line.strip() == ")":
                end_index = idx
            if start_index and end_index:
                break

        if not all([start_index, end_index]):
            return None

        new_script_lines = []
        new_script_lines.extend(script_lines[:start_index + 1])

        job_num = len(parallel_jobs)
        for idx, job in enumerate(parallel_jobs):
            job_str = "\'self_build_" + str(idx) + "\': { build job: \'" + job + "\', propagate: false}"
            if idx != job_num - 1:
                job_str = job_str + ","
            new_script_lines.append(job_str)

        new_script_lines.extend(script_lines[end_index:])
        new_script = "\n".join(new_script_lines)
        ele_cmd.text = new_script
        return config_root

    def update_paral_job_config(self, root_config, pkg_job_dict, target_job):
        """
        update the config of parallel job
        Args:
            root_config: config of template job
            pkg_job_dict: dict of jenkins jobs and pkgs
            target_job: target job

        Returns:
            root: parallel job config
        """
        # modify parallel job config according to template job
        ele_cmd = root_config.find("properties/hudson.model.ParametersDefinitionProperty//parameterDefinitions")
        actuator = root_config.find("assignedNode")

        if ele_cmd is not None and actuator is not None and pkg_job_dict.get(target_job):
            for node in ele_cmd:
                verify_pkgs = ",".join(pkg_job_dict.get(target_job))
                key = node.find('name').text
                if key == "PKG_NAME":
                    node.find('defaultValue').text = verify_pkgs
                elif key == "UPDATE_TIME":
                    node.find('defaultValue').text = self.release_date
                elif key == "BRANCH":
                    node.find('defaultValue').text = self.branch

            # Assign actuators according to different frames and branches
            if AARCH_FRAME in target_job:
                actuator.text = "k8s-" + AARCH_FRAME + "-" + ACTUATOR_DICT[self.branch]
            else:
                actuator.text = "k8s-x86-" + ACTUATOR_DICT[self.branch]

            return root_config
        else:
            logger.error("failed to get parameter definition of parallel job.")
            return None

    def update_config(self, target_job, template_job_config, packages):
        """
        update config for trigger、aarch64、x86 jenkins job
        Args:
            target_job: target jenkins job to create
            template_job_config: template jenkins job
            packages: packages

        Returns:
            root or None

        """
        paral_job_dict = self.generate_parallel_job_name()
        root = ET.fromstring(template_job_config.encode("utf-8"))
        if root:
            # modify the setting of trigger
            if "trigger" in target_job:
                # get all the parallel jobs which include "aarch64、x86"
                paral_jobs = []
                paral_jobs.extend(paral_job_dict[AARCH_FRAME])
                paral_jobs.extend(paral_job_dict[X86_FRAME])
                root = self.update_trigger_config(root, paral_jobs)
            else:
                # modify the setting of specific parallel job
                job_pkg_dict = dict()
                if AARCH_FRAME in target_job:
                    job_pkg_dict = self.get_job_pkg_dict(packages, paral_job_dict[AARCH_FRAME])
                elif X86_FRAME in target_job:
                    job_pkg_dict = self.get_job_pkg_dict(packages, paral_job_dict[X86_FRAME])

                root = self.update_paral_job_config(root, job_pkg_dict, target_job)

            if root:
                return ET.tostring(root).decode('utf-8')

        return None

    def create_multi_job(self, template_job, jobs, packages, concurrency=75, retry=3):
        """
        create multi jenkins job
        Args:
            template_job: template job name
            jobs: target jobs
            packages: packages
            concurrency: concurrency,default to 75
            retry: count to retry
        Returns:
            True or False
        """

        def create_multi_job_once(target_jobs, pkg_list):
            """
            create new job once for retry
            """
            batch = math.ceil(len(target_jobs) / concurrency)
            _failed_jobs = []
            for idx in range(batch):
                # jenkins job object list
                work_list = [gevent.spawn(self.dispatch, job, template_job, pkg_list)
                             for job in target_jobs[idx * concurrency: (idx + 1) * concurrency]]
                gevent.joinall(work_list)
                for work in work_list:
                    if work.value["result"]:
                        logger.info("job %s ... ok" % (work.value["job"]))
                    else:
                        _failed_jobs.append(work.value["job"])
                        logger.error("job %s  ... failed" % (work.value["job"]))
            return _failed_jobs

        failed_jobs = create_multi_job_once(jobs, packages)
        for index in range(retry):
            if not failed_jobs:
                break
            logger.info("%s jobs failed, retrying %s/%s" % (len(failed_jobs), index + 1, retry))
            failed_jobs = create_multi_job_once(failed_jobs, packages)

        if failed_jobs:
            return False
        return True

    @catch_jenkins_error
    def dispatch(self, job, template_job, packages):
        """
        dispatch create jenkins job
        Args:
            job: jenkins job name
            template_job: template job name
            packages: package names

        Returns:
            dict like {"job": job, "result": create_result}
        """
        job_exists = self.server.job_exists(template_job)
        if not job_exists:
            raise jenkins.NotFoundException("template job:%s not found." % template_job)

        temp_job_config = self.server.get_job_config(template_job)
        updated_config = self.update_config(job, temp_job_config, packages)
        create_result = self.create_new_job(job, updated_config)
        return {"job": job, "result": create_result}

    @catch_jenkins_error
    def create_selfbuild_jenkins_jobs(self, packages):
        """
        Create trigger, aarch64, x86 jobs respectively
        Returns:
            created_res
        """
        self.create_folder()
        template_job_list = [TRIGGER_TM_JOB, AARCH64_TM_JOB, X86_TM_JOB]
        for template_job in template_job_list:
            if not template_job:
                logger.error("error in getting template job name of %s for creating job." % template_job)
                return False

            target_jobs = self.get_jobs_to_create(template_job)
            created_res = self.create_multi_job(template_job, target_jobs, packages)
            if not created_res:
                return False

        return True

    @catch_jenkins_error
    def get_job_result_status(self, job_name, job_id):
        """
        get jenkins job result status
        Args:
            job_name: job name
            job_id: jenkins job build id

        Returns:
            build_res: SUCCESS, FAILURE, ABORTED, None(means the job is under building)
        """
        while True:
            time.sleep(5)
            build_res = self.server.get_build_info(job_name, job_id)['result']
            if build_res:
                break
        logger.info("%s %s build finished. The result status is %s" % (job_name, job_id, build_res))
        return build_res

    def build_specific_job(self, job_name, params=None):
        """
        build jenkins job according to job_name
        Args:
            params:parameters to build job
            job_name: job name

        Returns:
            last_job_num of jenkins job
        """
        queue_item = self.build_jenkins_job(job_name, params)

        if not queue_item:
            logger.error("unable to trigger specific job %s." % job_name)
            return None
        else:
            logger.info("successfully trigger %s, please waiting the jenkins job result..." % job_name)

            # The returned dict will have a "why" key if the queued item is still waiting for an executor
            while True:
                time.sleep(1)
                queue_item_resp = self.server.get_queue_item(queue_item)
                if not queue_item_resp.get("why"):
                    break

            # when the queue is over, the build id can be obtained
            last_job_num = self.server.get_job_info(job_name)['lastBuild']['number']
            return last_job_num

    @catch_jenkins_error
    def get_specific_job_comment(self, params, job_name):
        """
        get job status of jenkins job according to job name
        Args:
            params: params to build jenkins job
            job_name: job name

        Returns:

        """
        build_id = self.build_specific_job(job_name, params)

        if build_id:
            job_status = self.get_job_result_status(job_name, build_id)
            job_status_dict = {
                "name": job_name,
                "status": job_status,
                "output": self.get_output_hyperlink(job_name, build_id)
            }
            return [job_status_dict]

        return []

    @catch_jenkins_error
    def get_selfbuild_job_comment(self):
        """
        get parallel jenkins job status from trigger output
        Returns:
            job_status_list

        """

        def get_paral_job_id():
            job_name_id_dict = dict()
            try:
                target_trigger_job = self.get_jobs_to_create(TRIGGER_TM_JOB)[0]
                job_id = self.build_specific_job(target_trigger_job)
                trigger_status = self.get_job_result_status(target_trigger_job, job_id)
                logger.info("trigger job build finished, the result status is: %s" % trigger_status)

                # trigger output example:
                # Starting building: function-item » release-manager » openeuler-202106281604 » aarch64 » 2-11 #14
                output = self.server.get_build_console_output(target_trigger_job, job_id)
                new_output = output.replace(" » ", "/").splitlines()

                for line in new_output:
                    if "Starting building" in line:
                        line_info = line.split()
                        _job_name = line_info[2]
                        _build_id = line_info[3].strip("#")
                        job_name_id_dict[_job_name] = _build_id
                logger.info("finished to get build id dict: %s" % job_name_id_dict)
            except IndexError as err:
                logger.error("error in get self_build parallel job id. %s" % err)

            return job_name_id_dict

        job_name_id_map = get_paral_job_id()
        # get the status and output according to the job name and id
        job_status_list = []
        for job_name, build_id in job_name_id_map.items():
            job_name_status_dict = {
                "name": job_name,
                "status": self.get_job_result_status(job_name, int(build_id)),
                "output": self.get_output_hyperlink(job_name, build_id)
            }
            job_status_list.append(job_name_status_dict)
        return job_status_list
