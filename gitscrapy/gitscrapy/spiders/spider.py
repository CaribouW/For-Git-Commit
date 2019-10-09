import os
import re

import pandas as pd
import scrapy
from bs4 import BeautifulSoup
from sqlalchemy import create_engine


class GitSpider(scrapy.Spider):
    name = 'gitspider'
    git_url = 'https://github.com'  # 作为前缀
    git_api_url = 'https://api.github.com/repos'
    engine = create_engine('mysql+pymysql://root:mysql@39.105.74.179:3306/gitcommit?charset=utf8')  # 本地docker mysql
    raw_git_url = 'https://raw.githubusercontent.com'

    # commit
    # GET /repos/:owner/:repo/git/commits/:commit_sha

    def fetch_git_repos(self, file_name: 'str'):
        with open(file_name) as f:
            line = f.readlines()
        return [s.strip() for s in line]

    def hash_download(self, hashcode, source_path, target_path):
        # dgit facebook/react/src -r b5ac963

        pass
        # command = 'dgit {} -r {} {}'.format(source_path, hashcode, target_path)
        # return os.popen(command).read()

    def raw_load(self, content, path):
        with open(path, 'w') as f:
            f.write(content)
            # print('success store {}'.format(path))

    def start_requests(self):
        repo_list = self.fetch_git_repos('result.txt')
        diff_key_list = self.fetch_git_repos('keys.txt')
        for key in diff_key_list:
            data = pd.read_sql("select * from commitment c where c.diff = '{}'".format(key), self.engine)
            for index, row in data.iterrows():
                d = pd.read_sql("select * from hashdata h where h.hashcode = '{}'".format(row['hashcode']),
                                self.engine)
                for i, r in d.iterrows():
                    name = r['pname']
                    target = ''
                    for repo in repo_list:
                        if repo.endswith(name):
                            target = repo
                            break
                    yield scrapy.Request(url=self.git_url + target + "/commit/" + r['hashcode'])
        # for repo in repo_list:  # TODO
        #     name = repo.split('/')[-1]
        #     # 关联查询
        #     data = pd.read_sql("select * from hashdata h where h.pname = '{}' and h.hashcode in"
        #                        " (select c.hashcode from commitment c where c.diff in (select))".format(name), self.engine)
        #     for index, row in data.iterrows():
        #         yield scrapy.Request(url=self.git_url + repo + "/commit/" + row['hashcode'])

    def parse(self, response):
        txt = response.text
        url = response.url
        target_repo = re.findall(".*?github\\.com/(.*?)/commit.*?", url)[0]
        # 正则匹配获取根节点commit hash
        bsObj = BeautifulSoup(txt, "html.parser")
        ali = bsObj.findAll("a", {"class": "sha"})

        # parent hash
        parent_hash = [obj.get('href').split('/')[-1] for obj in ali][0]
        # curhash
        cur_hash = url.split('/')[-1]
        # 查找diff info
        sql_cmd = "select * from commitment where hashcode = '{}'".format(cur_hash)
        data = pd.read_sql(sql_cmd, self.engine)
        for index, row in data.iterrows():
            # 对于每一个被修改的文件
            diff = row['diff'].split()[2:]  # 获取源文件
            b_path = diff[1][2:]    # 一次hash的a 文件表示老版本, b 表示新版本 ; 当前hash下载b文件(cur hash)作为B;
                                    # parent下载b文件(parent hash)作为A
            sql_parent_cmd = "select * from commitment where hashcode = '{}' and diff = '{}'".format(cur_hash,
                                                                                                     row['diff'])
            parent_result = pd.read_sql(sql_parent_cmd, self.engine)
            if parent_result.empty:
                print('data error !')
                continue
            for i, r in parent_result.iterrows():
                a_path = r['diff'].split()[2][2:]

                a_source_path = '{}/{}'.format(target_repo, a_path)
                b_source_path = '{}/{}'.format(target_repo, b_path)
                # log.msg('a download from {} with hash {}'.format(a_source_path, parent_hash))
                # log.msg('b download from {} with hash {}'.format(b_source_path, cur_hash))

                a_fetch_url = "{}/{}/{}".format(target_repo, parent_hash, b_path)
                b_fetch_url = "{}/{}/{}".format(target_repo, cur_hash, b_path)

                # # 可以开始下载
                # # 1. 下载a 文件
                # self.hash_download(hashcode=parent_hash, source_path=a_source_path,
                #                    target_path='./download/{}/{}/a'.format(target_repo, cur_hash))
                #
                # # 2. 下载b 文件
                # self.hash_download(hashcode=cur_hash, source_path=b_source_path,
                #                    target_path='./download/{}/{}/b'.format(target_repo, cur_hash))
                yield scrapy.Request(url="{}/{}?href={}".format(self.raw_git_url,
                                                                b_fetch_url,
                                                                a_fetch_url),
                                     callback=self.fetBParse)

    def fetBParse(self, response):
        txt = response.text
        url = response.url
        li = re.split('\\?href=', url)
        B_fetch_uri = li[0].split(self.raw_git_url + '/')[1]
        A_fetch_uri = li[1]
        B_fetch_uri_li = B_fetch_uri.split('/')
        # 存储a
        cur_hash = B_fetch_uri_li[2]
        target_repo = B_fetch_uri_li[0] + '/' + B_fetch_uri_li[1]
        target_file = B_fetch_uri_li[-1]
        # 创建文件夹
        if not os.path.exists("./download/{}".format(target_repo)):
            repo_li = target_repo.split('/')
            os.system('mkdir ./download/{}'.format(repo_li[0]))
            os.system('mkdir ./download/{}'.format(target_repo))

        os.system('mkdir ./download/{}/{}'.format(target_repo, cur_hash))
        self.raw_load(txt, "./download/{}/{}/B@{}".format(target_repo,
                                                          cur_hash,
                                                          target_file))
        yield scrapy.Request(url='{}/{}?hash={}'.format(self.raw_git_url,
                                                        A_fetch_uri,
                                                        cur_hash),
                             callback=self.fetAParse)

    def fetAParse(self, response):
        txt = response.text
        url = response.url
        li = re.split('\\?hash=', url)
        cur_hash = li[1]
        fetch_uri = li[0].split(self.raw_git_url + '/')[1]
        fetch_uri_li = fetch_uri.split('/')
        # cur_hash = fetch_uri_li[2]
        target_repo = fetch_uri_li[0] + '/' + fetch_uri_li[1]
        target_file = fetch_uri_li[-1]
        self.raw_load(txt, "./download/{}/{}/A@{}".format(target_repo,
                                                          cur_hash,
                                                          target_file))
