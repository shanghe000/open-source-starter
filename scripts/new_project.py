#!/usr/bin/env python3
"""Create a repository from this template. No credentials are exported."""
import argparse
from pathlib import Path
import re
import subprocess
import sys


def project_readme(name, description, owner):
    return f'''# {name}

{description}

![Repository quality](https://github.com/{owner}/{name}/actions/workflows/quality.yml/badge.svg)

**状态：开发中。** 首次对外发布前，请补全以下内容并删除提示文字。

## 解决什么问题

写清目标用户、具体场景、适用范围与不适用的情况。

## 快速开始

补充实际安装命令、一个最小示例和预期结果。需要账号或外部服务时说明前提。

## 当前能力与限制

列出已经实现并验证的能力；计划中的功能放在 [路线图](docs/ROADMAP.md)。

## 开发与贡献

先运行通用检查：`python3 scripts/check_repository.py`。
接入本项目真实的测试与构建，再填写对应命令。

[贡献指南](CONTRIBUTING.md) · [行为规范](CODE_OF_CONDUCT.md) · [安全政策](SECURITY.md)

维护者请阅读 [维护说明](docs/MAINTAINER_GUIDE.md)，配置仓库设置、主分支规则与发布方式。

## 许可证

[MIT License](LICENSE)。保留模板许可，并为新增代码补充适用的版权声明。
'''


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', help='lowercase-kebab-case name')
    parser.add_argument('--description', required=True)
    parser.add_argument('--visibility', choices=['public', 'private'], default='private')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.name):
        parser.error('Use lowercase letters, numbers and single hyphens.')
    if Path(args.name).exists():
        parser.error('Local directory already exists; choose a different name or location.')
    owner = subprocess.check_output(['gh', 'api', 'user', '--jq', '.login'], text=True).strip()
    account_id = subprocess.check_output(['gh', 'api', 'user', '--jq', '.id'], text=True).strip()
    target = f'{owner}/{args.name}'
    run('gh', 'repo', 'create', target, '--template', 'shanghe000/open-source-starter', f'--{args.visibility}', '--description', args.description)
    run('gh', 'repo', 'clone', target, args.name)
    directory = Path(args.name)
    run('git', 'config', 'user.name', owner, cwd=directory)
    run('git', 'config', 'user.email', f'{account_id}+{owner}@users.noreply.github.com', cwd=directory)
    readme = directory / 'README.md'
    readme.write_text(project_readme(args.name, args.description, owner), encoding='utf-8')
    run('git', 'add', 'README.md', cwd=directory)
    run(sys.executable, 'scripts/check_repository.py', cwd=directory)
    run('git', 'commit', '-m', 'docs: initialize project overview', cwd=directory)
    run('git', 'push', cwd=directory)
    print(f'Created https://github.com/{target}. After Repository quality passes, run scripts/configure_repository.py inside {args.name}.')


if __name__ == '__main__':
    main()
