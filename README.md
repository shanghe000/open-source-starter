# Open Source Starter

一个轻量的开源项目起点：把文档、反馈、检查和发布流程准备好，再专注于项目本身。

**状态：可复用的仓库模板。** 不绑定框架或语言；尚未包含业务应用与业务测试。

## 快速开始

点击仓库顶部 **Use this template**，或在克隆本模板后运行：

```sh
python3 scripts/new_project.py my-project --description "一句话介绍项目" --visibility public
```

需要 Python 3.10+、Git 和已登录的 GitHub CLI。创建脚本默认使用私有可见性；以上示例明确选择公开。
随后把本 README 改成你的项目介绍，补上安装步骤、最小示例、功能范围、截图与限制。

## 已包含

| 内容 | 用途 |
| --- | --- |
| Issue 表单与 PR 模板 | 收集可复现的问题、清晰的变更说明 |
| CONTRIBUTING / SECURITY | 贡献方式与私密漏洞报告指引 |
| Repository quality | 校验文档本地链接、SVG、基础凭据模式与不应提交的文件 |
| Draft release | 手动创建版本标签与可审核的发布草稿 |
| Dependabot | 每月检查 GitHub Actions 依赖更新 |
| 初始化脚本 | 创建新项目，按需配置合并方式与默认分支规则 |

## 本地检查

```sh
python3 scripts/check_repository.py
```

这是仓库卫生检查，不能代替业务测试、完整密钥扫描或安全审计。
脚本扫描 Git 跟踪文件；修改后请先暂存新文件再检查，避免漏掉未跟踪文件。
链接检查覆盖 Markdown 行内相对链接和 HTML 图片本地路径，不请求外部网络，也不校验锚点。

## 初始化仓库设置

新项目首次推送并看到 `Repository quality` 成功后执行：

```sh
python3 scripts/configure_repository.py
```

脚本按当前仓库和已登录账号工作，要求你是仓库所有者；它设置 squash 合并与合并后清理功能分支。
公开仓库还会开启私密漏洞报告、添加需要 PR 和检查的默认分支规则；管理员仅在 PR 中可绕过。
私有仓库仅设置合并选项，并提示规则需按计划能力单独配置。
GitHub 不会从模板复制规则与仓库设置，因此每个新项目需运行一次。

## 发布

Actions → **Draft release** → **Run workflow** → 输入 `v0.1.0`。
成功后到 Releases 检查草稿，再手动发布。流程对默认分支运行时的确切提交打标签，不覆盖已有版本。
仅创建源码发布草稿；二进制打包与软件包分发请按项目添加。

## 接入你的技术栈

在 `.github/workflows/` 添加项目自己的检查。例如 Python 的真实测试、Node 的锁文件安装与构建、Go 的测试。
依赖清单存在后再添加对应的 Dependabot ecosystem，避免空配置报错。
功能稳定后，把业务检查名称加入默认分支规则。

## 贡献与许可

[贡献指南](CONTRIBUTING.md) · [安全政策](SECURITY.md) · [MIT License](LICENSE)

保留模板原有许可声明；为新增代码补充适用的版权与许可。
