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
__license__ = 'MIT'
__version__ = 1.0
__maintainer__ = 'Lim Kok Hole'
__email__ = 'limkokhole@gmail.com'
__status__ = 'Production'

import os, sys, traceback, time
import requests, re
import uuid
from urllib.parse import urljoin, urlparse
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

from .ffmpeg_lib import reset_ts_start_time 


def decrypt(data, key, iv, guest_padding_size):
    """Decrypt using AES CBC"""
    decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    # if ValueError AND has correct padding, https://github.com/Legrandin/pycryptodome/issues/10#issuecomment-354960150
    if guest_padding_size == 0: # can use as flag bcoz pad with 0 will throws modulo by zero err
        return decryptor.decrypt(data)
    else:
        return decryptor.decrypt(pad(data, guest_padding_size)) # You want pad to fill AND before decrypt, not unpad AND after decrypt. hexdump to view its last line not 16-bytes and need fill
    

def get_req(url, referer, proxies={}):
    """Get binary data from URL"""

    #data = ''
    #or chunk in requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, stream=True):
    #    data += chunk

    init_t = 0.3
    init_a = 0
    total_t = 0
    s = requests.Session()
    success_from_read = False
    while 1:
        try:
            if total_t >= 120:
                return None
            if ( (init_a % 6) == 0) and (init_t < 30):
                init_t+=0.3
            total_t+=init_t
            return s.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36', 'Referer': referer}, stream=True, timeout=init_t, proxies=proxies).content
            #success_from_read = False
        except requests.exceptions.ConnectTimeout:
            init_a+=1
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            success_from_read = True
            for t in (10, 20, 30, 60):
                try:
                    return s.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36', 'Referer': referer}, stream=True, timeout=t, proxies=proxies).content
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    pass
            return None

    #return requests.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36'}, stream=False, proxies=proxies).content #tested 1 proxy not able use stream=False
    #if r.status_code == 200:
    #    #r.raw.decode_content = True
    #    #return r.raw
    #    return r
    #return None


def parse_url(m3u8_host, m3u8_base, url):
    if '://' in url:
        return url
    else:
        if url.startswith('/'):
            return ''.join([ m3u8_host, url[1:] ])
        else:
            return ''.join([ m3u8_base, url ])


def main(m3u8_data, ts_path, ep_url, http_headers, arg_debug, debug_path, skip_ad=True, proxies={}):

    '''
    #testing:
    #m3u8_data = '#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1663000,RESOLUTION=1920x1080\n/ppvod/CLXhNcTU\n'
    m3u8_data = '#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,\
    BANDWIDTH=1663000,RESOLUTION=1920x1980\n/ppvod/CLXhNcTU\n'
    m3u8_data += '#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,\
    BANDWIDTH=1663000,RESOLUTION=360x1213\n/ppvod/ABChNcTU\n'
    m3u8_data += '#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,\
    BANDWIDTH=1663000,RESOLUTION=465x1080\n/ppvod/XYZhNcTU\n'
    '''
    m3u8_host = '{uri.scheme}://{uri.netloc}/'.format(uri= urlparse(ep_url) )
    m3u8_base = urljoin(ep_url, '.')

    # download and decrypt chunks
    #print((repr(m3u8_data)))
    '''
    #EXTM3U
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1663000,RESOLUTION=1920x1080
    /ppvod/RR9Qqr8K
    '''
    m3u8_resolution_d = {}
    m3u8_lines = m3u8_data.split('\n')
    m3u8_lines_last_line = len(m3u8_lines) - 1
    for i, line in enumerate(m3u8_lines):
        line = line.strip()
        ni = i + 1
        if line.startswith('#') and (',RESOLUTION=' in line) and (ni <= m3u8_lines_last_line) and not m3u8_lines[ni].strip().startswith('#'):
            line_r = line.split(',RESOLUTION=')
            if len(line_r) > 1:
                x_r = line_r[1].split('x')
                if len(x_r) > 1:
                    m3u8_resolution_d[x_r[1]] = m3u8_lines[ni].strip()

    #print('resolution_d: ' + repr(m3u8_resolution_d))

    if m3u8_resolution_d:
        real_m3u8_url = ''
        real_m3u8_data = ''
        for i in sorted(list(m3u8_resolution_d.keys()), reverse=True):
            try:
                real_m3u8_url = parse_url(m3u8_host, m3u8_base, m3u8_resolution_d[i])
                print(('real m3u8 url: ' + repr(real_m3u8_url)))

                m3u8_host = '{uri.scheme}://{uri.netloc}/'.format(uri= urlparse( real_m3u8_url ) )
                m3u8_base = urljoin( real_m3u8_url, '.')

                if arg_debug:
                    with open(debug_path, 'a') as f:
                        f.write('\n\nM3U8 URL: ' + real_m3u8_url + '\n\n')

                init_t = 1
                init_a = 0
                total_t = 0
                s = requests.Session()
                success_from_read = False
                while 1:
                    try:
                        if total_t >= 120:
                            return None
                        if ( (init_a % 6) == 0) and (init_t < 30):
                            init_t+=1
                        total_t+=init_t
                        real_m3u8_data = s.get(real_m3u8_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=proxies).text
                        #success_from_read = False
                        break
                    except requests.exceptions.ConnectTimeout:
                        init_a+=1
                    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                        success_from_read = True
                        break
                if success_from_read: # since we use Session(), so can reuse the "connected" session!
                    try:
                        real_m3u8_data = s.get(real_m3u8_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies).text
                    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                        print((traceback.format_exc()))

                if arg_debug:
                    with open(debug_path, 'a') as f:
                        f.write(real_m3u8_data)

            except Exception:
                print((traceback.format_exc()))
            else:
                break;
    else: # No resolution
        real_m3u8_data = m3u8_data

    sub_data = real_m3u8_data

    #for part_id, sub_data in enumerate(real_m3u8_data.split('#UPLYNK-SEGMENT:')):
    #for part_id, sub_data in enumerate(real_m3u8_data.split('\n')):

    # skip ad
    #if skip_ad:
    #    if re.findall('#UPLYNK-SEGMENT:.*,.*,ad', '#UPLYNK-SEGMENT:' + sub_data):
    #        continue

    #print(('sub_data: ' + repr(sub_data)))
    # get key, iv and data
    
    chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)\s.*\s(.*)', sub_data)

    print(('[1] chunks: ' + repr(chunks)))
    #print('[1.5] m3u8 host: ' + repr(m3u8_host))
    referer = m3u8_host + 'static/player/videojs.html'

    if not chunks:
        chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)"', sub_data)
        print(('[2] chunks: ' + repr(chunks)))
        if chunks:
            key_url = parse_url(m3u8_host, m3u8_base, chunks[0])
            key = get_req(key_url, referer, proxies=proxies)
            iv = key
        else:
            print('No need decrypt.')
            key_url = None
            key = None
            iv = None
        chunks = []
        #print(repr(sub_data.split('\n')))
        for d in sub_data.split('\n'):
            d = d.strip()
            if not d.startswith('#') and d.endswith('.ts'):
                #print(123)
                chunks.append(d)
        #chunks = re.findall(r'https?://.*ts', sub_data)
        #chunks = chunks[1:]
    else:
        chunks = chunks[0]
        key_url = parse_url(m3u8_host, m3u8_base, chunks[0])
        key = get_req(key_url, referer, proxies=proxies)
        iv = chunks[1][2:]
        #iv = iv.decode('hex')
        for d in sub_data.split('\n'):
            d = d.strip()
            if not d.startswith('#') and d.endswith('.ts'):
                 chunks.append(d)
        #chunks = re.findall(r'https?://.*ts', sub_data)
        #chunks = chunks[2:]

    print(('key_url: ' + repr(key_url)))
    print(('key: ' + repr(key)))
    #iv = "a7a15e3ee9dcaddd" #hole
    print(('iv: ' + repr(iv)))
    #print(('chunks: ' + repr(chunks)))

    total_chunks = len(chunks)
    for ts_i, ts_url in enumerate(chunks):

        ts_url = ts_url.strip()
        # Cmd need flush=True here:
        #ts_chunk_fname = os.path.basename(os.path.basename(ts_url).split('?')[0])
        if '://' not in ts_url:
            parsed = '+'
        else:
            parsed = ''
        ts_url = parse_url(m3u8_host, m3u8_base, ts_url)

        print('[{}/{}] 处理中{} {}'.format( (ts_i+1), total_chunks, parsed, ts_url ), flush=True)

        enc_ts = get_req(ts_url, referer, proxies=proxies)
        if enc_ts is None:
            print('[-] 网络问题，放弃此段。')
            continue

        #print(enc_ts)
        #print(dir(enc_ts))
    
        # concat decrypted ts to file
        #ts_path = os.path.join(output_folder, '%s' % 'love.mp4')
        #out_file = os.path.join(output_folder, '%s' % str(ts_i+1) + '_' + ts_chunk_fname)
        #ls -1 | sort -g | while IFS= read -r f; do cat "$f" >> ~/Downloads/duboku/vip4/chulian_from_205.ts; done
        
        if (ts_i == 0):
            #print('file mode is wb')
            file_mode = 'wb'
        else:
            #print('file mode is ab')
            file_mode = 'ab'
        try:
            with open(ts_path, file_mode) as f:
                #with open(ts_path, 'wb') as f:
                if (key is None) and (iv is None):
                    f.write(enc_ts)
                else:
                    try:
                        dec_ts = decrypt(enc_ts, key, iv, 0)
                        f.write(dec_ts)
                        #raise ValueError # TESTING PURPOSE
                    except ValueError:
                        # BLOCK_SIZE 16 also related to crypto_py_aes.py
                        print('[i] 此段不满足 16 倍数解密。') # hang and 声音位移
                        success_pad = False
                        ts_chunk_fname = str(uuid.uuid4()) + '.ts'
                        ts_chunk_fname_tmp = os.path.basename( '_'.join([ ts_chunk_fname, str(time.time()) + '.temp' ]) )
                        for i in range(1, 18):
                            try:
                                dec_ts = decrypt(enc_ts, key, iv, i)
                                with open(ts_chunk_fname_tmp, 'wb') as ts_cf:
                                    ts_cf.write(dec_ts)
                                    print('[+] 填充 ' + str(i) +  ' 字节成功。')
                                ts_chunk_reseted_fname, success = reset_ts_start_time(ts_chunk_fname_tmp, ts_chunk_fname)
                                with open(ts_chunk_reseted_fname, 'rb') as ts_crf:
                                    f.write(ts_crf.read())
                                if arg_debug and (not success):
                                    raise Exception
                                try:
                                    os.remove(ts_chunk_reseted_fname)
                                except OSError:
                                    print('[+] 删除临时文件失败: ' + repr(ts_chunk_reseted_fname) )
                                success_pad = True
                                break
                            except ValueError:
                                pass
                        if not success_pad:
                            print('[-] 放弃此段。')
        except PermissionError:
            print((traceback.format_exc()))
            print('[!] 请不要一边下载加密的 .ts 视频，一边观看该视频。 请重新下载该集。')

        ''' [onhold:0] How to know ts file size without download ???
        #with open(ts_path + str(ts_i+1), 'ab') as f:
        with open(ts_path + str(ts_i+1) + '.tmp', 'wb') as f:
            #with open(ts_path, 'wb') as f:
            dec_ts = decrypt(enc_ts, key, iv)
            f.write(dec_ts)

        overwrite = True

        ts_path_tmp = ts_path + str(ts_i+1) + '.tmp'
        if part_id == 0:
            if os.path.isfile(ts_path):

                os.path.getsize(ts_path_tmp) < os.path.getsize(ts_path)

                with open(ts_path_tmp, 'rb') as ts_f_part, open(ts_path, 'rb') as ts_f:
                    ts_f_part_512 = ts_f_part.read(512)
                    ts_f_512 = ts_f.read(512)
                    if ts_f_part_512 == ts_f_512:
                        print('file IS match, should find out resume point')
                        overwrite = False
                    else:
                        print('file NOT match')
        
        if overwrite:
            with open(ts_path_tmp, 'rb') as ts_f_part, open(ts_path, 'rb') as ts_f:
                ts_f.write(ts_f_part.read())
        '''
        

    return True

#if __name__ == '__main__':
#    if len(sys.argv) < 3:
#        sys.exit('Usage: %s <m3u8_file> <ts_path>' % os.path.basename(sys.argv[0]))
#    with open(sys.argv[1], 'r') as f:
#        m3u8_data = f.read()
#    # make output folder
#    #if not os.path.exists(output_folder):
#    #    os.makedirs(output_folder)
#    main(m3u8_data, sys.argv[2], skip_ad=True)
