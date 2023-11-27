"""
Various functions for timing and displaying progress of processes and iterations
"""

import sys
import time
import numpy as np


def time_update(start):
    """
    Returns a string of the time elapsed since start
    """
    seconds = time.perf_counter() - start
    mins = (np.round
            ((seconds // 60), 0))
    seconds = seconds % 60
    hours = mins // 60
    mins = mins % 60
    timer = f'{int(hours)}:{int(mins)}:{int(seconds)}'
    return timer


def progress_bar(start, filename, i, current, size, step):
    """
    Displays a progress bar in the terminal
    """
    timer = time_update(start)
    sys.stdout.write('\r')
    sys.stdout.write("%s | %s | %s | elapsed: %s | %d%%  %-20s" % (filename, current, step, timer,
                                                              ((i + 1) / size) * 100,
                                                              '#' * int(((i+1) / size) * 15)))
    sys.stdout.flush()


def short_step(start, step_str, i, total_steps):
    timer = time_update(start)
    sys.stdout.write('\r')
    sys.stdout.write("%s | elapsed: %s | %d%%  %-20s" % (step_str, timer,
                                                         (i / total_steps) * 100,
                                                         '#' * int((i / total_steps) * 15)))
    sys.stdout.flush()

    return