# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2019 limkokhole@gmail.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Lim Kok Hole'
__copyright__ = 'Copyright 2020'
__credits__ = ['Stack Overflow Links']
__license__ = 'MIT'
__version__ = 1.0
__maintainer__ = 'Lim Kok Hole'
__email__ = 'limkokhole@gmail.com'
__status__ = 'Production'

'''
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
'''

import sys, os, traceback
import requests

PY3 = sys.version_info[0] >= 3
if not PY3:
    print('\n[!] python 2 已在 2020 年退休。请使用 python 3。中止。')
    sys.exit(1)

from bs4 import BeautifulSoup

#try: from urllib.request import urlopen #python3
#except ImportError: from urllib2 import urlopen #python2

# RIP UA, https://groups.google.com/a/chromium.org/forum/m/#!msg/blink-dev/-2JIRNMWJ7s/yHe4tQNLCgAJ
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36'
#from termcolor import cprint
#import colorama
#from colorama import Style, Fore, Back
#colorama.init() # Windows need this
#BOLD_ONLY = ['bold']

# https://github.com/limkokhole/calmjs.parse
import calmjs # Used in `except calmjs...:`
from calmjs.parse import es5
# ~/.local/lib/python3.6/site-packages/calmjs/parse/walkers.py
from calmjs.parse.asttypes import Assign as CalmAssign
from calmjs.parse.asttypes import Identifier as CalmIdentifier
from calmjs.parse.asttypes import String as CalmString
from calmjs.parse.asttypes import VarDecl as CalmVar
from calmjs.parse.walkers import Walker as CalmWalker
from calmjs.parse.parsers.es5 import Parser as CalmParser

from duboku_lib.m3u8_decryptor import main as m3u8_decryptopr_main
from duboku_lib.ffmpeg_lib import remux_ts_to_mp4 
from duboku_lib.crypto_py_aes import main as crypto_py_aes_main

import argparse
from argparse import RawTextHelpFormatter
arg_parser = argparse.ArgumentParser(
    description='独播库下载器', formatter_class=RawTextHelpFormatter)

def quit(msgs, exit=True):
    if not isinstance(msgs, list):
        msgs = [msgs]
    # 搞笑 bug: 之前无意中移除 exit=True，导致我系统有默认 exit 没问题，别人却有问题。
    if exit: #避免只看见最后一行“中止。”而不懂必须滚上查看真正错误原因。
        msgs[-1]+= '中止。'
    for msg in msgs:
        if msg == '\n': # Empty line without bg color
            print('\n')
        else:
            #cprint(msg, 'white', 'on_red', attrs=BOLD_ONLY)
            print(msg)
    # Should not do this way, use return instead to support gui callback
    #if exit:
    #    #cprint('Abort.', 'white', 'on_red', attrs=BOLD_ONLY)
    #    sys.exit()

#arg_parser.add_argument('-t', '--video-type', dest='video_type', action='store_true', help='Specify movie instead of cinemae')
arg_parser.add_argument('-d', '--dir', help='用来储存连续剧/综艺的目录名 (非路径)。')
arg_parser.add_argument('-f', '--file', help='用来储存电影的文件名。请别加后缀 .mp4。')
#from/to options should grey out if -f selected:
arg_parser.add_argument('-from-ep', '--from-ep', dest='from_ep', default=1, type=int, help='从第几集开始下载。')
arg_parser.add_argument('-to-ep', '--to-ep', dest='to_ep',
                        type=int, help='到第几集停止下载。')
arg_parser.add_argument('-p', '--proxy', help='https 代理(如有)')
arg_parser.add_argument('-g', '--debug', action='store_true', help='储存 duboku_epN.log 日志附件， 然后你可以在 https://github.com/limkokhole/duboku-downloader/issues 报告无法下载的问题。')
arg_parser.add_argument('url', nargs='?', help='下载链接。')
args, remaining = arg_parser.parse_known_args()

def main(arg_dir, arg_file, arg_from_ep, arg_to_ep, arg_url, custom_stdout, arg_debug, arg_proxy=None):

    try:
        sys.stdout = custom_stdout
        # stderr can test with calmjs error:
        # Don't be confuse, outer es5 use internal es5, both files named es5.py:
        # this file -> CalmParser() -> calmjs.parse.parsers.es5 -> [calmjs\parse\parsers\es5.py] 
        # -> self.lexer.build(optimize=lex_optimize, lextab=lextab) -> from calmjs.parse.lexers.es5 import Lexer 
        # -> [calmjs\parse\lexers\es5.py] -> class Lexer(object): -> def build(self, **kwargs):  -> ply.lex.lex(object=self, **kwargs) 
        # -> [lex.py] -> def lex -> errorlog = PlyLogger(sys.stderr) -> class PlyLogger(object): -> def error(self, msg, *args, **kwargs): 
        # -> self.f.write('ERROR: ' + (msg % args) + '\n') # f should means stderr here
        # [UPDATE] disable since useless now (other place change stderr is calmjs CP.parse(script.text) below)
        # Without stderr still able to shows ffmpeg not found traceback on gui log
        # sys.stderr = custom_stdout 

        if not arg_url:
            print('main arg_url: ' + repr(arg_url))
            #quit('[!] [e1] Please specify cinema url in https://www.fanstui.com/voddetail-300.html. Abort.')
            return quit('[!] [e1] 请用该格式  https://www.duboku.co/voddetail/300.html 的链接。')

        # Should accept these formats:
        # https://www.duboku.net/voddetail/300.html 
        # https://www.fanstui.com/voddetail-300.html # Deprecated
        # https://www.fanstui.com/vodplay/300-1-1.html # Deprecated
        # https://www.fanstui.com/vp/529-1-1.html # Deprecated
        # https://tv.newsinportal.com/vodplay/1382-1-3.html
        #VODPLAY_PREFIX = 'https://www.fanstui.com/vodplay/'
        NEWS_VODPLAY_PREFIX = 'vodplay/'
        VODPLAY_PREFIX = 'vodplay/'
        VODDETAIL_PREFIX = 'voddetail/'
        #VP_PREFIX = 'https://www.fanstui.com/vp/'
        VP_PREFIX = 'vp/'
        ORIG_PREFIX='voddetail-'

        cinema_url_post = '.html'
        #cinema_url_pre = 'https://www.duboku.net/vodplay/'

        if '://' not in arg_url:
            arg_url = 'https://' + arg_url
        arg_path = '/'.join( arg_url.split('/')[-2:] )
        cinema_url_pre = '/'.join( arg_url.split('/')[:-2]) + '/' + VODPLAY_PREFIX

        arg_url_m = arg_path.strip() #.replace('https://www.duboku.net/', 'https://www.fanstui.com/')
        try:
            #if arg_url_m.startswith('https://www.fanstui.com/voddetail-'):
            if arg_url_m.startswith(ORIG_PREFIX):
                #cinema_id = int(arg_url_m.split('https://www.fanstui.com/voddetail-')[1].split('.html')[0])
                cinema_id = int(arg_url_m.split(ORIG_PREFIX)[1].split('.html')[0])
                cinema_id = str(cinema_id) #set back str after test int() ValueError
                cinema_url_middle = '-1-'
            elif arg_url_m.startswith(NEWS_VODPLAY_PREFIX):
                cinema_id = int(arg_url_m.split(NEWS_VODPLAY_PREFIX)[1].split('-')[0])
                cinema_id = str(cinema_id)
                cinema_url_middle = '-' + arg_url_m.split(NEWS_VODPLAY_PREFIX)[1].split('-')[1] + '-'
            elif arg_url_m.startswith(VODPLAY_PREFIX):
                cinema_id = int(arg_url_m.split(VODPLAY_PREFIX)[1].split('-')[0])
                cinema_id = str(cinema_id)
                cinema_url_middle = '-' + arg_url_m.split(VODPLAY_PREFIX)[1].split('-')[1] + '-'
            elif arg_url_m.startswith(VODDETAIL_PREFIX):
                cinema_id = int(arg_url_m.split(VODDETAIL_PREFIX)[1].split('.')[0])
                cinema_id = str(cinema_id)
                cinema_url_middle = '-1-'
            elif arg_url_m.startswith(VP_PREFIX):
                cinema_id = int(arg_url_m.split(VP_PREFIX)[1].split('-')[0])
                cinema_id = str(cinema_id)
                cinema_url_middle = '-' + arg_url_m.split(VP_PREFIX)[1].split('-')[1] + '-'
            else:
                #return quit('[!] [e2] Please specify cinema url in https://www.fanstui.com/voddetail-300.html. Abort.')
                return quit('[!] [e2] 请用该格式 https://www.duboku.co/voddetail/300.html 的链接。')
        except ValueError as ve:
            print(ve)
            #return quit('[!] [e3] Please specify cinema url in https://www.fanstui.com/voddetail-300.html. Abort.')
            return quit('[!] [e3] 请用该格式  https://www.duboku.co/voddetail/300.html 的链接。')


        if arg_file:
            if arg_dir:
                return quit('[!] 不能同时使用 -d 和 -f 选项。')
                
            ep_ts_path = os.path.abspath(arg_file + '.ts')
            ep_mp4_path = os.path.abspath(arg_file + '.mp4')
            arg_to_ep = 2
        else:
            if not arg_to_ep:
                return quit('[!] 请用 `--to-ep N` 选项决定从第 N 集停止下集。')
            if arg_from_ep > arg_to_ep:
                return quit('[!] 从第几集必须小于或等于到第几集。')
            arg_to_ep+=1

            if not arg_dir:
                return quit('[!] 请用 `-d 目录名` 选项。')

            dir_path_m = os.path.abspath(arg_dir)
            if not os.path.isdir(dir_path_m):
                try:
                    os.makedirs(dir_path_m)
                except OSError:
                    return quit('[i] 无法创建目录。或许已有同名文件？ ')

        # https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python
        http_headers = {
            'User-Agent': UA
            #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
            #, 'From': 'youremail@domain.com'  # This is another valid field
        }

        def calm_assign(node):
            #print('$$$$$$$$$$$$$$$$ START')
            #print(type(node)) #can see class xxx(e.g. BinOp) at calmjs/parse/asttypes.py
            #print(node)
            #print('$$$$$$$$$$$$$$$$ M')
            #print(dir(node))
            #print('$$$$$$$$$$$$$$$$ END')
            return isinstance(node, CalmAssign)

        def calm_id(node):
            #print(node)
            #print(type(node))
            #print(isinstance(node, Identifier))
            return isinstance(node, CalmIdentifier)

        def calm_str(node):
            return isinstance(node, CalmString)

        def calm_var(node):
            return isinstance(node, CalmVar)

        '''
        //https://github.com/brix/crypto-js
        //import js in console:
        var imported = document.createElement('script');
        //https://cdnjs.com/libraries/crypto-js
        imported.src = 'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/crypto-js.js';
        document.head.appendChild(imported);

        //rerun the code from webpage:
        var content = "U2FsdGVkX18/ZQ8zQuYIsjIgZkCTVTWoklPND/Bx5tdp3vphNNtxnlzBPeCW2h3OiGbgI17pH/14qF2e8ZsWLpcNeGegDzRonl8dnDwnZKYSOgkPXmSwxArjg1lBPufaSJs8IyTcATJINMrWme/TqSPxxe7CdezlsA35neSw+OjEzx5yUH3mhZY2Jnah+ko2wmIBucCkRUdGbwU8ufsmX4FL+fkKDAIPi+AVmITbzcquMnGHnk/CmibPG9CNOr5joKrdJ1GT2bodPn9vnruvY+j3tNC6D4sdRtLnHAlEUnxlLu0Sr6NczJsgVlrKhsn06ML2Jkcc+ZQ4+fuFeXhEl6isEGjlCAdnrlbSl6SvSxqyjnA2JwBGjUWGs3kIBnaNc+TCNi5Vmxiv3OsSgbQM4NX6SqD66+cqBlM6gqeUjOXDa+7O39GcIsKNo/95hbfTBruDZIIQM1UKVoA7ZfuFN+L9AmuoirrMb24AWxTiHQPGdCxWLzncwdn9Ri7GouiUVGDBuDaiRBKJvR1MgVIBUQ8n/D1HZUsFQJLpA4x2+49ZQ2loovIYU5gkoPZSPGnYHK1iZmMPYLFFxPyHob5QBu1w5wgo5ZtSYS14B3PnT6DY0NLHm5etSgeOM2dvkOY+i/U9q98XLYMd1GAORWt6AdpMFZm+1BVwIxF1JyodpLg57z9eTZSv/I0+FlGsQRGArXga5Xoq6Sj22l1tiGgt5ZDtHFaQeLBMhKWqIdVDyxhsqhtRpxx//EA9b9ZALquYo+6XeEm61RLbyoUqPnYE0ygi1W3Br6EpnimKAxYAoYqv7vIedF2WLOJ9t/mPB594EPkV8PGgha6IOyqLgn8QPqS+pFsuJeRAD9xUCAL9905v9igSC73Q22gXxcTb9m2CEqHDYWrVD528rr7uY/c8PypvvWX35dxNdNiJ3n4Kc6SuL27ncmPyHIyTXrNwdPyvvexIrzD7uJIUFirqoR1JCGGyjks5RLcw/iTTXurV2M9y3mGr3pBAM66bxlglfNugp/Pwg05gr8ik31mqvvxyWw==";
        var bytes =  CryptoJS.AES.decrypt(content, 'ppvod');
        var originalText = bytes.toString(CryptoJS.enc.Utf8);

        //get:
        "var hosts = 'www.duboku.net|tv.zdubo.com|v.zdubo.com|v.wedubo.com|v.duboku.net|www.fanstui.com|www.duboku.tv|localhost';
        var playlist = '[{\"url\":\"/20190923/EEGkg4vm/hls/index.m3u8\"}]';
        playlist = JSON.parse(playlist);
            var danmuenable = 0;
            var magnet = \"\"
            var redirecturl = \"https://v.zdubo.com\";
            var videoid = \"1Rhgp5nzyWuK3P6k\";
            var id = '1Rhgp5nzyWuK3P6k'
            var l = ''
            var r = ''
            var t = '15'
            var d = ''
            var u = ''
            var main = \"/ppvod/H2GPhFCJ\";
            var playertype = 'dplayer'; // dplayer || ckplayer
            
            var mp4 = \"/20190923/EEGkg4vm/mp4/EEGkg4vm.mp4\";
            
            var xml = \"\";		
            
            var pic = \"/20190923/EEGkg4vm/1.jpg\";
                

        $(function () {
            var t = BrowserType();		
            if (t && t.indexOf(\"IE\") >= 0  )
                playertype = \"ckplayer\"
            var order = 0;
                
            init(order);
        })
        '''

        CP = CalmParser()
        walker = CalmWalker()
        if arg_proxy:
            arg_proxy = arg_proxy.strip()
        if arg_proxy:
            if not arg_proxy.startswith('http://') and not arg_proxy.startswith('https://') and not arg_proxy.startswith('socks5://'):
                arg_proxy = 'http://' + arg_proxy
            proxies = { 'https': arg_proxy, }
            print('[...] 尝试代理: ' + proxies['https'])
        else:
            proxies = {}
            print('[...] 无代理。')
            
        for ep in range(arg_from_ep, arg_to_ep):
            url = ''.join([cinema_url_pre, cinema_id, cinema_url_middle, str(ep), cinema_url_post]) #don't override template cinema_url
            if arg_file:
                print('[...] 尝试 URL: ' + url)
            else:
                print('[当前第{}集] 尝试 URL: {}'.format(ep, url) )
            try:

                if arg_debug:
                    with open('duboku_ep' + str(ep) + '.log', 'w') as f:
                        f.write('URL: ' + url + '\n\n')

                try:
                    try:
                        http_headers.pop('referer')
                    except KeyError:
                        pass
                    r = requests.get(url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies)
                except requests.exceptions.ConnectionError:
                    print('\n[!] 你的网络出现问题，也可能是网站的服务器问题。\n', flush=True)
                    continue

                if arg_debug:
                    with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                        f.write(r.text)

            except requests.exceptions.ProxyError as pe:
                print('[😞] 代理错误。请检查您的代理。确保有端口号(port number)， 例如端口1234: http://127.0.0.1:1234\n')
                print(traceback.format_exc())
                break
            soup = BeautifulSoup(r.text, 'html.parser')

            ct_b64 = '' #reset
            passwd = '' #reset
            http_headers.update({'referer': url})

            printed_err = False
            got_ep_url = False
            for script in soup.find_all('script'):
                #print(script)
                try:
                    #program = es5(script.text)

                    #PyInstaller has issue to make `ply_dist = working_set.find(Requirement.parse('ply'))` in calmjs\parse\utils.py return non-None
                    #... And causes self.parser.parse in \calmjs\parse\parsers\es5.py no parse method 
                    #... bcoz set with unknown pkg name by Parser() constructor/init 's tabmodule=yacctab arg
                    #, so re-assign stderr here to ignore this common warning msg to send to gui log
                    # [UPDATE] disable since useless now.
                    #sys.stderr = sys.__stderr__
                    tree = CP.parse(script.text)
                    #sys.stderr = custom_stdout 

                    #print(type(tree)) #<class 'calmjs.parse.factory.ES5Program'>
                    #print(tree)

                    #print('######## START')
                    #print(tree) #text #type is <class 'calmjs.parse.factory.ES5Program'
                    #print(walker.filter(tree, assignment)) #<generator object Walker.filter at 0x7f0b75664360>
                    #print(walker.filter(tree, assignment)) 

                    #for w in walker.filter(tree, assignment):
                    #    print(w)
                    ep_url = '' #reset
                    is_vimeo = False
                    vimeo_qd = {}
                    ep_mp4_path = None
                    for w in walker.filter(tree, calm_id):
                        if w.value == 'player_data':
                            for wa in walker.filter(tree, calm_assign):
                                if wa.left.value == '"url"': #'' included ""
                                    rv = wa.right.value
                                    ep_url = rv.replace('\/', '/').strip('\"').strip('\'')

                                    #episode not exists
                                    if not ep_url.strip():

                                        if not printed_err:
                                            print('[!] 不存在第{}集。'.format(ep))
                                        printed_err = True

                                        continue

                                    try:
                                        if ep_url.split('/')[2].split('.')[1].lower() == 'vimeo':
                                            # e.g. https://www.duboku.co/vodplay/1584-1-1.html 
                                            # -> https://player.vimeo.com/video/452182074
                                            is_vimeo = True

                                            if arg_debug:
                                                with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                                    f.write('\n\nEP URL of VIMEO: ' + ep_url + '\n\n')
                                            #print('呼叫 vimeo... ' + repr(ep_url))
                                            r_iframe = requests.get(ep_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies)

                                            if arg_debug:
                                                with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                                    f.write(r_iframe.text)
                                            soup_iframe = BeautifulSoup(r_iframe.text, 'html.parser')
                                            for vimeo_script in soup_iframe.find_all('script'):
                                                tree = es5( vimeo_script.text )
                                                for w in walker.filter(tree, calm_var):
                                                    if w.identifier.value == 'config':
                                                        for config_wp in w.initializer.properties:
                                                            try:
                                                                for config_wp2 in config_wp.right.properties:
                                                                    for config_wp3 in config_wp2.right.properties:
                                                                        if 'progressive' != config_wp3.left.value.strip('"').lower():
                                                                                continue
                                                                        try:
                                                                            for config_wp4 in config_wp3.right.children():
                                                                                next_width_k = '' 
                                                                                next_url_v = ''
                                                                                for config_wp5 in config_wp4.properties:
                                                                                    if config_wp5.left.value.strip('"').lower() == 'width':
                                                                                        next_width_k = config_wp5.right.value
                                                                                        if next_url_v:
                                                                                            vimeo_qd[int(next_width_k)] = next_url_v
                                                                                    elif config_wp5.left.value.strip('"').lower() == 'url':
                                                                                        next_url_v = config_wp5.right.value.strip('"')
                                                                                        if next_width_k:
                                                                                            vimeo_qd[int(next_width_k)] = next_url_v
                                                                        except (TypeError, AttributeError):
                                                                            pass #print(traceback.format_exc())
                                                            except (TypeError, AttributeError):
                                                                pass
                                    except IndexError:
                                        print('Split ep url failed: ' + repr(ep_url))

                                    if is_vimeo:
                                        #print('vimeo 视频质量: ' + repr(vimeo_qd))
                                        if not vimeo_qd:
                                            continue
                                        vimeo_qdk = list(vimeo_qd.keys())
                                        vimeo_qdk.sort(key=int)
                                        ep_url = vimeo_qd[int(vimeo_qdk[-1])]

                                    elif rv.endswith('.m3u8"') or rv.endswith(".m3u8'"): #[todo:0] need check ' also ?
                                        pass
                                            
                                    else: #single video normally came here
                                        #print('NEW url type? ' + repr(ep_url))

                                        if arg_debug:
                                            with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                                f.write('\n\nEP URL: ' + ep_url + '\n\n')

                                        r_iframe = requests.get(ep_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies)

                                        if arg_debug:
                                            with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                                f.write(r_iframe.text)

                                        soup_iframe = BeautifulSoup(r_iframe.text, 'html.parser')
                                        decrypted_final_js = None
                                        for script_iframe in soup_iframe.find_all('script'):
                                            tree_iframe = CalmParser().parse(script_iframe.text.strip())
                                            for decrypt_js in walker.filter(tree_iframe, calm_var):
                                                if decrypt_js.identifier.value == 'content':
                                                    ct_b64 = decrypt_js.initializer.value
                                                elif decrypt_js.identifier.value == 'bytes':
                                                    get_passwd = False
                                                    for decrypt_i, decrypt_js_c in enumerate(decrypt_js.initializer.children()):
                                                        if get_passwd:
                                                            #(content, 'ppvod')
                                                            for dci, dc in enumerate(decrypt_js_c.children()):
                                                                if dci == 1 and isinstance(dc.value, str):
                                                                    passwd = dc.value[1:-1] #exclude ''
                                                        if decrypt_js_c.__str__() == 'CryptoJS.AES.decrypt':
                                                            #CryptoJS.AES.decrypt
                                                            get_passwd = True
                                                elif decrypt_js.identifier.value == 'playlist':
                                                    decrypted_final_js = tree_iframe
                                                   
                                        if ct_b64: 
                                            print('ct b64 data: ' + repr(ct_b64))
                                            print('passwd: ' + repr(passwd))
                                            decrypted_final_content = crypto_py_aes_main(ct_b64, passwd)
                                            decrypted_final_js = CalmParser().parse(decrypted_final_content.decode())
                                        #else: # No nid decrypt, direct use plain `decrypted_final_js = tree_iframe` above
                                        m3u8_path_incomplete = '' #reset
                                        m3u8_host_incomplete = ''

                                        for decrypted_final_var in walker.filter(decrypted_final_js, calm_var):
                                            if decrypted_final_var.identifier.value == 'playlist':
                                                decrypted_m3u8_path = decrypted_final_var.initializer.value[1:-1]  # exclude ''
                                                if "'" in decrypted_m3u8_path:
                                                    dot_type = "'"
                                                elif '"' in decrypted_m3u8_path:
                                                    dot_type = '"'
                                                else:
                                                    continue
                                                for path_part in decrypted_m3u8_path.split(dot_type):
                                                    if path_part.endswith('.m3u8'):
                                                        m3u8_path_incomplete = path_part

                                            elif decrypted_final_var.identifier.value == 'redirecturl':
                                                m3u8_host_incomplete = decrypted_final_var.initializer.value[1:-1] #exclude ""
                                            
                                        if not m3u8_host_incomplete.endswith('/') and not m3u8_path_incomplete.startswith('/'):
                                            ep_url = m3u8_host_incomplete + '/' + m3u8_path_incomplete 
                                        else:
                                            ep_url = m3u8_host_incomplete + m3u8_path_incomplete

                                    if arg_dir:
                                        ep_filename = os.path.basename( ''.join([ '第', str(ep), '集' ]) )
                                        ep_ts_path = os.path.join(dir_path_m, ''.join([os.path.basename(ep_filename) + '.ts']) )
                                        ep_mp4_path = os.path.join(dir_path_m, ''.join([os.path.basename(ep_filename), '.mp4']) )
                                        
                                if ep_url:
                                    break
                        if ep_url:
                            break

                    if ep_url and ep_mp4_path:
                        got_ep_url = True
                        print('下载的 url: ' + ep_url)
                        if not is_vimeo:
                            print('下载的 ts 路径: ' + ep_ts_path)
                        print('下载的 mp4 路径: ' + ep_mp4_path)

                        if arg_debug:
                            with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                f.write('\n\n下载的 url: ' + ep_url)
                                if not is_vimeo:
                                    f.write('\n下载的 ts 路径: ' + ep_ts_path)
                                f.write('\n下载的 mp4 路径: ' + ep_mp4_path + '\n\n')

                        if is_vimeo:
                            import tqdm
                            r = requests.get(ep_url, allow_redirects=True, headers=http_headers, timeout=30
                                , proxies=proxies, stream=True)
                            chunk_size = 1024  # 1 MB
                            file_size = int(r.headers['Content-Length'])
                            num_bars = 0 #int(file_size / chunk_size)
                            with open(ep_mp4_path, 'wb') as fp:
                                for chunk in tqdm.tqdm(r.iter_content(chunk_size=chunk_size), total=num_bars
                                        , position=0, mininterval=5
                                        , unit='KB', desc=ep_mp4_path, leave=True, file=sys.stdout):
                                    fp.write(chunk)
                        else:

                            r = requests.get(ep_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies)

                            if arg_debug:
                                with open('duboku_ep' + str(ep) + '.log', 'a') as f:
                                    f.write('r: ' + r.text)

                            # Disable `if` condition line below, if want to test convert .ts without re-download
                            if m3u8_decryptopr_main(r.text, ep_ts_path, ep_url, http_headers, arg_debug, 'duboku_ep' + str(ep) + '.log', proxies=proxies):
                                remux_ts_to_mp4(ep_ts_path, ep_mp4_path)

                        #source_url = "https://tv2.xboku.com/20191126/wNiFeUIj/index.m3u8"
                        #https://stackoverflow.com/questions/52736897/custom-user-agent-in-youtube-dl-python-script
                        #youtube_dl.utils.std_headers['User-Agent'] = UA
                        #try: # This one shouldn't pass .mp4 ep_path
                        #    youtube_dl.YoutubeDL(params={'-c': '', '-q': '', '--no-mtime': '',
                        #                                 'outtmpl': ep_path + '.%(ext)s'}).download([ep_url])
                        #except youtube_dl.utils.DownloadError:
                        #    print(traceback.format_exc())
                        #    print(
                        #        'Possible reason is filename too long. Please retry with -s <maximum filename size>.')
                        #    sys.exit()

                        break
                    #print(walker.extract(tree, assignment))

                    #print('######## END')
                except calmjs.parse.exceptions.ECMASyntaxError as ee:
                    pass #here is normal
                    #print('ex') 
                    #print(traceback.format_exc())
                except Exception:
                    #Need to catch & print exception explicitly to pass to duboku_gui to show err log
                    print(traceback.format_exc())
                    try:
                        print('[😞]')
                    except UnicodeEncodeError:
                        print('[!] 失败。')

            if not got_ep_url:
                if not printed_err:
                    if arg_file:
                        print('[!] 不存在该部影片。')
                    else:
                        print('[!] 不存在第{}集。'.format(ep))

    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')

    try:
        print('[😄] 全部下载工作完毕。您已可以关闭窗口, 或下载别的视频。')
    except UnicodeEncodeError:
        print('[*] 全部下载工作完毕。您已可以关闭窗口, 或下载别的视频。')

    '''
    #slimit, https://stackoverflow.com/questions/44503833/python-slimit-minimizer-unwanted-warning-output
    parser = Parser()
    tree = parser.parse(script.text)
    for node in nodevisitor.visit(tree):
        if isinstance(node, ast.Assign):
            print(666)
    '''

    #soup.find_all(id='')
    #print(soup)

if __name__ == "__main__":
    main(args.dir, args.file, args.from_ep, args.to_ep, args.url, sys.stdout, args.debug, args.proxy)
