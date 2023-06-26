#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
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
Description: check openEuler cvrf packages version before publishing
"""

import argparse
import os
import sys
import ssl
import warnings

import xml.etree.ElementTree as et
from urllib.request import urlopen

import requests
from lxml import etree

from javcra.api.obscloud import ObsCloud
from javcra.common.constant import CVE_MANAGE_SERVER, CVE_MANAGE_BUCKET_NAME, VERSION_LIST, ARCH_LIST, BASE_URL


def resolve_xml(cvrf: str) -> dict:
    """
    resolve cvrf xml to get packages info.
    Args:
        cvrf(str): name of the cvrf
    Returns:
        xml_result(list): return the package list of the cvrf
    """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    xml_result = {}
    ssl._create_default_https_context = ssl._create_unverified_context
    cvrf_url = "https://repo.openeuler.org/security/data/cvrf/{}".format(cvrf)
    raw_xml = urlopen(cvrf_url)
    tree = et.parse(raw_xml)
    root = tree.getroot()

    # resolve packages' version from cvrf files.
    for branch in root[6]:
        if branch.attrib["Name"] == "openEuler":
            continue
        for product in branch:
            version_branch = product.attrib['CPE'].split(":", 3)[-1].replace(":", "-")
            pkg_arch = product.text.rsplit(".", 2)[-2]
            pkgs_of_branch = xml_result.get(version_branch, {})
            temp_list = pkgs_of_branch.get(pkg_arch, [])
            temp_list.append(product.text)
            pkgs_of_branch[pkg_arch] = temp_list
            xml_result[version_branch] = pkgs_of_branch
    return xml_result


def resolve_html(version_date: str) -> dict:
    """
    resovle test repo's packates
    Args:
        version_date(str): The version cration date of update.
    Returns:
        html_result(list): package of the test repo
    """
    html_result = {}
    for version in VERSION_LIST:
        html_result[version] = {}
        for arch in ARCH_LIST:
            arch_pkgs = []

            # resolve EPOL packages when packages in VERSION_LIST[4:], which is epol repo list.
            if version in VERSION_LIST[4:]:
                response = requests.get(BASE_URL.format(version, version_date + "/main", arch))
            else:
                response = requests.get(BASE_URL.format(version, version_date, arch))

            # resolve html element to get package versions with architecture.
            tree = etree.HTML(response.text)
            rows = tree.xpath('//table[@id="list"]/tbody/tr')[1:]
            for row in rows:
                package_name = row.xpath('./td/a/text()')
                arch_pkgs.append(str(package_name[0]))
            if arch == "source":
                html_result[version]["src"] = arch_pkgs
            html_result[version][arch] = arch_pkgs

    return html_result


def compare_packages(xml_result: dict, html_result: dict) -> bool:
    """
    Compare xml packages version with html packages
    Args:
        xml_result(dict): cvrf xml packages
        html_result(dict): all packages of update repo
    Returns:
        bool: the result of the comparision
    """
    result = []
    for version in VERSION_LIST:
        # resolve packages in everything
        if html_result.get(version) and xml_result.get(version):
            temp_res = check_packages_with_arch(version, html_result, xml_result, "")
            if all(res for res in temp_res):
                result.append(temp_res)
                continue

        # resolve packages in EPOL
        if html_result.get("".join([version, "/EPOL"])) and xml_result.get(version):
            temp_res = check_packages_with_arch(version, html_result, xml_result, "/EPOL")
            result.append(temp_res)

    return all(all(arch_res for arch_res in res) for res in result)


def check_packages_with_arch(version: str, html_result: dict, xml_result: dict, repo_type: str) -> list:
    """
    check packages with arch in a specific openEuler version
    Args:
        version(str): openEuler version e.g. openEuler-20.03-LTS-SP1
        html_result(dict): html repo infomation of packages
        xml_result(dict): cvrf xml information of packages
        repo_type(dict): repo type of the packages

    Returns:
        list: temp check result of a specific openEuler version
    """
    temp_res = []
    for xml_pkg in xml_result[version]:
        if xml_pkg == "noarch":
            result = all(pkg in html_result["".join([version, repo_type])]["aarch64"]
                         for pkg in xml_result[version][xml_pkg])
        else:
            result = all(pkg in html_result["".join([version, repo_type])][xml_pkg]
                         for pkg in xml_result[version][xml_pkg])
        if not res:
            print("Package check in {} failed arch is:{}, {}".format(version, xml_pkg, result))
        temp_res.append(result)

    return temp_res


def traversal_check_updated_cvrf(version_date: str):
    """
    check updated cvrfs' packages with the test repo
    Args:
        version_date(str): The version cration date of update.
    """
    html_result = resolve_html(version_date)
    with open("updated_index.txt", 'r', encoding='utf-8') as file:
        for line in file.readlines():
            xml_name = line.replace("\n", "")
            if compare_packages(resolve_xml(line), html_result):
                print("{} packages comparision result is: Pass.".format(xml_name))
            else:
                print("{} packages comparision result is: Failed.".format(xml_name))


if __name__ == "__main__":
    # cli parameters of the package check modole
    parser = argparse.ArgumentParser(description="check cvrf package's version")
    parser.add_argument("--updated_date", required=False, type=str, help="date of the update")
    parser.add_argument("--sk", required=True, type=str, action="store", help="provide your secret key")
    parser.add_argument("--ak", required=True, type=str, action="store", help="provide your access key")
    args = parser.parse_args()

    # download latest updated_index of cvrf files.
    file_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    obs_client = ObsCloud(args.ak, args.sk, CVE_MANAGE_SERVER, CVE_MANAGE_BUCKET_NAME)
    try:
        res = obs_client.down_load_file("cvrf/update_fixed.txt", os.path.join(file_path, "updated_index.txt"))
    except requests.exceptions.RequestException:
        print("Failed to get updated_infdex or the object does not exist in the bucket")
        sys.exit(1)

    # check all latest updated packages in cvrf and repo
    traversal_check_updated_cvrf(args.updated_date)
