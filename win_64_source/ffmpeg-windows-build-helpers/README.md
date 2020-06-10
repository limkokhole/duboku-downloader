
#### Note to build windows ffmpeg_minimal_ts_2_mp4.exe:

[1] Try to familiar build ffmpeg for Linux first. .`/configure --<your-options1> --<your-options2>; make -j4;` This configure options will reflect on configure output section. E.g. parsers section means you can use `--disable-parsers` to disable all parsers while add `--enable-parser(without 's')=xxx,yyy` to enable only xxx and yyy for parsers. Careful `--disable-parsers` must on the left of `--enable-parser=xxx,yyy` . To learn basics of tiny/minimal build, read https://github.com/alberthdev/alberthdev-misc/wiki/Build-your-own-tiny-FFMPEG

[2] We need Linux to cross compile ffmpeg with the help of clean environment script. Full code please clone from https://github.com/rdp/ffmpeg-windows-build-helpers , OR my backup (not up to date) repo https://github.com/limkokhole/ffmpeg-windows-build-helpers  

[3] Modify cross_compile_ffmpeg.sh, run this script, select x64 only(build both x32/x64 would do double jobs and slow. ). Still, the first time to build can be few hours because it download/build dependency packages from scratch (And this is better than build from my system which packages version failed to match to cross compile ffmpeg successfully).  

[4] When I build this exe, I modify cross_compile_ffmpeg.sh, and the sample cross_compile_ffmpeg_latest.sh is latest git I copy at this time (without my modification). The latest script seems like already fixed fribidi undefined reference errors by specify commit id `fribidi_git 79581cc93b26c84edf74c9b51511126e0aacec9e`, while I simply fix it by disable fribidy and libass previously.  

You can diff this 2 files to know what I've modified, e.g. with this command:  

`dwdiff -C 0 -w "$(echo -e '\x1b[1;9m\x1b[1;91m')" -x "$(echo -e '\x1b[0m\x1b[K')" -y "$(tput bold; tput setaf 2)" -z "$(tput sgr0)" <(cat -v cross_compile_ffmpeg.sh) <(cat -v cross_compile_ffmpeg_latest.sh)`  

but this is the most important config options part to make ts to mp4 works with minimal size while slightly faster coversion speed:  

    ```
    #without enable-small (faster 1 second in average(2-3-4_seldom) vs --enable-small(3-4)):
    config_options="$init_options --disable-everything --disable-network --disable-autodetect --disable-doc --disable-ffprobe --disable-swscale --disable-avdevice --disable-swresample --disable-bzlib --disable-sndio --disable-sdl2 --disable-libxcb_xfixes --disable-libxcb --disable-libxcb_shape --disable-libxcb_shm --disable-lzma --disable-iconv --disable-xlib --disable-zlib --enable-bsf=extract_extradata,aac_adtstoasc --enable-muxer=mp4,mpegts --enable-demuxer=mpegts,aac,h264 --enable-decoder=aac,h264 --enable-parser=h264,aac --enable-protocol=file"
    ```

And I noticed --disable-everything only replaced this options ( p/s: Careful `--disable-demuxers` might not included default, show `--disable-demuxers` far more than what you can see if not put `--disable-demuxers`, can see by put `--disable-demuxers + enable_all` VS `no disable-demuxers + enable_all`, so be aware when narrow down):
    
    ```
    --disable-outdevs --disable-indevs --disable-protocols --disable-hwaccels --disable-parsers --disable-bsfs --disable-encoders --disable-decoders --disable-filters --disable-indev=v4l2 --disable-outdev=v4l2 --disable-v4l2-m2m --disable-muxers --disable-demuxers
    ```

`--enable-muxer=mpegts` require to allow remux the DTS/PTS of individual broken .ts chunk。


