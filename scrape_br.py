from urllib import request, error
from collections import Counter
path = "./clean_mvote_logs.txt"
maps = {'vadso', 'kozelsk', 'kokan', 'route', 'mestia', 'grozny', 'brecourt',
        'dovre', 'masirah', 'shijia', 'burning', 'barracuda', 'battle',
        'charlies', 'silent', 'omaha', 'qwai', 'ramiel', 'masri',
        'wanda', 'merville', 'goose', 'carentan', 'musa', 'korengal',
        'nuijamaa', 'karbala', 'kashan', 'bamyan', 'muttrah', 'black',
        'xian', 'pavlovsk', 'basrah', 'falk', 'lashkar',
        'beirut', 'hill', 'jabal', 'sahel', 'reichswald', 'yamalia',
        'asad', 'saar', 'fallu', 'fools', 'shah', 'bijar',
        'tad', 'adak', 'outpost', 'gaza', 'iron', 'kaf',
        'khami', 'sbeneh', 'hades', 'bobcat', 'falcon', 'uly',
        'ghost', 'marl', 'soul', 'thund', 'dragon'}
map_counts = {}
for m in maps:
    map_counts[m] = 0
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
        for m in map_counts:
            if m in name:
                map_counts[m] += count
    sorted_map_count = {k: v for k, v in sorted(map_counts.items(), key=lambda i: i[1], reverse=True)}
    print(sorted_map_count)