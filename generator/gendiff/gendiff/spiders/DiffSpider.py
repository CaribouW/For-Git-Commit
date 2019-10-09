import os

import scrapy


def diff(resource: str, target: str, form: str = 'jsondiff') -> str:
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


class DiffSpider(scrapy.Spider):
    name = 'diffSpider'

    def start_requests(self):
        file_map = file_name('download')
        os.system('mkdir result')
        for k, v in file_map.items():
            root_path = k
            base = root_path[len('download/'):].replace('/', '@')
            file_tuples = v
            for i, f in enumerate(file_tuples):
                A_path = '{}/{}'.format(k, f[0]) if f[0] is not None else 'none.java'
                B_path = '{}/{}'.format(k, f[1]) if f[1] is not None else 'none.java'
                if f[0] is not None:
                    name = str(f[0][2:])[:-5]
                else:
                    name = str(f[1][2:])[:-5]

                di = diff(A_path, B_path)
                output_path = '{}/{}.json'.format(base, name)
                os.system('mkdir result/{}'.format(base))
                with open('result/{}'.format(output_path), 'w') as file:
                    file.write(di)

    def parse(self, response):
        pass
