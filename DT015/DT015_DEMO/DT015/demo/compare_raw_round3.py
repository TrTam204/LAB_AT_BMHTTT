"""Run only after obtaining authentic raw ratings. No synthetic data are generated."""
import argparse, csv, hashlib, json, math, statistics
from collections import defaultdict
from pathlib import Path
from check_published_table import extract_table, ROOT

def summarize(values,quartiles,ddof):
    if len(values)<2:raise ValueError('At least two ratings required')
    if quartiles=='linear':
        x=sorted(values)
        def q(p):
            h=(len(x)-1)*p;i=int(h);return x[i]+(h-i)*(x[min(i+1,len(x)-1)]-x[i])
        iqr=q(.75)-q(.25)
    else:
        q=statistics.quantiles(values,n=4,method=quartiles);iqr=q[2]-q[0]
    return {'mean':statistics.mean(values),'median':statistics.median(values),
            'modes':statistics.multimode(values),
            'sd':statistics.stdev(values) if ddof==1 else statistics.pstdev(values),'iqr':iqr}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('raw_csv',type=Path,help='Columns: expert_id,process_id,rating. Authentic round-3 data only.')
    p.add_argument('--quartiles',choices=['linear','inclusive','exclusive'],required=True)
    p.add_argument('--ddof',type=int,choices=[0,1],required=True)
    args=p.parse_args();data=defaultdict(list);seen=set();experts=defaultdict(set)
    with args.raw_csv.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'expert_id','process_id','rating'}<=set(reader.fieldnames or []):raise ValueError('Missing required columns')
        for row in reader:
            expert=row['expert_id'].strip();pid=row['process_id'].strip()
            if not expert or not pid:raise ValueError('Empty identifier')
            key=expert,pid
            if key in seen:raise ValueError(f'Duplicate response: {key}')
            value=float(row['rating'])
            if not math.isfinite(value) or value not in (1,2,3,4,5):raise ValueError('Ratings must be integer values 1..5')
            seen.add(key);data[pid].append(value);experts[pid].add(expert)
    published=extract_table(ROOT/'sources/Appendix_A_D_original.docx')
    records=[]
    for pub in published:
        pid=pub['process_id']
        if len(data[pid])!=10:raise ValueError(f'{pid}: expected 10 round-3 ratings, got {len(data[pid])}')
        s=summarize(data[pid],args.quartiles,args.ddof)
        entry={'process_id':pid,'n':len(data[pid])}
        for metric,precision in [('mean',1),('median',2),('sd',2),('iqr',2)]:
            entry[metric]=s[metric];entry[metric+'_published']=pub[metric]
            entry[metric+'_matches_rounding']=abs(s[metric]-pub[metric])<=.5*10**(-precision)+1e-10
        entry['all_modes']=s['modes'];entry['published_mode_is_a_mode']=pub['mode'] in s['modes']
        entry['passes_consensus']=s['median']>=4 and s['iqr']<=1
        records.append(entry)
    panels=[experts[r['process_id']] for r in published]
    if any(panel!=panels[0] for panel in panels):raise ValueError('Inconsistent expert panel across the 36 processes')
    report={'status':'RAW_COMPARISON_REQUIRES_PROVENANCE_REVIEW','sha256':hashlib.sha256(args.raw_csv.read_bytes()).hexdigest(),
            'configuration':{'quartiles':args.quartiles,'ddof':args.ddof},
            'note':'The paper does not specify these computational conventions in the inspected material. Verify them against author code. Results concern the published 36-process subset only.',
            'unmatched_raw_processes':sorted(set(data)-{r['process_id'] for r in published}),
            'records':records}
    out=ROOT/'results/raw_round3_comparison.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Written:',out)
    print('Validate source provenance and every mismatch before claiming reproduction.')

if __name__=='__main__':main()
