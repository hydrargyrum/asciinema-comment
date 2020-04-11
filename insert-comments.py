#!/usr/bin/env python3
# license: the Unlicense, see UNLICENSE file

import argparse
import json
import re


def pad_message(message, align, width):
    return '{{message:{align}{width}s}}'.format(**locals()).format(**locals())


def merge_iterables(*iterables, key=lambda x: x):
    def keyfunc(kv):
        return key(kv[1])

    def consume(iterator):
        try:
            value = next(iterator)
        except StopIteration:
            del iterables[iterator]
        else:
            iterables[iterator] = value

    iterables = {iter(it): None for it in iterables}
    for iterator in list(iterables):
        consume(iterator)

    while iterables:
        iterator, value = min(iterables.items(), key=keyfunc)
        yield value
        consume(iterator)


def inserts_to_records(fd, y, width):
    for line in fd:
        line = line.strip()
        m = re.fullmatch(
            r'(?P<start>\d+(?:\.\d*)?)'
            r'(?:\s*-\s*(?P<end>\d+(?:\.\d*)?)|\s*:\s*(?P<duration>\d+(?:\.\d*)?))?'
            r'(?:\s+(?P<style>[r<^>]+\s+)?(?P<message>.*))?',
            line,
        )
        if not m:
            raise NotImplementedError(f"oops: {line!r}")

        start = float(m['start'])

        end = None
        if m['end']:
            end = float(m['end'])

        duration = None
        if m['duration']:
            duration = float(m['duration'])
            end = start + duration

        message = m['message'] or ''

        style = m['style'] or ''
        align = (re.search('[<^>]', style) or ['^'])[0]

        rev_start = rev_end = ''
        if 'r' in style:
            rev_start = '\u001b[7m'
            rev_end = '\u001b[m'

        records = []

        padded = pad_message(message, align, width)
        records.append([start, 'o', f"\u001b[s\u001b[{y};1H{rev_start}{padded}{rev_end}\u001b[u"])
        if end:
            padded = pad_message('', '^', width)
            records.append([end, 'o', f"\u001b[s\u001b[{y};1H{padded}\u001b[u"])

        for data in records:
            line = json.dumps(data) + '\n'
            yield data, line


def parse_srt_time(strtime):
    m = list(map(int, re.search(r'(\d+):(\d+):(\d+),(\d+)', strtime).groups()))
    return m[0] * 3600 + m[1] * 60 + m[2] + m[3] / 1000


def srt_to_records(fd, y, width):
    while True:
        if not fd.readline():  # EOF
            break
        timestamps = fd.readline()

        message = ''
        for line in fd:
            if not line.strip():
                break
            message += line.strip()

        start, end = map(parse_srt_time, timestamps.split(' --> '))

        records = []
        padded = pad_message(message, '^', width)
        records.append([start, 'o', f"\u001b[s\u001b[{y};1H{padded}\u001b[u"])
        padded = pad_message('', '^', width)
        records.append([end, 'o', f"\u001b[s\u001b[{y};1H{padded}\u001b[u"])

        for data in records:
            line = json.dumps(data) + '\n'
            yield data, line


def rec_to_records(fd):
    for line in fd:
        data = json.loads(line)
        yield data, line


parser = argparse.ArgumentParser()
parser.add_argument('rec_file', type=argparse.FileType('r'))
parser.add_argument('inserts_file', type=argparse.FileType('r'))
parser.add_argument('output', type=argparse.FileType('w'))
parser.add_argument('--top', action='store_true', default=False)

args = parser.parse_args()

with args.rec_file, args.inserts_file:
    with args.output:
        line = args.rec_file.readline()
        data = json.loads(line)
        args.output.write(line)

        if args.top:
            y = 1
        else:
            y = data['height']

        if args.inserts_file.name.endswith('.srt'):
            subtitles_it = srt_to_records(args.inserts_file, y, data['width'])
        else:
            subtitles_it = inserts_to_records(args.inserts_file, y, data['width'])

        it = merge_iterables(rec_to_records(args.rec_file), subtitles_it)
        for data, line in it:
            args.output.write(line)
