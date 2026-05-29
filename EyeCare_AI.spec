# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Adhiraj Singh/miniconda3/envs/eyecare_env/lib/site-packages/mediapipe', 'mediapipe')],
    hiddenimports=['cv2', 'mediapipe', 'customtkinter', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'tensorflow', 'torch', 'sklearn', 'plotly', 'PyQt6', 'PyQt5', 'numpy'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EyeCare_AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=['vcruntime140.dll', 'msvcp140.dll'],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Produce a one-folder distribution (COLLECT) so numpy compiled extensions remain as files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='EyeCare_AI',
)
