#!/usr/bin/env python3
"""Conservative publication checks. Reports locations, never matching values.

This complements full-history credential scanning and a human review of rights,
screenshots, examples and runtime behavior. It does not change visibility.
"""
from pathlib import Path
import re
import hashlib
import subprocess
import sys

REQUIRED = ('README.md', 'LICENSE', 'CONTRIBUTING.md', 'SECURITY.md')
EDITORIAL = re.compile(
    r'独立脱敏|脱敏源码|脱敏说明|中性.{0,8}品牌|sanitized source distribution|'
    r'公司订阅|公司模型|本轮|用户本次要求|用户明确授权的|用户要求[:：]|'
    r'上线验收记录|本次.{0,12}(?:验收|部署|交付|验证)|'
    r'原本机|原采集目录|原 ChatGPT|/Users/[^/\s]+/|/home/developer/|'
    r'首次对外发布前，请补全|写清目标用户|补充实际安装命令|接入本项目真实的测试', re.I)
CREDENTIALS = re.compile(
    r'gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}|'
    r'AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
FOREIGN_RUNTIME = re.compile(
    r'rh-dev(?:-cn)?-int\.haimacloud\.com|sd-tk\.haimawan\.com|'
    r'analytics\.ahrefs\.com|hm\.baidu\.com|fxgate\.baidu\.com|'
    r'proj-xtrace-[\w-]+\.log\.aliyuncs\.com')


def check(root):
    root = Path(root).resolve()
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    errors = []
    for name in REQUIRED:
        if not (root / name).is_file() or not (root / name).read_text().strip():
            errors.append(f'{name}: required publication file missing or empty')
    for name in filter(None, names):
        path = root / name
        if not path.exists():
            errors.append(f'{name}: tracked file missing')
            continue
        if path.is_symlink():
            errors.append(f'{name}: symlink needs an explicit packaging review')
            continue
        if path.name.upper() == 'SANITIZED-DISTRIBUTION.MD':
            errors.append(f'{name}: internal export document')
        if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example'):
            errors.append(f'{name}: local environment file')
        # No size cutoff: compiled bundles can contain embedded credentials.
        raw = path.read_bytes()
        content = raw.decode('utf-8', errors='replace')
        if CREDENTIALS.search(content):
            errors.append(f'{name}: possible credential (value withheld)')
        third_party = any(part in ('vendor', 'node_modules') for part in path.relative_to(root).parts)
        if third_party:
            continue  # Keep upstream documentation and attribution intact.
        editorial_scope = path.suffix.lower() in ('.md', '.txt', '.json', '.yaml', '.yml', '.html')
        tooling = name.startswith(('scripts/', 'tests/', '.github/'))
        if editorial_scope and not tooling and EDITORIAL.search(content):
            errors.append(f'{name}: internal handoff or unfinished project prose')
        if name.startswith(('dist/', 'apps/web/public/')) and FOREIGN_RUNTIME.search(content):
            errors.append(f'{name}: third-party runtime or telemetry endpoint needs review')
        if path.suffix == '.svg' and hashlib.sha256(raw).hexdigest() == 'd6d755a57fa2d1f5257628f32150bbf6afb9540257e7e708468ad19a85a305e3':
            errors.append(f'{name}: generic placeholder artwork needs replacement or removal')
        if path.name == 'UPSTREAM.json' and '"license_file_present": false' in content:
            errors.append(f'{name}: third-party distribution permission unresolved')
    return errors


if __name__ == '__main__':
    root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
    errors = check(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f'Publication blocked: {len(errors)} findings. Review every finding; do not erase attribution or rebaseline tests to bypass the check.', file=sys.stderr)
        sys.exit(1)
    print('Publication text and packaging checks passed. Full-history secret scanning, license review and project tests are still required.')
