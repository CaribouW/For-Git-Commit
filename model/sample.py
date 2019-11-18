import os

if __name__ == '__main__':
    path = "download"
    dirs = os.listdir(path)

    # 输出所有文件和文件夹
    for file in dirs:
        print(file)
