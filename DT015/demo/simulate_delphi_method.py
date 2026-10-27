"""Illustrative Delphi statistics; NOT original expert responses from Liu et al. (2025).
Python 3.10+; only the standard library is needed.

Input:  data/delphi_ILLUSTRATIVE_ratings.csv
Output: results/delphi_ILLUSTRATIVE_statistics.csv
Quartiles use linear interpolation (a demonstration choice, NOT a confirmed paper convention).
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from statistics import mean, median, multimode, stdev
import csv
import math

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data' / 'delphi_ILLUSTRATIVE_ratings.csv'
OUTPUT = ROOT / 'results' / 'delphi_ILLUSTRATIVE_statistics.csv'


def percentile_linear(values: list[int], probability: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    return ordered[lower] + (index - lower) * (ordered[upper] - ordered[lower])


def load_ratings() -> dict[str, list[int]]:
    collected: dict[str, dict[str, int]] = defaultdict(dict)
    with SOURCE.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['process_id', 'expert_id', 'rating']:
            raise ValueError('CSV must have process_id, expert_id, rating')
        for record in reader:
            process = record['process_id'].strip()
            expert = record['expert_id'].strip()
            score = int(record['rating'])
            if not process or not expert or score not in (1, 2, 3, 4, 5):
                raise ValueError(f'Invalid row: {record}')
            if expert in collected[process]:
                raise ValueError(f'Duplicate expert for process {process}: {expert}')
            collected[process][expert] = score
    if not collected:
        raise ValueError('Empty illustrative dataset')
    for process, answers in collected.items():
        if set(answers) != {f'E{i}' for i in range(1, 11)}:
            raise ValueError(f'{process}: expected exactly E1..E10')
    return {name: [answers[f'E{i}'] for i in range(1, 11)]
            for name, answers in collected.items()}


def calculate(process_id: str, scores: list[int]) -> dict[str, object]:
    q1 = percentile_linear(scores, 0.25)
    q3 = percentile_linear(scores, 0.75)
    middle = median(scores)
    iqr = q3 - q1
    selected = middle >= 4 and iqr <= 1
    return {
        'process_id': process_id,
        'raw_ratings_E1_to_E10': ' '.join(map(str, scores)),
        'mean': round(mean(scores), 2),
        'median': round(middle, 2),
        'modes_all': '/'.join(map(str, multimode(scores))),
        'sd_sample_ddof1': round(stdev(scores), 2),
        'q1_linear': round(q1, 2),
        'q3_linear': round(q3, 2),
        'iqr_linear': round(iqr, 2),
        'passes_both_thresholds': selected,
    }


def main() -> None:
    print('=' * 76)
    print('DELPHI METHOD DEMONSTRATION - ILLUSTRATIVE SIMULATED DATA ONLY')
    print('NOT authentic responses from the Liu et al. paper.')
    print('Quartiles: linear interpolation (method not verified against authors).')
    print('=' * 76)
    data = load_ratings()
    records = [calculate(process, scores) for process, scores in data.items()]
    for record in records:
        print('\nCase:', record['process_id'])
        print('  E1..E10:', record['raw_ratings_E1_to_E10'])
        print(f"  Mean={record['mean']} Median={record['median']} Modes={record['modes_all']}")
        print(f"  Sample SD={record['sd_sample_ddof1']}; Q1={record['q1_linear']}; Q3={record['q3_linear']}; IQR={record['iqr_linear']}")
        print('  Median>=4 AND IQR<=1:', 'PASS' if record['passes_both_thresholds'] else 'NOT PASS')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    assert records[0]['mean'] == 3.8 and records[0]['median'] == 4 and records[0]['iqr_linear'] == 1.0
    assert [r['passes_both_thresholds'] for r in records] == [True, False, False]
    print('\nOutput:', OUTPUT.relative_to(ROOT))
    print('This proves understanding of the illustrative calculations, NOT full Delphi reproduction.')


if __name__ == '__main__':
    main()
