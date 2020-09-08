import os, sys
import traceback
import subprocess as sp
ffmpeg_path = 'ffmpeg_minimal_ts_2_mp4'

# SO/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
#if getattr(sys, 'frozen', False):
#    #print('sys exe: ' + repr(sys.executable))
#    application_path = os.path.dirname(os.path.realpath(sys.executable))
#elif __file__:
#    application_path = os.path.dirname(os.path.realpath(__file__))
#ffmpeg_full_path = ffmpeg_path #os.path.join(application_path, ffmpeg_path)

# SO/questions/7674790/bundling-data-files-with-pyinstaller-onefile
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    #print('done base_path: ' + repr(base_path))
except Exception:
    #print('use abs path')
    base_path = os.path.abspath(".")

# The reason why cann't do '.' in .spec and single os.path.join() below is bcoz:
# Since I want to put ffmpeg exe inside github's duboku_lib which is the hierachy nicer than put same path as duboku_gui.py
# then .spec runtime directory need same('.\\duboku_lib\\') as duboku_lib directory name AS run from command `python3 duboku_gui.py` bcoz they need refer same file(you don't want put duplicated ffmpeg exe in 2 places) which sahre the same code "duboku_lib" here.
ffmpeg_full_path = os.path.join(base_path, os.path.join('duboku_lib', ffmpeg_path) )

#print( 'app path: ' + repr(application_path) )
# [Use this for debug]
#print( 'ffmpeg full path: ' + repr(ffmpeg_full_path) , flush=True)
#print( os.path.dirname(os.path.realpath(__file__)) , flush=True)

def reset_ts_start_time(ts_broken_path, ts_reset_path):

    print( '[...] 修复 .ts ({}) 去 .ts ({})'.format(ts_broken_path, ts_reset_path) )
    args = [ffmpeg_full_path, '-v', 'verbose', '-y', '-i', ts_broken_path, '-c', 'copy', ts_reset_path]
    try:
        proc = sp.Popen(args, shell=True, stdin=sp.PIPE, stdout=sp.PIPE)
    except FileNotFoundError:
        print(traceback.format_exc())
        try:
            print('[😞] 转换失败, 文件不存在。')
        except UnicodeEncodeError:
            print('[!] 转换失败, 文件不存在。')
        return ts_broken_path, False

    retval = proc.wait()
    #retval = 1 # TESTING PURPOSE
    if retval == 0:
        print('[+] 修复完成。 {}'.format(ts_reset_path) )
        try:
            os.remove(ts_broken_path)
        except OSError as e: 
            print("[!] 删除已损 .ts 文件失败: %s - %s。" % (e.filename, e.strerror))
        return ts_reset_path, True
    else: #1
        try:
            print('[😞] 修复失败。')
        except UnicodeEncodeError:
            print('[!] 修复失败。')
        return ts_broken_path, False

def remux_ts_to_mp4(ts_path, mp4_path):

    print( '[...] 转换 .ts ({}) 去 .mp4 ({})'.format(ts_path, mp4_path) )
    # -v verbose can see -bsf:a aac_adtstoasc already auto added
    # no nid -crf 0(loseless)-51(blur) if -c copy
    args = [ffmpeg_full_path, '-v', 'verbose', '-y', '-i', ts_path, '-c', 'copy', mp4_path]
    try:
        proc = sp.Popen(args, shell=True, stdin=sp.PIPE, stdout=sp.PIPE)
        # OR [single_str] with shell=True (without shell=True will popup black cmd window which is annoying if you doing other task):
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

