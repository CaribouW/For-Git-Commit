FROM python
ENV PATH=/usr/local/bin:$PATH
ADD requirements.txt .
ADD diffSpider .
ADD gumtree .
#RUN apt-get update && apt-get install -y wget
#RUN wget https://npm.taobao.org/mirrors/node/v6.10.1/node-v6.10.1-linux-x64.tar.gz && \
#    tar -C /usr/local --strip-components 1 -xzf node-v6.10.1-linux-x64.tar.gz && \
#    rm node-v6.10.1-linux-x64.tar.gz
#RUN npm install -g dgit
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
CMD scrapy crawl diffSpider