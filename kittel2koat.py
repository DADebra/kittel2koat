#!/usr/bin/env python3

import re
import sys

relmatch = re.compile("([^(]+)\(([^)]*)\)")
varre = re.compile("[^-0-9+*/ ][^-+*/ ]*")

def displaymatch(match):
    if match is None:
        return None
    return '<Match: %r, groups=%r>' % (match.group(), match.groups())

rules = []

for line in sys.stdin:
    line = line.strip(" ").rstrip(" \n")
    arr_ind = line.find("->")
    if arr_ind < 0:
        continue
    pre, post, cond = line[0:arr_ind].strip(" ").rstrip(" "), line[arr_ind+2:].strip(" ").rstrip(" "), None
    lbr_ind = post.find("[")
    if lbr_ind >= 0:
        post, cond = post[0:lbr_ind].rstrip(" "), "[" + post[lbr_ind+1:]

    #print(repr(pre), repr(post), repr(cond))
    m = relmatch.match(pre)
    pre_rel, pre_vars = m.group(1), m.group(2).replace(", ", ",").split(',') if len(m.group(2)) > 0 else []
    m = relmatch.match(post)
    post_rel, post_vars = m.group(1), m.group(2).replace(", ", ",").split(',') if len(m.group(2)) > 0 else []

    rules.append((pre_rel, pre_vars, post_rel, post_vars, cond))

firstrel = rules[0][0]
maxvars = None
rel_vars = {}

for rule in rules:
    if rule[0] not in rel_vars:
        rel_vars[rule[0]] = []
        i = 0
        for var in rule[1]:
            rel_vars[rule[0]].append("VAR"+str(i))
            i += 1

for ri in range(0, len(rules)):
    pre_rel, pre_vars, post_rel, post_vars, cond = rules[ri]
    var_map = {}
    for i in range(0, len(pre_vars)):
        v = rel_vars[pre_rel][i]
        var_map[pre_vars[i]] = v
        pre_vars[i] = v

    for i in range(0, len(post_vars)):
        v = post_vars[i]
        for vf, vt in var_map.items():
            v = v.replace(vf, vt)
        post_vars[i] = v

    for i in range(0, len(post_vars)):
        v = post_vars[i]
        for var in varre.findall(v):
            if var not in rel_vars[pre_rel]:
                assert(v.find(" ") < 0)
                v = v.replace(var, rel_vars[post_rel][i])
        post_vars[i] = v

    if cond:
        for vf, vt in var_map.items():
            cond = cond.replace(vf, vt)

    if not maxvars or len(pre_vars) > len(maxvars):
        maxvars = pre_vars

    rules[ri] = (pre_rel, pre_vars, post_rel, post_vars, cond)


for ri in range(0, len(rules)):
    pre_rel, pre_vars, post_rel, post_vars, cond = rules[ri]

    for v in maxvars[len(pre_vars):]:
        pre_vars.append(v)

    for v in maxvars[len(post_vars):]:
        post_vars.append(v)

    #if len(post_vars) > len(pre_vars):
    #    for i in range(0, len(post_vars)):
    #        assert(post_vars[i].find(" ") < 0)
    #        v = rel_vars[post_rel][i]
    #        post_vars[i] = v

    rules[ri] = (pre_rel, pre_vars, post_rel, post_vars, cond)

print("(GOAL COMPLEXITY)")
print("(STARTTERM (FUNCTIONSYMBOLS " + firstrel + "))")
print("(VAR " + " ".join(maxvars) + ")")
print("(RULES")

for rule in rules:
    #print(rule)
    print("  " + rule[0] + "(" + ", ".join(rule[1]) + ") -> " +
        rule[2] + "(" + ", ".join(rule[3]) + ")" + (" " + rule[4] if rule[4] else ""))
print(")")
