from pathlib import Path
import json
from fractions import Fraction
from bisect import bisect
import math

from header_template import template


class MalodyChart:
    def __init__(self, mc_filepath: Path):
        with mc_filepath.open(encoding='utf-8') as f:
            content = f.read().strip()
        self.malody_chart = json.loads(content)
        if self.malody_chart['meta']['mode'] != 0:
            raise RuntimeError(str(mc_filepath) + ' is not a keyboard map.')
        self.col_count = int(self.malody_chart['meta']['mode_ext']['column'])

    @staticmethod
    def bpm2ms_per_beat(bpm):
        return 60 * 1000 / bpm

    @staticmethod
    def beat2frac(beat):
        return beat[0] + Fraction(beat[1], beat[2])

    @staticmethod
    def time_obj2key(time_obj):
        return MalodyChart.beat2frac(time_obj['beat'])

    @staticmethod
    def calc_bpm_offset(bpm_sorted):
        bpm_offsets = []
        prev_offset = 0
        prev_beat_frac = 0
        prev_bpm = 0
        for time_obj in bpm_sorted:
            curr_beat_frac = MalodyChart.beat2frac(time_obj['beat'])
            beat_dist = curr_beat_frac - prev_beat_frac
            curr_offset = prev_offset + beat_dist * prev_bpm

            bpm_offsets.append(curr_offset)

            prev_offset = curr_offset
            prev_beat_frac = curr_beat_frac
            prev_bpm = MalodyChart.bpm2ms_per_beat(time_obj['bpm'])
        return bpm_offsets

    @staticmethod
    def make_timing_points(time: int, bpm):
        return f'{int(time)},{MalodyChart.bpm2ms_per_beat(bpm)},4,2,0,75,1,0'

    def make_hit_object(self, col: int, start: int, end: int = None):
        """

        :param col: index of lane, starts from 0
        :param start: start timestamp(ms)
        :param end: end timestamp(ms) if it is a hold
        :return: str
        """
        lane_width = 512 / self.col_count
        x = int(math.floor((col + 0.5) * lane_width))
        start = int(start)

        if end is None:
            return f'{x},192,{start},1,0,0:0:0:0:'
        else:
            end = int(end)
            return f'{x},192,{start},128,0,{end}:0:0:0:0:'

    def get_osu_chart(self):
        bpm_raw = self.malody_chart['time'][:]
        notes_raw = self.malody_chart['note'][:]

        global_offset = -notes_raw[-1]['offset']  # 这东西和osu的反着来的

        bpm_sorted = sorted(bpm_raw, key=MalodyChart.time_obj2key)
        bpm_offsets = MalodyChart.calc_bpm_offset(bpm_sorted)
        bpm_offsets = [bpm_offset + global_offset for bpm_offset in bpm_offsets]
        bpm_keys = [MalodyChart.time_obj2key(time_obj) for time_obj in bpm_sorted]

        osu_timing_points = []
        for i, time_obj in enumerate(bpm_sorted):
            osu_timing_points.append(MalodyChart.make_timing_points(bpm_offsets[i], time_obj['bpm']))

        notes = notes_raw[:-1]
        notes = sorted(notes, key=MalodyChart.time_obj2key)

        curr_bpm_offset_idx = 0

        def get_offset_ms(beat_frac, bpm_offset_idx: int):
            return ((beat_frac - bpm_keys[bpm_offset_idx])
                    * MalodyChart.bpm2ms_per_beat(bpm_sorted[bpm_offset_idx]['bpm'])
                    + bpm_offsets[bpm_offset_idx])

        osu_hit_objects = []
        for note in notes:
            col = note['column']
            start_beat_frac = MalodyChart.beat2frac(note['beat'])

            while (curr_bpm_offset_idx < len(bpm_keys) - 1) and start_beat_frac >= bpm_keys[curr_bpm_offset_idx + 1]:
                curr_bpm_offset_idx += 1
            start = get_offset_ms(start_beat_frac, curr_bpm_offset_idx)

            osu_hit_obj = ''
            if 'endbeat' in note:
                end_beat_frac = MalodyChart.beat2frac(note['endbeat'])
                endbeat_bpm_offset_idx = bisect(bpm_keys, end_beat_frac) - 1
                end = get_offset_ms(end_beat_frac, endbeat_bpm_offset_idx)
                osu_hit_obj = self.make_hit_object(col, start, end)
            else:
                osu_hit_obj = self.make_hit_object(col, start)

            osu_hit_objects.append(osu_hit_obj)

        return template.format(audio_name=notes_raw[-1]['sound'],
                               # offset=global_offset,
                               offset=0,
                               preview=self.malody_chart['meta']['preview']
                               if 'preview' in self.malody_chart['meta'] else -1,
                               title_ascii=self.malody_chart['meta']['song']['title'],
                               title_unicode=self.malody_chart['meta']['song']['titleorg']
                               if 'titleorg' in self.malody_chart['meta']['song'] else
                               self.malody_chart['meta']['song']['title'],
                               artist_ascii=self.malody_chart['meta']['song']['artist'],
                               artist_unicode=self.malody_chart['meta']['song']['artist'],
                               version=self.malody_chart['meta']['version']
                               if 'version' in self.malody_chart['meta'] else '0.1',
                               col_num=self.col_count,
                               bk=self.malody_chart['meta']['background'],
                               timing_points='\n'.join(osu_timing_points),
                               hit_objects='\n'.join(osu_hit_objects))
