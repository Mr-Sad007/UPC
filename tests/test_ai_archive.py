import json


def test_archive_appends_without_removing_user_notes(tmp_path, monkeypatch):
    from src import archive_ai
    monkeypatch.setattr(archive_ai, 'ROOT', tmp_path)
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/original_request.txt').write_text('Original exact query', encoding='utf-8')
    path = tmp_path/'session.jsonl'
    record = dict(type='response_item', payload=dict(type='message', role='assistant',
                  content=[dict(type='output_text', text='First visible output')]))
    path.write_text(json.dumps(record)+'\n', encoding='utf-8')
    archive_ai.archive(path)
    with (tmp_path/'AI_LOG.md').open('a', encoding='utf-8') as f:
        f.write('\nExact later user prompt: continue\n')
    before = (tmp_path/'AI_LOG.md').read_text(encoding='utf-8')
    record['payload']['content'][0]['text'] = 'Second visible output'
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record)+'\n')
    archive_ai.archive(path)
    after = (tmp_path/'AI_LOG.md').read_text(encoding='utf-8')
    assert after.startswith(before)
    assert 'Second visible output' in after
