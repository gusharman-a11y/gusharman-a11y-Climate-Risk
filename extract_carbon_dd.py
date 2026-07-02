import json, pathlib
raw = pathlib.Path(r'C:\Users\ANGUS~1.HAR\AppData\Local\Temp\claude\C--Users-angus-harman\8afa0a21-674f-4471-a1f3-e99bd6ccb3ec\tasks\worzkj0mo.output').read_text(encoding='utf-8')
data = json.loads(raw)
result = data['result']
pathlib.Path('carbon_dd_results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(f"Carbon: {len(result.get('carbon',[]))} | News: {len(result.get('news',[]))}")
for c in result.get('carbon',[]):
    print(f"  [{c.get('confidence','?'):7}] {c.get('company','')[:45]}")
