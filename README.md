# duboku-downloader
复制链接，然后自定义下载第几集的独播库视频

---
### 普通用户:
Windows (64-bit) 用户，只需要下载 "独播库下载器_win_64_exe.zip", 解压缩后， 双击 "独播库下载器.exe" 文件执行。 

---
### python 3 用户:

根据你的平台选择 linux_source 或 win_64_source 目录。

你可以 `python3 duboku_gui.py` 打开图形界面，或 `python3 duboku_console.py -选项` 使用命令行界面。

python3 用户必须先执行命令 `python3 -m pip install beautifulsoup4==4.7.1` 才能正常使用。 其余 `pip` 的依赖请参考 requirements_py3_gui.txt(图形界面) 或 requirements_py3_console.txt(命令行) 文件。

Linux 用户请确保安装了 `ffmpeg` 命令。 

Windows 用户如果不想使用我编译的 ffmpeg_minimal_ts_2_mp4.exe， 只需修改 `duboku_gui.py` 的 `'./ffmpeg_minimal_ts_2_mp4'` 去你的 ffmpeg 路径， 抑或自行下载 ffmpeg 后命名成 fmpeg_minimal_ts_2_mp4 替代。

###### 命令行界面的用法:
请自行参考 `python3 duboku_console.py --help`。

例子1(连续剧): `python3 duboku_console.py https://tv.newsinportal.com/vodplay/1324-1-11.html -d 冰糖炖雪梨/ --from-ep 1 -to-ep 5`    

例子2(电影): `python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校`  

例子3(储存开 issue 需要的 duboku_epN.log 日志): `python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校 --debug`   

例子4(代理): `python3 duboku_console.py https://www.duboku.net/voddetail/1152.html -f 返校 --proxy http://127.0.0.1:22`

---
### 注意事项:

1. 下载过程是先下载多段 .ts 文件，组成单个 .ts 文件， 完成后才转换去 .mp4，没有转换会导致某些播放器无法正常跳转或某部分模糊。请确保下载完毕不是 .ts 而是 .mp4。
2. 重复下载 .ts/.mp4 会覆盖原本的同名 .ts/.mp4。如果转换 ts 去 mp4 失败可能不会保留 .ts。
3. 某段 .ts 下载失败会显示信息， 要不要重新下载该集取决于你。
4. 网络有时候慢导致下载失败， 就停止等一阵子才尝试。 

---
### 示范视频 (点击图片会在 YouTube 打开):

[![watch in youtube](https://i.ytimg.com/vi/eejUgl7Ku8E/hqdefault.jpg)](https://www.youtube.com/watch?v=eejUgl7Ku8E "独播库下载器")


