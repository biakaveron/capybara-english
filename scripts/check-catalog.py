import json
from pathlib import Path
base=Path(__file__).resolve().parent.parent/'src'
catalog=json.loads((base/'curriculum.json').read_text(encoding='utf-8'))
dictionary=json.loads((base/'curriculum-vocab.json').read_text(encoding='utf-8'))
vocab={w['en']:w for w in dictionary['words']}
topics={t['id']:t for t in dictionary['topics']}
assert len(vocab)==len(dictionary['words']), 'Duplicate dictionary words'
assert len(topics)==len(dictionary['topics']), 'Duplicate dictionary topics'
for topic in topics.values():
    groups=topic.get('groups',[])
    assert len({g['id'] for g in groups})==len(groups),topic['id']
    for group in groups:assert group['title'] and any(w.get('group')==group['id'] and w['topic']==topic['id'] for w in vocab.values()),group['id']
for word in vocab.values():
    assert all(word.get(key) for key in ['en','ipa','ru','example','topic']),word['en']
    assert word['topic'] in topics,word['en']
    if topics[word['topic']].get('groups'):assert word.get('group') in {g['id'] for g in topics[word['topic']]['groups']},word['en']
def fingerprint(q):
    fields={k:q.get(k) for k in ['kind','stimulus','speech','complete','figure','hour','minute','acceptedText','pairs']}
    if 'choices' in q:fields['choices']=sorted(json.dumps(c,sort_keys=True) for c in q['choices'])
    return json.dumps(fields,sort_keys=True,ensure_ascii=False)
ids=set();checked=0
for m in catalog['modules']:
    practiced={fingerprint(q) for q in m['tasks']}
    if not m.get('practiceOnly'):assert len(m['assessmentTasks'])>=10,m['id']
    for q in m['assessmentTasks']:assert fingerprint(q) not in practiced,('Repeated practice example',q['id'])
    for q in m['tasks']+m['assessmentTasks']:
        assert q['id'] not in ids;ids.add(q['id']);assert q['moduleId']==m['id']
        scenes=[c['scene'] for c in q.get('choices',[]) if 'scene' in c]
        if q.get('figure',{}).get('type')=='scene':scenes.append(q['figure']['scene'])
        for scene in scenes:assert scene['word'] in vocab,(q['id'],scene['word'])
        if q['kind']=='choice':
            assert 0<=q['correct']<len(q['choices'])
            assert len(set(json.dumps(c,sort_keys=True) for c in q['choices']))==len(q['choices']),q['id']
        if q['kind']=='build':
            assert sorted(q['tokens'])==sorted(q['answer'])
            for answer in q['acceptedAnswers']:assert sorted(w.lower() for w in answer)==sorted(w.lower() for w in q['tokens'])
        if q['kind']=='matching':
            assert len(set(p['left'] for p in q['pairs']))==len(q['pairs'])
            assert len(set(p['right'] for p in q['pairs']))==len(q['pairs'])
        checked+=1
for mid in ['adventure-school','adventure-shop','adventure-day']:
    m=next(m for m in catalog['modules'] if m['id']==mid)
    assert len(m['tasks'])==8 and all(q.get('storyLead') for q in m['tasks'])
trace=next(m for m in catalog['modules'] if m['id']=='trace-letters')
assert ''.join(q['guide'] for q in trace['tasks'])=='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
print(f'PASS: {checked} catalog tasks, stable ids, distinct assessment material, picture references, answer banks, matching pairs, three coherent eight-step adventures and 26 letter outlines.')
