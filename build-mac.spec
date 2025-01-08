# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/resources/styles', 'src/resources/styles'), ('src/resources/fonts', 'src/resources/fonts'), ('src/resources/images', 'src/resources/images'),('src/resources/html', 'src/resources/html')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UlogAnalyse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='1.0.0',
    icon=['images\\favicon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UlogAnalyse',
)

app = BUNDLE(
    coll,
    name='UlogAnalyse.app',
    icon='images/favicon.icns',
    bundle_identifier=None,
    version='1.0.0',
)