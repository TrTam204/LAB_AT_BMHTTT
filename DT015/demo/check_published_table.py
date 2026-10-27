"""Verify published aggregates, not a rerun on respondent-level data. Python 3.10+."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, platform, re, time, zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def extract_table(path):
    with zipfile.ZipFile(path) as z:
        document=ET.fromstring(z.read('word/document.xml'))
    table=document.findall('.//w:tbl',NS)[0]
    rows=[]
    for tr in table.findall('w:tr',NS):
        cells=[''.join(t.text or '' for t in c.findall('.//w:t',NS)).strip()
               for c in tr.findall('w:tc',NS)]
        if not cells or not re.fullmatch(r'[STO]P\.\s*\d+',cells[0]):continue
        if len(cells)!=7:raise ValueError(f'Unexpected table row: {cells}')
        code=re.sub(r'\s+','',cells[0])
        row=dict(zip(['process_id','name','mean','median','mode','sd','iqr'],[code]+cells[1:]))
        for key in ['mean','median','mode','sd','iqr']:row[key]=float(row[key])
        row['tier']={'SP':'Strategic','TP':'Tactical','OP':'Operational'}[code.split('.')[0]]
        row['consensus_from_published_aggregates']=row['median']>=4 and row['iqr']<=1
        rows.append(row)
    if len({r['process_id'] for r in rows})!=len(rows):raise ValueError('Duplicate process IDs')
    return rows

def main():
    path=ROOT/'sources/Appendix_A_D_original.docx'
    rows=extract_table(path)
    counts=Counter(r['tier'] for r in rows)
    assert counts=={'Strategic':6,'Tactical':11,'Operational':19},counts
    assert len(rows)==36 and all(r['consensus_from_published_aggregates'] for r in rows)
    for code,mean in [('TP.10',4.5),('OP.4',4.8),('OP.5',4.5),('OP.6',4.8)]:
        assert next(r for r in rows if r['process_id']==code)['mean']==mean
    (ROOT/'data').mkdir(exist_ok=True);(ROOT/'results').mkdir(exist_ok=True)
    with (ROOT/'data/published_round3.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'status':'PUBLISHED_AGGREGATE_CHECK_ONLY','input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'python':platform.python_version(),'source_table':'Appendix A, Table A1',
            'rows':len(rows),'tier_counts':dict(counts),
            'passes_published_consensus_rule':sum(r['consensus_from_published_aggregates'] for r in rows),
            'raw_ratings_available':False,'full_reproduction':False,
            'limitation':'Input is the published final table of retained processes. This does not re-estimate statistics or validate exclusions from raw data.'}
    runs=[]
    for i in range(3):
        t=time.perf_counter();again=extract_table(path)
        runs.append({'run':i+1,'identical_to_first':again==rows,'elapsed_seconds':round(time.perf_counter()-t,6)})
    result['deterministic_checks']=runs
    (ROOT/'results/published_table_check.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('DT015 - CHECK OF PUBLISHED TABLE A1')
    print('Published rows:',len(rows));print('Tier counts:',dict(counts))
    print('Published median >= 4 and IQR <= 1:',result['passes_published_consensus_rule'],'/ 36')
    print('Deterministic checks:',sum(r['identical_to_first'] for r in runs),'/ 3')
    print('LIMITATION: published aggregates only; original respondent ratings are missing.')
    print('This is NOT full reproduction, model training, or proof of improved results.')
    print('Outputs: data/published_round3.csv and results/published_table_check.json')

if __name__=='__main__':main()
