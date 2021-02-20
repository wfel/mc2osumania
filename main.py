import argparse
from pathlib import Path
from chart import MalodyChart

parser = argparse.ArgumentParser()
parser.add_argument('input_filepath', metavar='input',
                    help='input file path')
parser.add_argument('output_filepath', metavar='output',
                    help='output file path')
args = parser.parse_args()

chart = MalodyChart(Path(args.input_filepath))
osu_chart = chart.get_osu_chart()

with Path(args.output_filepath).open('w', encoding='utf-8') as of:
    of.write(osu_chart)
