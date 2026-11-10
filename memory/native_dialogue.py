"""Native dialogue adapters for exact source-text extraction.
No semantic filtering or intellectual acceptance is performed.
"""
import collections,hashlib,json,re

def sha(b):
    return hashlib.sha256(b).hexdigest()

def canonical(x):
    return sha(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode())
SYSTEM_TAGS = ['<system-info\\b[^>]*>.*?</system-info>', '<system-reminder\\b[^>]*>.*?</system-reminder>', '<default aesthetic_system_instructions>.*?</default aesthetic_system_instructions>']
SYNTHETIC_PREFIX = ('This session is being continued from a previous conversation', 'The following is the Codex agent history', '# AGENTS.md instructions', '<subagent_notification>', '<environment_context>', '<permissions instructions>', '<developer_instructions>')

FLAT_MARKER=re.compile(r'(?m)^[ \t]*\[(thinking|redacted_thinking|tool_use|tool_result|image|document|audio|file)(?=[:\]])')

def flattened_protocol_ranges(text,protected):
    excluded=[];issues=[];position=0
    while match:=FLAT_MARKER.search(text,position):
        start=text.index('[',match.start(),match.end());kind=match.group(1)
        if any(a<=start<b for a,b in protected):position=match.end();continue
        reason='non_text_attachment' if kind in ('image','document','audio','file') else 'flattened_'+kind
        depth=0;quote=None;escape=False;end=None
        for i in range(start,len(text)):
            char=text[i]
            if quote:
                if escape:escape=False
                elif char=='\\':escape=True
                elif char==quote:quote=None
                continue
            if kind=='tool_use' and char in ('\"',"'"):
                quote=char;continue
            if char=='[':depth+=1
            elif char==']':
                depth-=1
                if depth==0:end=i+1;break
        if end is None:
            excluded.append((reason,start,len(text)));issues.append('Flattened native protocol boundary is incomplete; original retained for review');break
        if kind in ('image','document','audio','file') and text[end:end+1]=='(':position=end;continue
        if kind in ('thinking','redacted_thinking','tool_use','tool_result') and (text[:start].strip() or text[end:].strip()):
            # A scalar capture has no typed block boundary. Brackets inside a
            # payload cannot establish where following dialogue begins.
            excluded.append((reason,start,len(text)))
            issues.append('Mixed or ambiguous flattened protocol field retained native-only after its first protocol marker; typed source reconciliation required')
            break
        excluded.append((reason,start,end));position=end
    return excluded,issues

def visible_ranges(text, speaker, design=False, native_flattened=False, native_context=False):
    """Return exact substrings, never rewritten content. Recognized machine framing is separately accounted."""
    stripped = text.lstrip()
    if speaker == 'USER' and stripped.startswith(SYNTHETIC_PREFIX):
        return ([], [('synthetic_summary_or_instructions', 0, len(text))], [])
    if speaker == 'ASSISTANT' and stripped.startswith(('[external_agent_tool_call', '[external_agent_tool_result')):
        end = re.search('\\[/external_agent_tool_(?:call|result)\\]', text)
        if end and (not text[end.end():].strip()):
            return ([], [('external_agent_tool_execution', 0, len(text))], [])
        return ([], [('ambiguous_mixed_external_wrapper', 0, len(text))], ['External tool wrapper boundary does not encompass the complete record'])
    if speaker == 'USER' and stripped.startswith(('Access re-granted for ', 'Continuing from "')) and design:
        return ([], [('generated_navigation_or_access_context', 0, len(text))], [])
    excluded = [];issues=[]
    protected = [(m.start(), m.end()) for m in re.finditer('```.*?```|<pasted_text\\b[^>]*>.*?</pasted_text>', text, re.S)]
    if native_flattened:
        flat,issues=flattened_protocol_ranges(text,protected);excluded.extend(flat)
    if (design or native_context) and speaker == 'USER':
        for pattern in SYSTEM_TAGS:
            excluded.extend((('synthetic_injection', m.start(), m.end()) for m in re.finditer(pattern, text, re.S) if not any((a <= m.start() < b for a, b in protected))))
    if design and speaker == 'USER':
        excluded.extend((('pasted_text_wrapper', m.start(), m.end()) for m in re.finditer('</?pasted_text\\b[^>]*>', text)))
    marker = re.search('(?m)^## My request(?: for Codex)?:[ \\t]*\\n', text)
    if speaker == 'USER' and marker and stripped.startswith(('# Files', '# In app browser:', '# Browser')):
        excluded.append(('generated_attachment_or_browser_preface', 0, marker.end()))
    covered = []
    for reason, a, b in sorted(excluded, key=lambda v: v[1]):
        if covered and a < covered[-1][1]:
            continue
        covered.append((a, b, reason))
    spans = []
    pos = 0
    for a, b, reason in covered:
        if a > pos:
            spans.append((pos, a))
        pos = b
    if pos < len(text):
        spans.append((pos, len(text)))
    if not ''.join((text[a:b] for a, b in spans)).strip():
        return (spans, [(reason, a, b) for a, b, reason in covered], issues)
    return (spans, [(reason, a, b) for a, b, reason in covered], issues)

class Capture:

    def __init__(self, category, native, provider, title, snapshots):
        self.category = category
        self.native = native
        self.provider = provider
        self.title = title
        self.snapshots = snapshots
        self.records = []
        self.turns = []
        self.exceptions = []
        self.conflicts = []
        self.duplicates = 0
        self.context = {}
        self.replay = category == 'replayed_codex'

    def record(self, source, loc, nid, role, time, parent=None):
        rec = {'source_id': source, 'locator': loc, 'native_message_id': nid, 'native_role': role, 'timestamp_original': time, 'parent_native_message_id': parent, 'classification': 'excluded', 'exclusions': [], 'turns': []}
        self.records.append(rec)
        return rec

    def exclude(self, rec, reason, loc=None, **extra):
        rec['exclusions'].append({'reason': reason, 'locator': loc or rec['locator'], **extra})

    def text(self, rec, text, loc, speaker, design=False, native_flattened=False,native_context=False):
        try:
            text.encode('utf8')
        except UnicodeEncodeError:
            self.exclude(rec, 'unrenderable_visible_unicode', loc)
            self.exceptions.append({'locator': loc, 'issue': 'Unpaired surrogate in dialogue; no replacement applied'})
            return
        ranges, excluded, issues = visible_ranges(text, speaker, design,native_flattened,native_context)
        for reason, a, b in excluded:
            self.exclude(rec, reason, loc, start_character=a, end_character=b)
        for issue in issues:
            self.exceptions.append({'locator': loc, 'issue': issue})
        for a, b in ranges:
            if a != b:
                rec.setdefault('_parts', []).append({'source_id': rec['source_id'], 'locator': loc, 'start_character': a, 'end_character': b, 'text': text[a:b]})

    def finish_message(self, rec, speaker, *, allow_assistant_attachments=False):
        parts = rec.pop('_parts', [])
        attachment_reasons={'non_text_attachment','separate_attachment_content_or_reference'}
        attachment_reasons.update('native_only_'+kind for kind in ('image','input_image','audio','input_audio','file','document'))
        attachment_only=(speaker=='USER' or allow_assistant_attachments and speaker=='ASSISTANT') and any(e['reason'] in attachment_reasons for e in rec['exclusions'])
        if (not parts or not ''.join((p['text'] for p in parts)).strip()) and not attachment_only:
            if not rec['exclusions']:
                self.exclude(rec, 'empty_native_message_no_text')
            return
        self.turns.append({'speaker': speaker, 'native_message_id': rec['native_message_id'], 'timestamp_original': None if self.replay else rec['timestamp_original'], 'snapshot_observation_timestamp': rec['timestamp_original'] if self.replay else None, 'parent_native_message_id': rec['parent_native_message_id'], 'source_id': rec['source_id'], 'locator': rec['locator'], 'parts': parts, 'record_index': len(self.records) - 1})
        rec['classification'] = 'included' if not rec['exclusions'] else 'included_with_structural_exclusions'

def web(p, source, x, index, oldsource=None, old=None):
    prefix = '/' + str(index)
    oldmap = {m['uuid']: m for m in old['chat_messages']} if old else {}
    nativemap = {m['uuid']: m for m in x['chat_messages']}
    parents = {m['uuid']: m.get('parent_message_uuid') for m in x['chat_messages']}
    p.context['parent_map'] = parents
    for j, m in enumerate(x['chat_messages']):
        loc = source.get('locator_prefix', 'zip:conversations.json#') + prefix + '/chat_messages/' + str(j)
        rec = p.record(source['id'], loc, m['uuid'], m['sender'], m.get('created_at'), m.get('parent_message_uuid'))
        sp = 'USER' if m['sender'] == 'human' else 'ASSISTANT' if m['sender'] == 'assistant' else None
        if not sp:
            p.exclude(rec, 'unsupported_speaker')
            p.exceptions.append({'locator': loc, 'issue': 'Unknown native speaker'})
            continue
        prior = oldmap.get(m['uuid'])
        if prior and canonical(prior) != canonical(m):
            conflict = {'native_message_id': m['uuid'], 'old_source_id': oldsource['id'], 'new_source_id': source['id'], 'different_fields': [k for k in sorted(set(prior) | set(m)) if canonical(prior.get(k)) != canonical(m.get(k))], 'typed_visible_text_equal': [b.get('text') for b in prior['content'] if b.get('type') == 'text'] == [b.get('text') for b in m['content'] if b.get('type') == 'text'], 'old_record_sha256': canonical(prior), 'new_record_sha256': canonical(m)}
            p.conflicts.append(conflict)
        for k, b in enumerate(m.get('content', [])):
            bl = loc + '/content/' + str(k)
            typ = b.get('type')
            if typ == 'text':
                p.text(rec, b.get('text', ''), bl + '/text', sp)
            elif typ in ('thinking', 'redacted_thinking'):
                p.exclude(rec, 'internal_reasoning', bl)
            elif 'tool' in str(typ):
                p.exclude(rec, 'tool_execution', bl)
            elif typ == 'injected_prompt_block':
                p.exclude(rec, 'synthetic_memory_injection', bl)
            else:
                p.exceptions.append({'locator': bl, 'issue': 'Unrecognized native block: '+str(typ)}) if typ not in ('image','document','audio') else None
                p.exclude(rec, 'non_text_attachment' if typ in ('image', 'document', 'audio') else 'unknown_block_requires_review', bl)
        for k in ('attachments', 'files'):
            if m.get(k):
                p.exclude(rec, 'separate_attachment_content_or_reference', loc + '/' + k)
        if m.get('text') and not m.get('content'):
            p.exceptions.append({'locator':loc+'/text','issue':'Flattened-only message has no typed visible text; interpretation requires review'})
        if m.get('text'):
            p.exclude(rec, 'alternate_flattened_text_not_a_second_turn', loc + '/text')
        p.finish_message(rec, sp)
    if old:
        oldidx = next((i for i, v in enumerate(OLD) if v['uuid'] == old['uuid']))
        for j, m in enumerate(old['chat_messages']):
            rec = p.record(oldsource['id'], '/' + str(oldidx) + '/chat_messages/' + str(j), m['uuid'], m['sender'], m.get('created_at'), m.get('parent_message_uuid'))
            if m['uuid'] in nativemap:
                rec['classification'] = 'duplicate_source_observation'
                p.exclude(rec, 'same_native_message_snapshot_observation')
                p.duplicates += 1
                rec['typed_visible_text_agrees'] = [b.get('text') for b in m['content'] if b.get('type') == 'text'] == [b.get('text') for b in nativemap[m['uuid']]['content'] if b.get('type') == 'text']
            else:
                p.exclude(rec, 'older_message_absent_from_selected_snapshot')
                p.exceptions.append({'locator': rec['locator'], 'issue': 'Absent older message requires reconciliation; not deleted'})
    p.context['snapshot_message_counts'] = {'current': len(x['chat_messages']), 'previous': len(old['chat_messages']) if old else None}

def design(p, source, x, member):
    p.context['ordering'] = 'Native messages-array order; no native parent field. Branch completeness is unknown.'
    for j, m in enumerate(x['messages']):
        d = m['content']
        loc = 'zip:' + member + '#/messages/' + str(j)
        rec = p.record(source['id'], loc, m['uuid'], m['role'], m.get('created_at'))
        rec['inner_application_message_id'] = d.get('id')
        rec['inner_application_timestamp'] = d.get('timestamp')
        sp = 'USER' if m['role'] == 'user' else 'ASSISTANT' if m['role'] == 'assistant' else None
        if not sp:
            p.exclude(rec, 'unsupported_speaker')
            p.exceptions.append({'locator': loc, 'issue': 'Unknown native speaker'})
            continue
        if d.get('pill') and d.get('content', '').strip() in ('Re-running the check', 'Found issues — fixing…', 'Verifier agent check completed') and any(('<async_tool_result' in str(a.get('content', '')) or str(a.get('content', '')).startswith('The background verifier was interrupted') for a in d.get('attachments', []))):
            p.exclude(rec, 'generated_verifier_status')
            continue
        if d.get('kind') == 'chat-summary':
            p.exclude(rec, 'generated_chat_summary')
            continue
        if d.get('role') != m['role']:
            p.exclude(rec, 'role_conflict')
            p.exceptions.append({'locator': loc, 'issue': 'Outer and inner speaker disagree'})
            continue
        if sp == 'ASSISTANT' and d.get('contentBlocks') and (d['content'] != ''.join((b.get('text', '') for b in d['contentBlocks'] if b.get('type') == 'text'))):
            p.exclude(rec, 'ambiguous_visible_text_representations')
            p.exceptions.append({'locator': loc, 'issue': 'Design content and typed visible text differ'})
            continue
        p.text(rec, d.get('content', ''), loc + '/content/content', sp, True)
        for k, b in enumerate(d.get('contentBlocks', [])):
            typ = b.get('type')
            bl = loc + '/content/contentBlocks/' + str(k)
            if typ == 'text':
                p.exclude(rec, 'duplicate_visible_text_block_observation', bl)
            elif typ == 'thinking':
                p.exclude(rec, 'internal_reasoning', bl)
            elif typ == 'tool_call':
                p.exclude(rec, 'tool_execution', bl)
                try:
                    json.dumps(b, ensure_ascii=False).encode()
                except UnicodeEncodeError:
                    p.exclude(rec, 'unrenderable_unicode_in_excluded_tool_output', bl)
                    p.context.setdefault('unicode_exclusions', []).append(bl)
            else:
                p.exclude(rec, 'non_dialogue_design_event', bl)
        if d.get('attachments'):
            p.exclude(rec, 'separate_attachment_content_or_reference', loc + '/content/attachments')
        p.finish_message(rec, sp)


def stream_dialogue(capture, source, rows):
    """Interpret local JSONL incrementally. Internal records stay native-only."""
    for line_number,row in rows:
        location='line:'+str(line_number)
        if '_native_parse_error' in row:
            error=row['_native_parse_error'];capture.exceptions.append({'locator':location,'issue':'Unparseable native JSONL record at line '+str(error['line'])+', column '+str(error['column'])+': '+error['reason']});continue
        if source['provider']=='codex':
            payload=row.get('payload',{})
            if row.get('type')=='session_meta':
                capture.context.update({k:payload.get(k) for k in ('id','timestamp','history_mode','model_provider','forked_from_id','parent_thread_id')})
                origin=payload.get('source')
                if isinstance(origin,dict) and 'subagent' in origin:capture.context['native_only_auxiliary_agent']=True
            if capture.context.get('native_only_auxiliary_agent'):continue
            if row.get('type')!='response_item' or payload.get('type')!='message':continue
            if payload.get('channel')=='analysis' or payload.get('phase')=='analysis':continue
            role=payload.get('role'); native_id=payload.get('id'); timestamp=row.get('timestamp'); parent=None
            blocks=payload.get('content',[]); field=location+'#/payload/content'
        else:
            if row.get('uuid'):capture.context.setdefault('parent_map',{})[row['uuid']]=row.get('parentUuid')
            if row.get('type') not in ('user','assistant'):continue
            if row.get('isSidechain'):
                capture.context['auxiliary_agent_evidence']=True
                continue
            payload=row.get('message',{});role=payload.get('role',row['type']);native_id=row.get('uuid')
            timestamp=row.get('timestamp');parent=row.get('parentUuid');blocks=payload.get('content',[]);field=location+'#/message/content'
        if role not in ('user','assistant'):continue
        if row.get('isMeta') is True or row.get('isApiErrorMessage') is True:
            capture.context['native_metadata_events_excluded']=capture.context.get('native_metadata_events_excluded',0)+1
            continue
        if source['provider']=='claude' and row.get('sessionId'):capture.context.setdefault('native_session_ids',set()).add(row['sessionId'])
        record=capture.record(source['id'],location,native_id,role,timestamp,parent)
        if isinstance(blocks,str):capture.text(record,blocks,field,role.upper(),native_flattened=bool(source.get('_flattened_capture')),native_context=source['provider']=='claude')
        elif isinstance(blocks,list):
            for number,block in enumerate(blocks):
                if not isinstance(block,dict):
                    capture.exclude(record,'unrecognized_content_block',field+'/'+str(number));continue
                kind=block.get('type')
                if kind in ('text','input_text','output_text'):
                    capture.text(record,block.get('text',''),field+'/'+str(number)+'/text',role.upper(),native_context=source['provider']=='claude')
                else:
                    capture.exclude(record,'native_only_'+str(kind),field+'/'+str(number))
                    if kind not in ('image','input_image','output_image','audio','input_audio','file','document','tool_use','tool_result','thinking','redacted_thinking'):
                        capture.exceptions.append({'locator':field+'/'+str(number),'issue':'Unrecognized native content block requires review: '+str(kind)})
        else:
            capture.exclude(record,'unrecognized_message_content',field)
            capture.exceptions.append({'locator':location,'issue':'Native message content is not a string or block array'})
        capture.finish_message(record,role.upper())
        # Excluded execution records are not expanded into MESSAGES.yaml.
