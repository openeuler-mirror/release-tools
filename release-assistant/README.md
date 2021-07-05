# Javcra

#### 介绍
Javcra 是一款辅助社区开发者和版本发布人员快速发布openEuler update版本的自动化发布工具，它配合gitee api、Jenkins 以及cve-manager等周边组件，依托gitee的issue平台，通过在issue中评论相应命令，实现自动触发发布流程、修改发布列表以及监控版本issue和自动验证功能。


#### 安装教程

1.  git clone https://gitee.com/openeuler/release-tools.git
2.  在 release-tools/javcra 文件夹下执行如下命令
3.  python3 setup.py build
4.  python3 setup.py build

#### 使用说明

1.  启动发布流程（start）：

    gitee issue评论： /start-update

    ```bash
    javcra start $releaseIssueID --giteeid $GITEEID
    ```
2.  修改issue中的列表（modify）：

    gitee issue 评论：/add cve #I84734 #I93043 #I3A34M

    ```bash
    # 添加cve列表中的issue
    javcra modify $releaseIssueID --add cve --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/add bugfix #I84734 #I93043 #I3A34M

    ```bash
    # 添加bugfix列表中的issue
    javcra modify $releaseIssueID --add bug --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/add test #I84734 #I93043 #I3A34M

    ```bash
    # 添加test列表中的issue
    javcra modify $releaseIssueID --add test --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/add release #I84734 #I93043 #I3A34M

    ```bash
    # 添加最终发布的问题列表（默认都是确认发布的，这个场景主要用于，一开始确认为不发布，后来需要修改成发布的场景）
    javcra modify $releaseIssueID --add release --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/delete cve #I84734 #I93043 #I3A34M

    ```bash
    # 删除cve列表中的issue
    javcra modify $releaseIssueID --del cve --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/delete bugfix #I84734 #I93043 #I3A34M

    ```bash
    # 删除bugfix列表中的issue
    javcra modify $releaseIssueID --del bug --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/delete test #I84734 #I93043 #I3A34M

    ```bash
    # 删除test列表中的issue
    javcra modify $releaseIssueID --del test --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

    gitee issue 评论：/delete release #I84734 #I93043 #I3A34M

    ```bash
    # 添加最终不发布的问题列表
    javcra modify $releaseIssueID --del release --id $issueID1  $issueID2 ... --giteeid $GITEEID
    ```

3. 发布流程中对各个状态的检查和确认（check）：

    gitee issue 评论：/cve-ok or /cve-not-ok

    ```bash
    # 确认cve列表issue ok 或者 不ok
    javcra check $releaseIssueID --type cve --result yes/no --giteeid $GITEEID
    ```

    gitee issue 评论：/bugfix-ok or /bugfix-not-ok

    ```bash
    # 确认bugfix列表issue ok 或者 不ok
    javcra check $releaseIssueID --type bug --result yes/no --giteeid $GITEEID
    ```

    gitee issue 评论：/test-ok or /test-not-ok

    ```bash
    # 确认测试结果为 通过 或者 不通过
    javcra check $releaseIssueID --type test --result yes/no --giteeid $GITEEID
    ```

    gitee issue 评论：/check-status

    ```bash
    # 获取当前版本提交的issue状态
    javcra check $releaseIssueID --type status --giteeid $GITEEID
    ```

    gitee issue 评论：/get-requires

    ```bash
    # 获取当前版本的发布范围以及自验证结果
    javcra check $releaseIssueID --type requires --giteeid $GITEEID
    ```

4. 最终发布前的确认（release）：

    gitee issue 评论：/check-ok

    ```bash
    # 版本发布人员确认最终发布结果没问题
    javcra check $releaseIssueID --type checkok --giteeid $GITEEID
    ```

    gitee issue 评论：/cvrf-ok

    ```bash
    # 安全委员会人员确认最终发布结果没问题
    javcra check $releaseIssueID --type cvrfok --giteeid $GITEEID
    ```

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

