"""DT015: two transparent dataset demos, invoked by meaningful names.

From project root:
    wsl python3 d.py mo_phong
    wsl python3 d.py cong_bo

mo_phong: calculates statistics from illustrative individual scores.
cong_bo : checks the authors' published aggregate table in Appendix A.
These are NOT the same dataset, and neither reproduces the full Delphi survey.
"""
import csv
import runpy
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = 'Su dung: wsl python3 d.py mo_phong  HOAC  wsl python3 d.py cong_bo'


def run_simulated():
    source = ROOT / 'data' / 'delphi_ILLUSTRATIVE_ratings.csv'
    with source.open(newline='', encoding='utf-8-sig') as file:
        scores = [int(row['rating']) for row in csv.DictReader(file)
                  if row['process_id'] == 'EX_SP5_ILLUSTRATIVE']
    if len(scores) != 10 or any(score not in (1, 2, 3, 4, 5) for score in scores):
        raise ValueError('Vi du mo phong phai co dung 10 diem Likert tu 1 den 5.')

    # Inclusive quartiles use linear interpolation for Q1 and Q3.
    # This convention has NOT been verified as the article authors' convention.
    q1, _, q3 = statistics.quantiles(scores, n=4, method='inclusive')
    median = statistics.median(scores)
    iqr = q3 - q1

    print('=== DU LIEU MO PHONG DELPHI (KHONG PHAI PHIEU GOC) ===')
    print('Nguon:', source.relative_to(ROOT))
    print('Diem 10 chuyen gia GIA DINH:', scores)
    print('Mean = Tong diem / 10 =', f'{sum(scores)} / 10 = {statistics.mean(scores):.2f}')
    print(f'Median = {median:g} | Q1 = {q1:g} | Q3 = {q3:g} | IQR = {iqr:g}')
    print('Mode(s) =', ', '.join(map(str, statistics.multimode(scores))))
    print(f'SD mau = {statistics.stdev(scores):.2f}')
    print('DIEU KIEN: Median >= 4 VA IQR <= 1')
    print('KET LUAN:', 'DAT' if median >= 4 and iqr <= 1 else 'KHONG DAT')
    print('GIOI HAN: Tu phan vi tinh bang noi suy tuyen tinh;')
    print('          chua xac minh quy uoc cua tac gia.')


def run_published():
    source = ROOT / 'sources' / 'Appendix_A_D_original.docx'
    print('=== DU LIEU CONG BO: APPENDIX A - TABLE A1 ===', flush=True)
    print('Nguon:', source.relative_to(ROOT), flush=True)
    # Executes the real existing program: parses the original DOCX and creates CSV/JSON.
    runpy.run_path(str(ROOT / 'demo' / 'check_published_table.py'), run_name='__main__')
    output = ROOT / 'data' / 'published_round3.csv'
    print('\nDOI CHIEU MOT SO HANG TRONG BANG CONG BO:')
    with output.open(newline='', encoding='utf-8-sig') as file:
        for row in csv.DictReader(file):
            if row['process_id'] in ('SP.5', 'TP.10', 'OP.5'):
                print(f"{row['process_id']:5s}  Mean={row['mean']:4s}  "
                      f"Median={row['median']:4s}  IQR={row['iqr']}")
    print('GIOI HAN: Chi kiem chung thong ke da cong bo,')
    print('          KHONG tai lap tu phieu diem chuyen gia goc.')


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('mo_phong', 'cong_bo'):
        sys.exit(USAGE)
    if sys.argv[1] == 'mo_phong':
        run_simulated()
    else:
        run_published()


if __name__ == '__main__':
    main()
