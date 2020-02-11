import os

from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:mysql@localhost:33006/test")


def file_name(file_dir):
    dic = {}
    for root, dirs, files in os.walk(file_dir):
        if len(dic.keys()) >= 1000:
            break
        if len(files) != 0:
            # files 里面的内容转换为元组
            dic[root] = list2tuples(files)
    return dic


def list2tuples(files: 'list') -> 'list':
    A_l = [str(f) for f in files if f.startswith('A')]
    A_l.sort()
    B_l = [str(f) for f in files if f.startswith('B')]
    B_l.sort()
    ans = []
    for a in A_l:
        find = False
        for b in B_l:
            if a[2:] == b[2:]:
                ans.append((a, b))
                find = True
        if not find:
            ans.append((a, None))
    # 反过来
    item = [x[1] for x in ans]
    for b in B_l:
        if b is not None and b not in item:
            ans.append((None, b))
    return ans


def diff(resource: str, target: str, form: str = 'diff') -> str:
    """
    Fetch the diff between the two files
    :param resource:
    :param target:
    :param form: Default axmldiff
    others:
        diff : return the plain text
        jsondiff : return the diff in json format
        dotdiff : return the diff in dot format
    :return:
    """
    pre_com = 'sh gumtree/bin/gumtree '
    command = pre_com + form + \
              ' ' + resource + ' ' + target
    return os.popen(command).read()


if __name__ == '__main__':
    print()
    # ./gumtree cluster ../../download/2dxgujun/AndroidTagGroup/11d981bb90c102fb9f89e653942d9d27c4c25114/B@TagGroup.java ../../download/2dxgujun/AndroidTagGroup/11d981bb90c102fb9f89e653942d9d27c4c25114/A@TagGroup.java

    # df = pd.DataFrame()
    # file_map = file_name('download')
    # os.system('mkdir result')
    # df = pd.DataFrame()
    # for k, v in file_map.items():
    #     root_path = k
    #     base = root_path[len('download/'):].replace('/', '@')
    #     file_tuples = v
    #     li = root_path.split('/')
    #     target_url = "https://github.com/{}/{}/commit/{}".format(li[1], li[2], li[3])
    #     print('url is {}'.format(target_url))
    #     html = requests.get(target_url)
    #     bsObj = BeautifulSoup(html.text, "html.parser")
    #     commit_msgs = bsObj.findAll("p", {"class": "commit-title"})
    #     # data to put into db
    #     msg = [obj.get_text().strip() for obj in commit_msgs][0]
    #     diffs = []
    #     for i, f in enumerate(file_tuples):
    #         A_path = '{}/{}'.format(k, f[0]) if f[0] is not None else 'none.java'
    #         B_path = '{}/{}'.format(k, f[1]) if f[1] is not None else 'none.java'
    #         if f[0] is not None:
    #             name = str(f[0][2:])[:-5]
    #         else:
    #             name = str(f[1][2:])[:-5]
    #         if A_path != 'none.java' and B_path != 'none.java':
    #             # 把信息保存
    #             action = json.loads(diff(A_path, B_path, form='jsondiff'))['actions']
    #             diffs.append(action)
    #     # 数据写入
    #     data = {
    #         'message': msg,
    #         'diff': json.dumps(diffs)
    #     }
    #     df = df.append([data], ignore_index=True)
    #     # df.to_sql('git_commits', con=engine, if_exists='append', index=False)
    #     print(df)
    #     df.to_csv('git-diff.csv')
