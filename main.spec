# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\eye_care_project\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Adhiraj Singh/miniconda3/envs/eyecare_env/lib/site-packages/mediapipe', 'mediapipe')],
    hiddenimports=['cv2', 'mediapipe', 'customtkinter', 'PIL', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
