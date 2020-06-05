# duboku-downloader
复制链接，然后自定义下载第几集的独播库视频

#### 图形界面:
Windows-64 bit 用户可以下载 "独播库下载器_win_64_exe.zip", 解压缩后， 双击 "独播库下载器.exe" 文件执行。请确保附件 ffmpeg_minimal_ts_2_mp4.exe 与 "独播库下载器.exe" 在同一个目录。 

命令行爱好者也可以 python duboku_gui.py 打开。python3 用户必须先执行命令 `python3 -m pip install beautifulsoup4==4.7.1` 才能正常使用。Linux 用户请确保已安装了 `ffmpeg`。 python 用户的 pip 详细需求可以参考 requirements_py3_gui.txt 以及 requirements_py3_console.txt。

###### 安装 pycrypto 的需求， 例子:
python 3.6 用户请确保(apt)安装了 gcc, build-essential, python3.6-dev。 
python 3.8 用户请确保(apt)安装了 gcc, libpython3.8-dev。

#### 命令行界面:
请自行参考 `python duboku_console.py --help`。  

例子1(连续剧): python3 duboku_console.py https://www.duboku.net/vodplay/1324-1-11.html -d 冰糖炖雪梨/ --from-ep 1 -to-ep 5  
例子2(电影): python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校  
例子3(储存开 issue 需要的 duboku_epN.log): python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校 --debug   
例子4(代理): python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校 --proxy http://127.0.0.1:22

#### 注意事项:

1. 下载过程是先下载多段 .ts 文件，组成单个 .ts 文件， 完成后才转换去 .mp4，没有转换会导致某些播放器无法正常跳转或某部分模糊。请确保下载完毕不是 .ts 而是 .mp4。
2. 转换 .ts 去 .mp4 的过程会出现黑窗口几秒。
3. 重复下载 .ts/.mp4 会覆盖原本的同名 .ts/.mp4。如果转换 ts 去 mp4 失败可能不会保留 .ts。
4. 某段 .ts 下载失败会显示信息， 要不要重新下载该集取决于你。
5. 网络有时候慢导致下载失败， 就停止等一阵子才尝试。 

#### 示范视频 (点击图片会在 YouTube 打开):

[![watch in youtube](https://i.ytimg.com/vi/eejUgl7Ku8E/hqdefault.jpg)](https://www.youtube.com/watch?v=eejUgl7Ku8E "独播库下载器")


