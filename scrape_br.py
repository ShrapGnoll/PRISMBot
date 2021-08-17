from urllib import request, error
from collections import Counter
path = "./clean_mvote_logs.txt"
with open(path, "r") as logs:
    l = []
    mapvote_winners = []
    for line in logs:
        spl = line.split(" ")
        name = spl[6]
        if name == "user":
            name = spl[7]
        map_end_i = []
        vote_count_i = []
        pipes_i = []
        br = None
        for n, e in enumerate(spl):
            if e == "|":
                pipes_i.append(n)
            if e == "finished:":
                br = n
            elif e.endswith(":"):
                if spl[n + 1] != "Vote":
                    vote_count_i.append(n + 1)
        winners = [each.split(":")[0] for each in " ".join(spl[br + 1:]).split("|")]
        mapvote_winners.extend(winners)
        l.append(name)
    mapvote_winners = [each.lower().lstrip(" ").rstrip(" ") for each in mapvote_winners]
    c = Counter(mapvote_winners)
    sorted_count = {k: v for k, v in sorted(c.items(), key=lambda i: i[1], reverse=True)}
    for each in sorted_count:
        name = each
        count = sorted_count[each]
        print(name + ": Count: " + str(count))