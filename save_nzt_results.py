import json, pathlib
raw = pathlib.Path(r'C:\Users\ANGUS~1.HAR\AppData\Local\Temp\claude\C--Users-angus-harman\8afa0a21-674f-4471-a1f3-e99bd6ccb3ec\tasks\wiu2gjlou.output').read_text(encoding='utf-8')
data = json.loads(raw)
results = data['result']
pathlib.Path('dd_nzt_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(f'{len(results)} results')
for r in results:
    conf = r.get('confidence', '')
    name = r.get('company_name', '')[:50]
    print(f'  [{conf:10}] {name}')
