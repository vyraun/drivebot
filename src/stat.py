#!/usr/bin/env python
import json
import sys
for line in sys.stdin:
    d = json.loads(line)
    print len(d)

#    rewards = [r['reward'] for r in d]
#    print sum(rewards), "\t", rewards

