"""Fictional decision history, executed through the actual CLI in fresh processes."""
import hashlib
import json
import pathlib
import subprocess
import sys

PACKAGE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from tools.initialize import initialize
from memory.records import load, write, resolve_subject, atomic


def main(destination):
    root = initialize(destination)
    events = []

    def command(*args):
        argv = [sys.executable, '-m', 'memory.cli', '--root', str(root), *args]
        result = subprocess.run(argv, cwd=PACKAGE, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(f'{args}: {result.stderr or result.stdout}')
        output = json.loads(result.stdout)
        events.append({'command': ['python', '-m', 'memory.cli', '--root', 'DEMO_ROOT', *args], 'output': output})
        return output.get('result', output) if isinstance(output, dict) else output

    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.STDOUT, text=True).strip()

    def commit(message):
        git('add', '.')
        git('-c', 'user.name=Fictional Reviewer', '-c', 'user.email=reviewer@example.invalid',
            'commit', '-m', message + '\n\nMemory-Operator: synthetic-reviewer\nMemory-Session: fictional-demo')
        return git('rev-parse', 'HEAD')

    git('init', '-b', 'review')
    commit('Initialize fictional memory repository')
    subject = command('create-subject', 'Fictional lantern controller', '--slug', 'lantern', '--scope', 'Fictional control policy')
    sid = subject['subject_id']
    decisions = [
        [('user', 'Consider a fixed timer and a sensor for the fictional lantern.'),
         ('assistant', 'A sensor might adapt to changing light; a timer is simpler.'),
         ('user', 'Choose the fixed timer initially because its operation is predictable. Reject sensor-only control until its failure behavior is reviewed.')],
        [('user', 'Revise the decision: use a sensor with a timer fallback because the fallback preserves predictable operation. The timer-only decision is superseded.'),
         ('assistant', 'A future adaptive schedule is another possible approach.'),
         ('user', 'Keep the adaptive schedule unresolved. Start documenting the fallback procedure.')]
    ]
    evidence = []
    originals = {}
    for number, messages in enumerate(decisions, 1):
        data = {'native_conversation_id': f'fictional-lantern-{number}', 'title': f'Fictional lantern revision {number}',
                'messages': [{'native_message_id': f'{number}-{n}', 'role': role, 'content': text,
                              'source_locator': f'messages[{n}]'} for n, (role, text) in enumerate(messages)]}
        intake = root / 'DEMO_INPUTS'; intake.mkdir(exist_ok=True)
        native = intake / f'conversation-{number}.json'
        native.write_text(json.dumps(data, indent=2) + '\n')
        export = command('register-export', str(native), '--provider', 'fictional', '--environment', 'synthetic',
                         '--scope', 'Complete fictional example authored for this demonstration', '--completeness', 'complete')
        original = root / export['source_files'][0]['path']
        originals[str(original.relative_to(root))] = hashlib.sha256(original.read_bytes()).hexdigest()
        commit(f'Preserve fictional original {number}')
        sot = command('register-sot', export['export_id'], str(native))
        source = next(root.glob(f"SOT/*/*/*/{sot['sot_id']}/manifest.yaml"))
        mids = [m['message_id'] for m in load(source.parent / 'MESSAGES.yaml')['messages']]
        ref = {'sot_id': sot['sot_id'], 'message_ids': [mids[2] if number == 1 else mids[0]]}
        evidence.append(ref)
        command('set-attachment-inventory', sot['sot_id'], '--expected', '0', '--verification', 'verified',
                '--evidence', f"export {export['export_id']}: fictional source has no attachments")
        for index, classification in ([(0, 'user_proposal'), (1, 'model_suggestion'), (2, 'established_user_position'), (2, 'rejected_or_superseded')]
                                      if number == 1 else [(0, 'established_user_position'), (0, 'rejected_or_superseded'), (1, 'model_suggestion'), (2, 'unresolved_interpretation')]):
            command('associate-source', sid, sot['sot_id'], mids[index], '--classification', classification,
                    '--description', messages[index][1], '--occurred-at', f'2026-01-0{number}')
        # The source explicitly establishes these fictional positions. This is a reviewed edit,
        # not automatic promotion by associate-source.
        p, _ = resolve_subject(root, sid)
        current = p.parent / 'CURRENT.md'
        old = current.read_text()
        value = 'Fixed timer; sensor-only rejected pending failure review.' if number == 1 else 'Sensor with timer fallback; timer-only superseded; adaptive schedule unresolved.'
        sections = old.split('## Established Current Position\n', 1)
        tail = sections[1].split('\n## ', 1)[1]
        atomic(current, sections[0] + '## Established Current Position\n\n' + value + '\n\n## ' + tail)
        command('render-agenda')
        command('validate')
        commit(f'Review fictional decision {number}; preserve prior reasoning')
    work = command('create-work', 'Document fictional fallback procedure', '--type', 'documentation')
    wid = work['work_item_id']
    workpath = root / f'WORK/ITEMS/work_{wid}.md'
    record, body = load(workpath)
    record['subject_ids'] = [sid]
    record['source_refs'] = evidence
    record['resumption']['current_position'] = 'Document the sensor and timer fallback decision.'
    record['resumption']['source_refs'] = evidence
    write(workpath, record, body)
    command('render-agenda')
    evidence_path = root / 'DEMO_INPUTS/evidence.json'
    evidence_path.write_text(json.dumps([evidence[-1]]))
    command('transition-work', wid, 'active', '--reason', 'Explicit fictional instruction to start documentation', '--evidence', str(evidence_path))
    command('validate')
    commit('Record fictional operational continuity')
    # Each invocation uses a new Python process, with no conversational memory.
    recovered = command('resolve-subject', sid)
    assert 'Sensor with timer fallback' in recovered['current']
    assert 'Fixed timer' not in recovered['current']
    history = (root / recovered['history_path']).read_text()
    assert 'predictable' in history and 'superseded' in history
    command('resolve-work', wid)
    for ref in evidence:
        command('resolve-source', ref['sot_id'], '--message-id', ref['message_ids'][0])
    assert not [f for f in command('validate') if f['severity'] == 'ERROR']
    for rel, expected in originals.items():
        assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == expected
    report = {'synthetic': True, 'external_model_executed': False, 'subject_id': sid, 'work_item_id': wid,
              'original_hashes_verified': originals, 'events': events, 'result': 'PASS'}
    (root / 'DEMO_RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': 'PASS', 'subject_id': sid, 'work_item_id': wid,
                      'report': str(root / 'DEMO_RESULT.json'), 'external_model_executed': False}, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python examples/demo.py EMPTY_DESTINATION')
    main(pathlib.Path(sys.argv[1]))
