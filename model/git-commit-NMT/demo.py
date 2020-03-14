url = 'https://updates.jenkins-zh.cn/jenkins/plugins/{}/latest/{}.hpi'
with open('/Users/mac/Documents/docker images/jenkins/plugins.txt', 'r') as f:
    for line in f.readlines():
        line = line[:-1]
        res = line + ':::' + url.format(line, line)
        print(res)
