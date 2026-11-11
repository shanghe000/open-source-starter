#!/usr/bin/env python3
"""Configure the current owned repository; safe to rerun for this named ruleset."""
import json
import subprocess

RULE_NAME = 'default-branch-quality'


def gh(*args, payload=None):
    command = ['gh', *args]
    if payload is not None:
        command += ['--input', '-']
    output = subprocess.check_output(command, input=json.dumps(payload) if payload is not None else None, text=True)
    return json.loads(output) if output.strip() else None


def main():
    repo = gh('repo', 'view', '--json', 'nameWithOwner,isPrivate,defaultBranchRef')
    name = repo['nameWithOwner']
    login = gh('api', 'user')['login']
    if name.split('/')[0].lower() != login.lower():
        raise SystemExit('Only repositories owned by the currently authenticated user are supported.')
    if not repo['defaultBranchRef'] or not repo['defaultBranchRef'].get('name'):
        raise SystemExit('Push the initial commit before configuring repository rules.')
    # Do not install a required check until it has actually run successfully.
    if not repo['isPrivate']:
        branch = repo['defaultBranchRef']['name']
        head = gh('api', f'repos/{name}/commits/{branch}')['sha']
        runs = gh('run', 'list', '--repo', name, '--workflow', 'quality.yml', '--branch', branch, '--limit', '30', '--json', 'conclusion,event,headSha')
        if not any(r['headSha'] == head and r['conclusion'] == 'success' and r['event'] in ['push', 'workflow_dispatch'] for r in runs):
            raise SystemExit('Wait for a successful Repository quality run on the default branch, then rerun.')
        publication = gh('run', 'list', '--repo', name, '--workflow', 'publication.yml', '--branch', branch, '--limit', '30', '--json', 'conclusion,headSha,event')
        if not any(r['headSha'] == head and r['conclusion'] == 'success' and r['event'] in ['push', 'workflow_dispatch'] for r in publication):
            raise SystemExit('Wait for Publication readiness to pass on the current default-branch commit.')
    gh('api', f'repos/{name}', '--method', 'PATCH', payload={
        'allow_squash_merge': True, 'allow_merge_commit': False,
        'allow_rebase_merge': False, 'delete_branch_on_merge': True,
        'squash_merge_commit_title': 'PR_TITLE', 'squash_merge_commit_message': 'PR_BODY',
    })
    if repo['isPrivate']:
        print(f'{name}: merge settings configured. Private branch rules depend on your GitHub plan; configure separately.')
        return
    gh('api', f'repos/{name}/private-vulnerability-reporting', '--method', 'PUT')
    rules = {
        'name': RULE_NAME, 'target': 'branch', 'enforcement': 'active',
        'bypass_actors': [{'actor_id': 5, 'actor_type': 'RepositoryRole', 'bypass_mode': 'pull_request'}],
        'conditions': {'ref_name': {'include': ['~DEFAULT_BRANCH'], 'exclude': []}},
        'rules': [
            {'type': 'deletion'}, {'type': 'non_fast_forward'},
            {'type': 'pull_request', 'parameters': {
                'required_approving_review_count': 0, 'dismiss_stale_reviews_on_push': True,
                'require_code_owner_review': False, 'require_last_push_approval': False,
                'required_review_thread_resolution': True,
            }},
            {'type': 'required_status_checks', 'parameters': {
                'required_status_checks': [{'context': name, 'integration_id': 15368} for name in ('Repository quality', 'Publication content', 'Credential scan')],
                'strict_required_status_checks_policy': True,
            }},
        ],
    }
    existing = gh('api', f'repos/{name}/rulesets')
    matched = [item for item in existing if item['name'] == RULE_NAME]
    endpoint = f'repos/{name}/rulesets' + (f"/{matched[0]['id']}" if matched else '')
    gh('api', endpoint, '--method', 'PUT' if matched else 'POST', payload=rules)
    print(f'{name}: merge settings, private vulnerability reporting and {RULE_NAME} are active.')


if __name__ == '__main__':
    main()
