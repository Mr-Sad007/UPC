"""Archive visible model messages and tool-call outputs, excluding hidden reasoning."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def archive(session_path):
    source = Path(session_path)
    records = []
    for line in source.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item.get('type') != 'response_item':
            continue
        payload = item.get('payload', {})
        if payload.get('type') == 'message' and payload.get('role') == 'assistant':
            content = [c.get('text', '') for c in payload.get('content', []) if c.get('type') == 'output_text']
            if content:
                records.append(dict(type='visible_assistant_message', text='\n'.join(content)))
        elif payload.get('type') in ['function_call', 'custom_tool_call']:
            records.append(dict(type='assistant_tool_call', name=payload.get('name'),
                                arguments=payload.get('arguments', payload.get('input', ''))))
    assert all(r['type'] in ['visible_assistant_message', 'assistant_tool_call'] for r in records)
    previous_path = ROOT/'docs/ai_output_snapshot.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else []
    assert records[:len(previous)] == previous, 'Existing output prefix changed; preserve the old log for manual reconciliation'
    original = (ROOT/'docs/original_request.txt').read_text(encoding='utf-8')
    header = ('# AI Use Log\n\nDate: 2026-11-07, Asia/Shanghai. System: OpenAI Codex; underlying model identifier is not asserted. '
              'Roles: source lookup, analysis, scientific programming, execution, figures, English drafting, numerical and layout review. '
              'An independent Codex reviewer checked scientific code and result claims.\n\n'
              'This is an exact project-prompt and model-output snapshot through the archive operation. '
              'Hidden reasoning, system/developer instructions and non-model tool-return transport are excluded. '
              'Numerical tool outputs are preserved in results/. Source outputs and prior revisions occur in the verbatim model tool-call archive. '
              'Later visible replies must be appended in a closing export.\n\n'
              'ANONYMITY: raw tool calls can contain local account paths. This internal record must not be attached to an anonymous submission without review. '
              'The official complete-output requirement and anonymity must both be checked by the team. No redaction is silently presented as exact output.\n\n'
              '## Exact initial project prompt\n\n~~~~text\n')
    parts = [] if (ROOT/'AI_LOG.md').exists() else [header, original, '\n~~~~\n\n## Exact visible assistant outputs and model tool calls\n']
    for i, record in enumerate(records[len(previous):], start=len(previous)):
        parts.append(f'\n### Output {i+1}: {record["type"]}\n\n')
        if record['type'] == 'visible_assistant_message':
            parts.extend(['~~~~text\n', record['text'], '\n~~~~\n'])
        else:
            parts.extend(['~~~~text\n', str(record['name']), '\n', record['arguments'], '\n~~~~\n'])
    with (ROOT/'AI_LOG.md').open('a', encoding='utf-8') as f:
        f.write(''.join(parts))
    (ROOT/'docs/ai_output_snapshot.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    metadata = dict(records=len(records), visible_messages=sum(r['type'] == 'visible_assistant_message' for r in records),
                    tool_calls=sum(r['type'] == 'assistant_tool_call' for r in records),
                    exact_project_prompt_retained=True, hidden_reasoning_included=False,
                    full_closing_export_still_requires_final_reply=True,
                    submission_anonymity_review_required=True)
    (ROOT/'docs/ai_snapshot_status.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('session_path')
    archive(parser.parse_args().session_path)
