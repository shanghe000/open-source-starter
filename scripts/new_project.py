#!/usr/bin/env python3
"""Create a repository from this template. No credentials are exported."""
import argparse
from pathlib import Path
import re
import subprocess


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
    original = readme.read_text()
    readme.write_text(f'# {args.name}\n\n{args.description}\n\n' + original.split('\n', 1)[1].lstrip())
    run('git', 'add', 'README.md', cwd=directory)
    run('python3', 'scripts/check_repository.py', cwd=directory)
    run('git', 'commit', '-m', 'docs: initialize project overview', cwd=directory)
    run('git', 'push', cwd=directory)
    print(f'Created https://github.com/{target}. After Repository quality passes, run scripts/configure_repository.py inside {args.name}.')


if __name__ == '__main__':
    main()
