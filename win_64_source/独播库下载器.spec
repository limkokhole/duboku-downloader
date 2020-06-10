# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['duboku_gui.py'],
             pathex=['C:\\Users\\Administrator\\Documents\\duboku'],
             binaries=[ ('duboku_lib\\ffmpeg_minimal_ts_2_mp4.exe', 'duboku_lib') ],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='独播库下载器',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='duboku_small.ico')
