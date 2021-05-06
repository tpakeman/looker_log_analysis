from datetime import datetime as dt
import re

def timer(func):
    def wrapper(*args, **kwargs):
        start = dt.now()
        result = func (*args, **kwargs)
        end = dt.now()
        elapsed = (end - start).total_seconds()
        print(f'Function {func.__name__} executed in {elapsed:.2f} seconds')
        return result
    return wrapper

@timer
def with_startswith(lines):
    out = []
    for line in lines:
        if line.startswith('2021'):
            out.append(line)
    return out

@timer
def with_startswithtuple(lines):
    out = []
    for line in lines:
        if line.startswith(('2021-', '2020-', '2019-')):
            out.append(line)
    return out

@timer
def with_regex(lines):
    LINESTART = re.compile(r'^\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\.\d{3} \+\d{4} \[')
    out = []
    for line in lines:
        if re.match(LINESTART, line):
            out.append(line)
    return out

def generate_sample(n, bad_pc=0.1):
    goodline = '2021-02-24 07:03:49.609 +0000 [INFO|foo|db:looker] :: (0.063s) CALL IDENTITY()'
    badline = 'MFTQTWniuMKXvOxhVUKdrF3e40CKwRqsSaTjN3GhX8HdywdMxOyuCTukE+Fr'
    return [badline if i % int(1 / bad_pc) == 0 else goodline for i in range(n)]

def main():
    n = 1000000
    bad = 0.1
    lines = generate_sample(n, bad)
    print(f"Testing with {n:,} lines, {bad:.2%} bad:")
    with_startswith(lines)
    with_startswithtuple(lines)
    with_regex(lines)

if __name__ == '__main__':
    main()
