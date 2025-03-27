# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tbox.py'],  # 替换为你的主程序文件名
    pathex=[],
    binaries=[],
    datas=[
        ('icons/*.png', 'icons'),    # 包含图标文件夹
        ('icon.png', '.')            # 包含主程序图标
    ],
    hiddenimports=[
        'win32com',                 # 包含必须的隐藏依赖
        'win32com.client',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tbox',             # 生成的exe名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # 关键：关闭控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',                # 使用ICO格式图标
)