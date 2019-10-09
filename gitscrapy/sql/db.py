import json
import os


def analyse_pure_json(json_str):
    f = open(json_str, encoding='utf-8')
    js = json.load(f)
    ans = []
    for txt in js:
        li = txt.split('\n')
        for line in li:
            if str(line).startswith('diff --git'):
                ans.append(line + '\n')
    os.system('touch keys.txt')
    with open('keys.txt', 'w') as f:
        f.writelines(ans)


if __name__ == '__main__':
    analyse_pure_json('difftextV12.json')
