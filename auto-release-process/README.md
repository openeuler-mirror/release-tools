# Auto Release Process

#### 介绍
Auto Release Process 是一款辅助社区开发者和版本发布人员快速发布openEuler update版本的自动化发布工具，它配合gitee api、Jenkins 以及cve-manager等周边组件，依托gitee的issue平台，通过在issue中评论相应命令，实现自动触发发布流程、修改发布列表以及监控版本issue和自动验证功能。


#### 安装教程

1.  git clone https://gitee.com/openeuler/release-tools.git
2.  在 release-tools/auto-release-process 文件夹下执行如下命令
3.  python3 setup.py build
4.  python3 setup.py build

#### 使用说明

1.  启动发布流程：
gitee issue评论： /start-update

```bash
arp start releaseIssueID --giteeid GITEEID
```
2.  待添加

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

