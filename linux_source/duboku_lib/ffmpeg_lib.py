import os
import traceback
import subprocess as sp

ffmpeg_path = 'ffmpeg'

def reset_ts_start_time(ts_broken_path, ts_reset_path):

    print( '[...] 修复 .ts ({}) 去 .ts ({})'.format(ts_broken_path, ts_reset_path) )
    args = [ffmpeg_path, '-v', 'verbose', '-y', '-i', ts_broken_path, '-c', 'copy', ts_reset_path]
    try:
        proc = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
    except FileNotFoundError:
        print(traceback.format_exc())
        try:
            print('[😞] 转换失败, 文件不存在。')
        except UnicodeEncodeError:
            print('[!] 修复失败, 文件不存在。')
        return 127

    retval = proc.wait()
    if retval == 0:
        print('[+] 修复完成。 {}'.format(ts_reset_path) )
        try:
            os.remove(ts_broken_path)
        except OSError as e: 
            print("[!] 删除已损 .ts 文件失败: %s - %s。" % (e.filename, e.strerror))
        return ts_reset_path
    else: #1
        try:
            print('[😞] 修复失败。')
        except UnicodeEncodeError:
            print('[!] 修复失败。')
        return ts_broken_path

def remux_ts_to_mp4(ts_path, mp4_path):

    print( '[...] 转换 .ts ({}) 去 .mp4 ({})'.format(ts_path, mp4_path) )
    # -v verbose can see -bsf:a aac_adtstoasc already auto added
    # no nid -crf 0(loseless)-51(blur) if -c copy
    args = [ffmpeg_path, '-v', 'verbose', '-y', '-i', ts_path, '-c', 'copy', mp4_path]
    try:
        proc = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
        # OR [single_str] with shell=True:
        # args = [ffmpeg_path + " -v verbose -y -i " + ts_path + " -c copy " + mp4_path]
        # proc = sp.Popen(args, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, cwd=os.path.dirname(os.path.realpath(__file__)) )       
    except FileNotFoundError:
        print(traceback.format_exc())
        try:
            print('[😞] 转换失败, 文件不存在。')
        except UnicodeEncodeError:
            print('[!] 转换失败, 文件不存在。')
        return 127

    retval = proc.wait()
    if retval == 0:
        print('[+] 转换完成。您已可以观看该视频: {}'.format(mp4_path) )
    else: #1
        try:
            print('[😞] 转换失败。')
        except UnicodeEncodeError:
            print('[!] 转换失败。')
    try:
        os.remove(ts_path)
        #print('[-] 已删除 .ts 文件。{}'.format(ts_path) )
    except OSError as e: 
        print("[!] 删除 .ts 文件失败: %s - %s。" % (e.filename, e.strerror))

    return retval

if __name__ == "__main__":
    remux_ts_to_mp4('dftYY1Uh_246.ts', 'output.mp4')

'''
from ffmpeg_progress import start as ffmpeg_start

#def ffmpeg_callback(infile: str, outfile: str, vstats_path: str):
def ffmpeg_callback(infile, outfile, vstats_path):
return sp.Popen(['ffmpeg',
		'-nostats',
		'-loglevel', '0',
		'-y',
		'-vstats_file', vstats_path,
		'-i', infile,
		'c', 'copy',
		outfile]).pid
s
def on_message_handler(percent ,#: float,
		fr_cnt ,#: int,
		total_frames ,#: int,
		elapsed ): #: float):
print('percent: ' + repr(percent))
#sys.stdout.write('\r{:.2f}%'.format(percent))
#sys.stdout.flush()

def on_done():
print('hole OK')

ffmpeg_start(ts_path,
	mp4_path,
ffmpeg_callback,
on_message=on_message_handler,
on_done=on_done,
wait_time=1)  # seconds
'''

