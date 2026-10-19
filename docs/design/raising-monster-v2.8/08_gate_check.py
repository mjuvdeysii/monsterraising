#!/usr/bin/env python3
"""Raising Monster: evidence-completeness gate. Cannot establish that an app works.

Run: python docs/design/raising-monster-v2.8/08_gate_check.py --repo-root . --mode audit
     python docs/design/raising-monster-v2.8/08_gate_check.py --repo-root . --mode release
"""
import argparse
import csv
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
VALID_STATUSES = {"未核验", "待决策", "未实现", "开发中", "已实现待测", "已验证", "阻塞", "反复遗漏"}
BRAND_PENDING = {"BR-01", "BR-03"}


def csvrows(filename):
    with (HERE / filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def has_paths(raw, root):
    if not raw.strip():
        return False
    parts = [p.strip() for p in raw.replace('；', ';').split(';') if p.strip()]
    for item in parts:
        path = Path(item)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            return False
    return bool(parts)


def main():
    parser = argparse.ArgumentParser(description="Raising Monster evidence completeness checks; not a QA verdict")
    parser.add_argument('--repo-root', default='.', help='repository root for evidence file verification')
    parser.add_argument('--mode', choices=['audit', 'release'], default='audit')
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    req = csvrows('04_REQUIREMENTS.csv')
    qa = csvrows('05_QA_ANDROID_IOS.csv')
    screens = csvrows('reference_v2.7/04_47_Screen_Coverage.csv')
    issues = []
    warnings = []

    if len(screens) != 47:
        issues.append(f'Expected 47 baseline screens, actual {len(screens)}')
    if len(req) != len({r.get('Req_ID', '') for r in req}):
        issues.append('Duplicate Req_ID')
    if len(qa) != len({(r.get('Test_ID', ''), r.get('Platform', '')) for r in qa}):
        issues.append('Duplicate (Test_ID, Platform)')

    for r in req:
        rid, pri, status = r['Req_ID'], r['Priority'], r['Status']
        if status not in VALID_STATUSES:
            issues.append(f'{rid}: invalid status {status}')
        if not all(r.get(x, '').strip() for x in ['Screen_ID', 'Requirement', 'Acceptance_Criteria']):
            issues.append(f'{rid}: missing fundamental requirement columns')
        if status == '已验证':
            for x in ('Current_Code_Path', 'Commit_Hash'):
                if not r[x].strip():
                    issues.append(f'{rid}: marked 已验证 without {x}')
            if r['Android_Result'] != '通过' or r['iOS_Result'] != '通过':
                issues.append(f'{rid}: marked 已验证 without Android+iOS PASS')
            if not has_paths(r['Evidence_Paths'], repo_root):
                issues.append(f'{rid}: marked 已验证 without existing evidence files')
        if pri in ('P0', 'P1') and status != '已验证':
            if rid in BRAND_PENDING and status == '待决策':
                warnings.append(f'{rid}: brand decision pending; leave shipped name unchanged')
            else:
                issues.append(f'{rid}: unresolved {pri}, status={status}')

    for t in qa:
        key = f"{t['Test_ID']}/{t['Platform']}"
        if t['Actual_Result'] == '通过':
            for x in ('Device_And_OS', 'Build_Hash', 'Evidence_Path', 'Tester', 'Date'):
                if not t[x].strip():
                    issues.append(f'{key}: PASS missing {x}')
            if not has_paths(t['Evidence_Path'], repo_root):
                issues.append(f'{key}: PASS evidence file missing')
        if t['Priority'] in ('P0','P1') and t['Actual_Result'] != '通过':
            if t['Test_ID'] == 'T065':
                warnings.append(f'{key}: naming proposals pending user review; no renaming allowed')
            else:
                issues.append(f'{key}: unresolved {t["Priority"]}, result={t["Actual_Result"]}')

    for s in screens:
        key = s['Screen_ID']
        if not s.get('当前路由/组件（Claude填）', '').strip():
            issues.append(f'{key}: missing live route/component mapping')
        if s.get('最终状态') not in ('已验证', '保留未改已回归'):
            issues.append(f'{key}: baseline 47 screen not regression-verified')
        if s.get('Android验证') != '通过' or s.get('iOS验证') != '通过':
            issues.append(f'{key}: missing per-platform regression check')
        if not has_paths(s.get('实际证据路径',''), repo_root):
            issues.append(f'{key}: missing screen evidence')

    print(f'Raising Monster gate ({args.mode}); repository={repo_root}')
    print(f'Requirements: {len(req)}; QA platform runs: {len(qa)}; baseline screens: {len(screens)}')
    print('Requirements status:', dict(Counter(r['Status'] for r in req)))
    print('QA status:', dict(Counter(t['Actual_Result'] for t in qa)))
    print(f'Unresolved evidence/verification items: {len(issues)}; pending decisions: {len(warnings)}')
    if issues:
        for item in issues[:35]:
            print(' BLOCKED:', item)
        if len(issues) > 35:
            print(f' ... and {len(issues)-35} additional items; inspect CSV for all rows')
    if warnings:
        print('Decision warnings:', ' | '.join(warnings[:6]))
    print('IMPORTANT: A clean gate only means fields and files are present. Human review of real test content is still required.')
    if args.mode == 'release':
        if issues:
            print('RELEASE GATE: BLOCKED')
            return 2
        print('RELEASE GATE: EVIDENCE COMPLETE, pending human acceptance and platform approvals')
    else:
        print('AUDIT: incomplete items listed; this is expected before implementation')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
