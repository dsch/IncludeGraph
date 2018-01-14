import os
import re
from collections import defaultdict
import argparse
import logging

from graphviz import Digraph

p_include = re.compile(r'#include\s+(?:"(.*)"|<(.*)>)')
libc_headers = ['assert.h', 'complex.h', 'ctype.h', 'errno.h', 'fenv.h', 'float.h', 'inttypes.h', 'iso646.h',
                'limits.h', 'locale.h', 'math.h', 'setjmp.h', 'signal.h', 'stdalign.h', 'stdarg.h', 'stdatomic.h',
                'stdbool.h', 'stddef.h', 'stdint.h', 'stdio.h', 'stdlib.h', 'stdnoreturn.h', 'string.h', 'tgmath.h',
                'threads.h', 'time.h', 'uchar.h', 'wchar.h', 'wctype.h', ]

log = logging.getLogger(__name__)

include_map = defaultdict(list)
args = None


def process_file(root, file):
    log.debug('processing file "%s"', file)
    filename = os.path.join(root, file)
    for exclude in args.exclude:
        if re.search(exclude, filename):
            return
    with open(filename, 'r', encoding='iso8859-1') as f:
        inc_list = include_map[file]
        for l in f:
            match = p_include.match(l)
            if match:
                inc_file = match.group(1) or match.group(2)
                if args.nosysinc and inc_file in libc_headers:
                    continue
                inc_list.append(inc_file)


def include_graph(root):
    log.info('search for files in "%s"', root)
    walk_dir(root)
    graph = Digraph(format='svg')
    for node in include_map:
        graph.node(node)
    for node, inc in include_map.items():
        for i in inc:
            graph.edge(node, i)
    log.info('start rendering graph')
    graph.render('dependencies')


def walk_dir(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            ext = file.split('.')[-1]
            if ext in args.extension:
                process_file(root, file)
        for dir in dirs:
            walk_dir(dir)


def main():
    parser = argparse.ArgumentParser(description='Create include dependecy graph')
    parser.add_argument('--root', metavar='DIR', default='.',
                        help='root directory to scan')
    parser.add_argument('--extension', nargs='+', default=['h', 'c'],
                        help='file name extension to parse')
    parser.add_argument('--exclude', metavar='PATTERN', nargs='+',
                        help='regex pattern to exclude in path')
    parser.add_argument('--nosysinc', action='store_true',
                        help='ignore system includes')

    global args
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    include_graph(args.root)


if __name__ == '__main__':
    main()
