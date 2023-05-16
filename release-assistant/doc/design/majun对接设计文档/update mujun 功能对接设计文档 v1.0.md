

# update mujun 功能对接设计文档 v1.0

## 流程

update 发布主体流程如下，请保障每部执行皆可回退至上一状态。

![](.\流程设计majun.png)

## 接口清单

主要功能依靠于jenkins后台任务，jenkins任务远程触发方式如下：

jenkins 任务触发示例：https://jenkinsjob_url/buildWithParameters?token=`TOKEN_NAME`

jenkins 任务带参数触发：https://jenkinsjob_url/buildWithParameters?token=`TOKEN_NAME`&`params`=`parameters`



### 需求页面

![image-20221021153540667](.\img\release_plan.png)

#### 1、新建发布任务：[版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013.（新增）

当前支持每周一定时触发生成/手动触发生成 update release issue，后续是否考虑直接通过添加对majun前端支持。

- 旧请求参数 无

- 新请求参数

  | 参数       | 类型 | 说明                                   |
  | ---------- | ---- | -------------------------------------- |
  | token_name | str  | 操作token                              |
  | branch     | str  | 发布计划版本，不填写表示所有在维护版本 |
  | operation  | str  | 操作，【添加/删除】                    |

- 返回参数

  | 参数     | 类型 | 说明     |
  | -------- | ---- | -------- |
  | 返回结果 | bool | 执行结果 |


#### 2、获取待发布cve

release issue 通过 /start-update 触发release tools 调取cve-manager 接口，获取近一年待发布CVE。

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数       | 类型 | 说明                                   |
  | ---------- | ---- | -------------------------------------- |
  | issue_id   | str  | release issue id                       |
  | username   | str  | 操作者gitee id                         |
  | GiteeToken | str  | 操作者gitee token                      |
  | ak         | str  | 华为云ak                               |
  | sk         | str  | 华为云sk                               |
  | email      | str  | 操作者 gitee 邮箱，用于触发cve-manager |

  

- 新请求参数：

  | 参数       | 类型 | 说明                                   |
  | ---------- | ---- | -------------------------------------- |
  | token_name | str  | 操作token                              |
  | ak         | str  | 华为云ak                               |
  | sk         | str  | 华为云sk                               |
  | email      | str  | 操作者 gitee 邮箱，用于触发cve-manager |



- 返回参数
 | 参数     | 类型 | 说明          |
| -------- | ---- | ------------- |
| 返回结果 | bool | 执行结果      |
| cve_list | list | 待发布cve列表 |

#### 2、需求反馈

开发者通过反馈 issue 软件包 pr 将相关需求提交到版本计划页面

- 新请求参数：

  | 参数    | 类型 | 说明      |
  | ------- | ---- | --------- |
  | issueid | str  | 码云issue |
  | package | str  | 软件包名  |
  | pr      | str  | pr链接    |



- 返回参数

| 参数     | 类型 | 说明          |
| -------- | ---- | ------------- |
| 返回结果 | bool | 执行结果      |
| cve_list | list | 待发布cve列表 |



#### 3、修改 CVE 及 Bugfix 列表

通过 add/del + issue id  修改release issue 需求列表。

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数       | 类型 | 说明                     |
  | ---------- | ---- | ------------------------ |
  | issue_id   | str  | release issue id         |
  | username   | str  | 操作者gitee id           |
  | GiteeToken | str  | 操作者gitee token        |
  | operate    | str  | 操作类型，【add/del】    |
  | type       | str  | 需求类型，【bugfix/cve】 |

- 新请求参数：

  | 参数       | 类型 | 说明                     |
  | ---------- | ---- | ------------------------ |
  | token_name | str  | jenkins操作token         |
  | operate    | str  | 操作类型，【add/del】    |
  | type       | str  | 需求类型，【bugfix/cve】 |



- 返回参数

  | 参数     | 类型 | 说明     |
  | -------- | ---- | -------- |
  | 返回结果 | bool | 执行结果 |



#### 4、版本基线范围确认

cve-ok、bugfix-ok、test-ok 确认版本基线。

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数         | 类型 | 说明                          |
  | ------------ | ---- | ----------------------------- |
  | issue_id     | str  | release issue id              |
  | username     | str  | 操作者gitee id                |
  | GiteeToken   | str  | 操作者gitee token             |
  | type         | str  | 需求类型，【bugfix_cve/test】 |
  | ak           | str  | 华为云ak                      |
  | sk           | str  | 华为云sk                      |
  | jenkins_user | str  | 华为云jenkins user_id         |
  | jenkkins_key | str  | 华为云jenkins_api_token       |

- 新请求参数：

  | 参数         | 类型 | 说明                     |
  | ------------ | ---- | ------------------------ |
  | token_name   | str  | jenkins操作token         |
  | operate      | str  | 操作类型，【add/del】    |
  | type         | str  | 需求类型，【bugfix/cve】 |
  | ak           | str  | 华为云ak                 |
  | sk           | str  | 华为云sk                 |
  | jenkins_user | str  | 华为云jenkins user_id    |
  | jenkkins_key | str  | 华为云jenkins_api_token  |

- 返回参数

  | 参数     | 类型 | 说明     |
  | -------- | ---- | -------- |
  | 返回结果 | bool | 执行结果 |



#### 5、版本检查（新增）

/check-versions 检查软件包是否一致

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数         | 类型 | 说明                         |
  | ------------ | ---- | ---------------------------- |
  | issue_id     | str  | release issue id             |
  | username     | str  | 操作者gitee id               |
  | GiteeToken   | str  | 操作者gitee token            |
  | type         | str  | 需求类型，【check-versions】 |
  | ak           | str  | 华为云ak                     |
  | sk           | str  | 华为云sk                     |
  | jenkins_user | str  | 华为云jenkins user_id        |
  | jenkkins_key | str  | 华为云jenkins_api_token      |

- 新请求参数：

  | 参数         | 类型 | 说明                         |
  | ------------ | ---- | ---------------------------- |
  | token_name   | str  | jenkins操作token             |
  | type         | str  | 需求类型，【check-versions】 |
  | ak           | str  | 华为云ak                     |
  | sk           | str  | 华为云sk                     |
  | jenkins_user | str  | 华为云jenkins user_id        |
  | jenkkins_key | str  | 华为云jenkins_api_token      |

- 返回参数

  | 参数     | 类型  | 说明     |
  | -------- | ----- | -------- |
  | 返回结果 | bool  | 执行结果 |
  | 验证结果 | table | 对比结果 |



#### 6、测试repo生成

通过/check-requires

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数         | 类型 | 说明                         |
  | ------------ | ---- | ---------------------------- |
  | issue_id     | str  | release issue id             |
  | username     | str  | 操作者gitee id               |
  | GiteeToken   | str  | 操作者gitee token            |
  | type         | str  | 需求类型，【check-versions】 |
  | ak           | str  | 华为云ak                     |
  | sk           | str  | 华为云sk                     |
  | jenkins_user | str  | 华为云jenkins user_id        |
  | jenkkins_key | str  | 华为云jenkins_api_token      |
  | buildcheck   | str  | 可选选项                     |

- 新请求参数：

  | 参数         | 类型 | 说明                         |
  | ------------ | ---- | ---------------------------- |
  | token_name   | str  | jenkins操作token             |
  | type         | str  | 需求类型，【check-versions】 |
  | ak           | str  | 华为云ak                     |
  | sk           | str  | 华为云sk                     |
  | jenkins_user | str  | 华为云jenkins user_id        |
  | jenkkins_key | str  | 华为云jenkins_api_token      |
  | buildcheck   | str  | 可选选项                     |

- 返回参数

  | 参数             | 类型  | 说明         |
  | ---------------- | ----- | ------------ |
  | result           | bool  | 执行结果     |
  | repo jobs result | table | repo生成结果 |

### 测试页面

![image-20221021180341125](.\img\release_test.png)

#### 7、操作测试repo

删除、更新、发布测试源内容

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数           | 类型 | 说明                                                         |
  | -------------- | ---- | ------------------------------------------------------------ |
  | action         | str  | 操作类型【create/del_pkg_rpm/update/del_update_dir/release】 |
  | obs_project    | str  | obs 对应工程                                                 |
  | pkgnamelist    | str  | 需要更新的软件包名称列表：package1,pacakge,package3 ...      |
  | update_dir     | str  | 更新版本目录如：update_20210201                              |
  | package_family | str  | 包归属族【standard/EPOL/EPOL-main/EPOL-multi_version】       |

- 新请求参数：

  | 参数                       | 类型 | 说明                                                         |
  | -------------------------- | ---- | ------------------------------------------------------------ |
  | action                     | str  | 操作类型【create/del_pkg_rpm/update/del_update_dir/release】 |
  | obs_project                | str  | obs 对应工程                                                 |
  | pkgnamelist                | str  | 需要更新的软件包名称列表：package1,pacakge,package3 ...      |
  | update_dir                 | str  | 更新版本目录如：update_20210201                              |
  | package_familyjenkins_user | str  | 包归属族【standard/EPOL/EPOL-main/EPOL-multi_version】华为云jenkins user_id |
  | token_name                 | str  | jenkins操作token                                             |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |



#### 8、转测数据及转测邮件

通过前端按钮触发转测邮件及发送转测数据至raidatest

- 旧请求参数：$webhook_action $full_name $comment_body $issue_title

  | 参数         | 类型 | 说明                         |
  | ------------ | ---- | ---------------------------- |
  | issue_id     | str  | release issue id             |
  | username     | str  | 操作者gitee id               |
  | GiteeToken   | str  | 操作者gitee token            |
  | type         | str  | 需求类型，【check-versions】 |
  | ak           | str  | 华为云ak                     |
  | sk           | str  | 华为云sk                     |
  | jenkins_user | str  | 华为云jenkins user_id        |
  | jenkkins_key | str  | 华为云jenkins_api_token      |
  | buildcheck   | str  | 可选选项                     |

- 新请求参数：

  | 参数         | 类型 | 说明                       |
  | ------------ | ---- | -------------------------- |
  | token_name   | str  | jenkins操作token           |
  | type         | str  | 需求类型，【check-status】 |
  | ak           | str  | 华为云ak                   |
  | sk           | str  | 华为云sk                   |
  | jenkins_user | str  | 华为云jenkins user_id      |
  | jenkkins_key | str  | 华为云jenkins_api_token    |
  | buildcheck   | str  | 可选选项                   |

- 返回参数

  | 参数             | 类型  | 说明         |
  | ---------------- | ----- | ------------ |
  | result           | bool  | 执行结果     |
  | repo jobs result | table | repo生成结果 |



#### 9、触发生产安全公告

支持按cve触发或全量触发

触发链接：

- 新请求参数：

  | 参数     | 类型 | 说明                                 |
  | -------- | ---- | ------------------------------------ |
  | typename | str  | 校验用户                             |
  | cveid    | str  | CVE 列表，多个，分隔，省缺表示全部。 |
  | date     | str  | 触发时间                             |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |

### 发布页面

![image-20221021180422171](.\img\release_page.png)

#### 10、一键发布后台：

##### 1、删除CVE-输入CVE编号删除(cve-security-notice-server/deleteCVE)

- 新请求参数：

| 参数        | 类型 | 说明   |
| ----------- | ---- | ------ |
| username    | str  | 用户名 |
| password    | str  | 密码   |
| deleteCVEID | str  | Cveid  |
| packageName | str  | 软件包 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



##### 2、删除安全公告-输入公告编号删除(cve-security-notice-server/deleteSA)

- 新请求参数：

| 参数       | 类型 | 说明     |
| ---------- | ---- | -------- |
| username   | str  | 用户名   |
| password   | str  | 密码     |
| deleteSAID | str  | 安全公告 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



##### 3、同步 unaffected CVE(cve-security-notice-server/syncUnCVE)

- 新请求参数：

| 参数     | 说明 | 类型     |
| -------- | ---- | -------- |
| username | str  | 用户名   |
| password | str  | 密码     |
| cveNo    | str  | 文件路径 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



#####  4、同步 SA(cve-security-notice-server/syncSA)

- 新请求参数：

| 参数     | 说明 | 类型     |
| -------- | ---- | -------- |
| username | str  | 用户名   |
| password | str  | 密码     |
| saNo     | str  | 文件路径 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



#####  5、一键发布(cve-security-notice-server/syncAll)

- 新请求参数：

| 参数     | 类型 | 说明   |
| -------- | ---- | ------ |
| username | str  | 用户名 |
| password | str  | 密码   |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



#####  6、查询 CVE NVD解析(cve-security-notice-server/syncHardware)

- 新请求参数：

| 参数        | 说明 | 类型   |
| ----------- | ---- | ------ |
| username    | str  | 用户名 |
| password    | str  | 密码   |
| cveNo       | str  | Cveid  |
| packageName | str  | 软件包 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



##### 7、生成Unaffected文件(cve-security-notice-server/generateXml)

- 新请求参数：

| 参数      | 说明 | 类型   |
| --------- | ---- | ------ |
| username  | str  | 用户名 |
| password  | str  | 密码   |
| startTime | str  | 时间   |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |



##### 8、检验updateinfo(cve-security-notice-server/inspectionXml)

- 新请求参数：

| 参数     | 说明 | 类型   |
| -------- | ---- | ------ |
| username | str  | 用户名 |
| password | str  | 密码   |
| fileName | str  | 文件名 |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |
  | msg    | str  | 结果说明 |

 

#### 11、cvrf 同步

将CVRF 文件同步至官方归档地址

- 新请求参数：

  | 参数       | 类型 | 说明               |
  | ---------- | ---- | ------------------ |
  | server     | str  | 发布件存储后台后台 |
  | bucketname | str  | 存储对象桶名称     |
  | filename   | str  | 目录文件名         |
  | ipaddr     | str  | 发布机器IP地址     |

- 返回参数

  | 参数   | 类型 | 说明     |
  | ------ | ---- | -------- |
  | result | bool | 执行结果 |



#### 12、updateinfo 同步

根据软件包发布情况更新官网repodata

- 新请求参数：

  | 参数       | 类型 | 说明               |
  | ---------- | ---- | ------------------ |
  | server     | str  | 发布件存储后台后台 |
  | bucketname | str  | 存储对象桶名称     |
  | filename   | str  | 目录文件名         |
  | ipaddr     | str  | 发布机器IP地址     |

- 返回参数

  | 参数   | 类型 | 说明                |
  | ------ | ---- | ------------------- |
  | result | bool | 执行结果jiangpengju |



## Release-tools 功能实现

### 1. 获取待发布cve （start功能）

#### 1.1 实现流程

![本地路径](.\img\start.png)

#### 1.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称   | 参数类型 | 是否必传 | 说明                                                         |
| ---------- | :------- | :------- | :----------------------------------------------------------- |
| ak         | str      | 否       | 华为云的access_key，已经设置到jenkins的环境变量中名称为release_access_key |
| sk         | str      | 否       | 华为云的secret_key，已经设置到jenkins的环境变量中名称为release_secret_key |
| useremail  | str      | 是       | 触发cve-manage归档的邮箱地址                                 |
| task_title | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| id         | str      | 是       | majun 的uuid                                                 |

**返回数据**

```json
{'code': '200',
 'data': [{'CVE': '#I4WHTZ:CVE-2020-10775',
           'abiChange': '否',
           'score': 5.3,
           'status': '已完成',
           'version': '4.4.4.1',
           'software': 'ovirt-engine'}],
 'id': '778589',
 'msg': 'Operation succeeded'}
```

代码位置：majunstart.py

| 函数                   | 作用                               |
| ---------------------- | ---------------------------------- |
| trigger_cve_archive    | 触发cve mange 归档                 |
| get_cve_list           | 华为云下载excel文件，并读取        |
| cve_list_recombine     | cve list数据重新组合 key值重新命名 |
| send_cve_list_to_majun | 函数总入口                         |

### 2.  软件包的版本检查

#### 2.1 实现流程

![本地路径](.\img\package_version.png)

#### 2.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称   | 参数类型 | 是否必传 | 说明                                                         |
| ---------- | :------- | :------- | :----------------------------------------------------------- |
| task_title | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| pkglist    | str      | 是       | 软件包列表传参方式包名之间用空格隔开  vim CUnit              |
| id         | str      | 是       | majun 的uuid                                                 |

返回数据

```json
{'data': {'novnc': 'same', 'openstack-aodh': 'same'}, 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

**代码位置**package_version.py

| 函数名称              | 作用                             |
| --------------------- | -------------------------------- |
| run                   | 函数主入口                       |
| obs_package_version   | obs 上软件包的version release    |
| gitee_package_version | gitee 上 软件包的version release |

### 3.  操作repo

#### 3.1 实现流程

![本地路径](.\img\repo.png)

#### 3.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称       | 参数类型 | 是否必传 | 说明                                                         |
| -------------- | :------- | :------- | :----------------------------------------------------------- |
| task_title     | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| pkglist        | str      | 否       | 软件包列表传参方式包名之间用空格隔开  vim CUnit              |
| id             | str      | 是       | majun 的uuid                                                 |
| jenkinsuser    | str      | 是       | jenkins 的用户名，用jenkins的工程环境配置                    |
| jenkinskey     | str      | 是       | jenkins 的用户密码，用jenkins的工程环境配置                  |
| action         | str      | 是       | create：创建update目录并拷贝rpm到测试服务器上。（该功能需要的参数为：obs_project，pkgnamelist，update_dir【可选】，package_family） <BR> del_pkg_rpm：删除update目录中软件包的二进制。（该功能需要的参数为：obs_project，pkgnamelist，update_dir，package_family）                                                                                                                                                                                     update：更新update目录中一个或多个软件包的二进制。（该功能需要的参数为：obs_project，pkgnamelist，update_dir，package_family）                                                                                                                                                       del_update_dir：删除测试服务器上指定的update目录。（该功能需要的参数为：obs_project，update_dir，package_family） 注意：当删除多版本EPOL下的目录时，(1) package_family参数选择EPOL时，会删除整个创建好的update_xxx目录; (2)选择EPOL-main时，会删除update_xxx下的main目录；(3)选择EPOL-multi_version时，会删除update_xxx下的multi_version目录。 |
| package_family | str      | 否       | 当action 为del_update_dir package_family                     |

**返回给majun的结果**

action 为create

```
{'data': {'standard': 'http://xxx.xxx.xxx.xxx/repo.openeuler.org/openEuler-22.03-LTS/update_20191013test/'}, 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

action 为del_pkg_rpm

```jso
{'data': "CUnit,vim", 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

其他

```json
{'data': True, 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

代码位置：majunoperate.py

| 函数             | 作用                |
| ---------------- | ------------------- |
| operate_repo     | 操作repo总入口      |
| _normal_repo     | 日常版本操作repo    |
| _multi_repo      | 多版本操作repo      |
| transfer_pkg_rpm | 调用jenkins任务入口 |



### 4. 测试创建里程碑返回majun

#### 4.1 实现流程图

![本地路径](.\img\sendtest.png)

#### 4.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称   | 参数类型 | 是否必传 | 说明                                                         |
| ---------- | :------- | :------- | :----------------------------------------------------------- |
| task_title | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| pkglist    | str      | 是       | 软件包列表传参方式包名之间用空格隔开  vim CUnit              |
| id         | str      | 是       | majun 的uuid                                                 |

返回数据

```json
{'data': 里程碑名称, 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

代码位置：majunoperate.py

| 函数                   | 作用                                    |
| ---------------------- | --------------------------------------- |
| send_repo_info         | 发送数据给测试总入口，数据组合          |
| send_data_test_platfor | 发送数据给测试平台，并将结果返回给majun |

### 5. cvrf 同步 和 updateinfo 同步

#### 5.1实现流程

![本地路径](.\img\update.png)

#### 5.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称       | 参数类型 | 是否必传 | 说明                                                         |
| -------------- | :------- | :------- | :----------------------------------------------------------- |
| choice         | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| jenkinsuser    | str      | 是       | jenkins 的用户名，用jenkins的工程环境配置                    |
| jenkinskey     | str      | 是       | jenkins 的用户密码，用jenkins的工程环境配置                  |
| bucketname     | str      | 是       | openeuler-cve-cvrf                                           |
| server         | str      | 是       | 华为云云存储服务器地址                                       |
| cvrffilename   | str      | 是       | index.txt,update_fixed.txt                                   |
| updatefilename | str      | 是       | index.txt                                                    |
| ipaddr         | str      | 是       | 发布服务器地址                                               |
| id             | str      | 是       | majun 的uuid                                                 |

返回数据

```json
{'data': True, 
 'id': 'xxxxxx', 
 'code': '200', 
 'msg': 'Operation succeeded'}
```

代码位置：majunoperate.py

| 函数             | 作用                                 |
| ---------------- | ------------------------------------ |
| synchronous_info | cvrf 同步和updateinfo 同步 入口      |
| _all_sync        | 同时调用cvrf 同步和updateinfo 同步   |
| _single_sync     | 调用调用cvrf 同步或者updateinfo 同步 |

### 6. 协助获取at结果 

#### 6.1实现流程

![image-20230516142903048](.\img\at.png)

#### 6.2 调用

**调用方式**：远程调用 GET 请求

**请求参数：**

| 参数名称   | 参数类型 | 是否必传 | 说明                                                         |
| ---------- | :------- | :------- | :----------------------------------------------------------- |
| task_title | str      | 是       | 版本任务 如： [版本]_update[日期]， 如 openEuler-20.03-LTS-SP1_update20221013 |
| pkglist    | str      | 是       | 软件包列表传参方式包名之间用空格隔开  vim CUnit              |
| id         | str      | 是       | majun 的uuid                                                 |

返回数据

```json
{'data': 
 ' "http://xxx.xxx.xxx.xxx/dailybuild//openEuler-22.09/openeuler-2022-11-27-20-54-34/ISO/aarch64/openEuler-22.09-aarch64-dvd.iso";"http://xxx.xxx.xxx.xxx/dailybuild//openEuler-22.09/openeuler-2022-11-27-20-54-34/ISO/aarch64/openEuler-22.09-x86-dvd.iso" ',  
 'id': 'xxxxxx', 
 'code': '200',  
 'msg': 'Operation succeeded'}
```

代码位置：majun_at.py

| 函数                         | 作用                                             |
| ---------------------------- | ------------------------------------------------ |
| run                          | 函数总入口                                       |
| all_iso_time                 | 在dailybuild网站中获取release_iso文件中的内容    |
| get_jenkins_job_build_result | 调用iso 构建的jenkins任务，将jenkins运行结果返回 |

