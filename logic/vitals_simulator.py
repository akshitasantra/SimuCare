# logic/vitals_simulator.py
"""
Module to simulate patient vitals over time based on a predefined timeline.
Interpolates between key timepoints for continuous vitals values.

Usage:
    sim = VitalsSimulator(timeline)
    hr, spo2, bp, rr = sim.get_vitals(current_time)
"""

from bisect import bisect_right

class VitalsSimulator:
    def __init__(self, raw_timeline):
        """
        :param raw_timeline: list of dicts, each dict containing:
            {
              'time': int,
              'vitals': {
                  'HR': int,
                  'SpO2': int,
                  'BP': [sys, dia] or {'systolic': , 'diastolic': },
                  'RR': int
              }
            }
        """
        # Normalize and flatten 'vitals' into top-level keys
        normalized = []
        for pt in raw_timeline:
            base = {'time': pt['time']}
            vit = pt.get('vitals', {})
            base['HR'] = vit.get('HR')
            base['SpO2'] = vit.get('SpO2')
            bp = vit.get('BP')
            if isinstance(bp, (list, tuple)):
                base['BP'] = tuple(bp)
            elif isinstance(bp, dict):
                base['BP'] = (bp.get('systolic'), bp.get('diastolic'))
            else:
                base['BP'] = (None, None)
            base['RR'] = vit.get('RR')
            normalized.append(base)

        # Sort by time
        self.timeline = sorted(normalized, key=lambda x: x['time'])
        self.times = [pt['time'] for pt in self.timeline]

    def get_vitals(self, current_time):
        """
        Return interpolated vitals at the given time.
        If before first point, return first. If after last, return last.
        """
        if current_time <= self.times[0]:
            pt = self.timeline[0]
            return pt['HR'], pt['SpO2'], pt['BP'], pt['RR']
        if current_time >= self.times[-1]:
            pt = self.timeline[-1]
            return pt['HR'], pt['SpO2'], pt['BP'], pt['RR']

        # Find surrounding points
        idx = bisect_right(self.times, current_time)
        prev_pt = self.timeline[idx-1]
        next_pt = self.timeline[idx]

        # Fraction between times
        t0, t1 = prev_pt['time'], next_pt['time']
        frac = (current_time - t0) / (t1 - t0)

        # Interpolate each vital
        hr = int(prev_pt['HR'] + frac * (next_pt['HR'] - prev_pt['HR']))
        spo2 = int(prev_pt['SpO2'] + frac * (next_pt['SpO2'] - prev_pt['SpO2']))
        rr = int(prev_pt['RR'] + frac * (next_pt['RR'] - prev_pt['RR']))

        sys0, dia0 = prev_pt['BP']
        sys1, dia1 = next_pt['BP']
        sys = int(sys0 + frac * (sys1 - sys0)) if sys0 is not None else None
        dia = int(dia0 + frac * (dia1 - dia0)) if dia0 is not None else None

        return hr, spo2, (sys, dia), rr
