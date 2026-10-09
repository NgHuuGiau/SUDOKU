# PyInstaller build configuration for Sudoku
# Usage: python -m PyInstaller build.spec
# Cross-platform: Windows (exe), Linux (binary), macOS (app)

import os
import sys

block_cipher = None

# Platform-specific settings
IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'

# Data files to include
datas = [
    ('assets/icons/SUDOKU.ico', 'assets/icons'),
]

# Excludes to reduce binary size
excludes = [
    'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
    'pytest', 'unittest', 'doctest', 'test',
    'IPython', 'jupyter', 'notebook',
    'sphinx', 'docutils',
    'setuptools', 'pip', 'wheel',
]

a = Analysis(
    ['src/sudoku/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific executable options
if IS_WINDOWS:
    icon = 'assets/icons/SUDOKU.ico'
elif IS_MACOS:
    icon = 'assets/icons/SUDOKU.icns' if os.path.exists('assets/icons/SUDOKU.icns') else None
else:
    icon = None

exe_options = {'codesign_identity': None, 'entitlements_file': None} if IS_MACOS else {}
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SudokuMaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=icon,
    **exe_options,
)

if IS_MACOS:
    app = BUNDLE(
        exe,
        name='SudokuMaster.app',
        icon=icon,
        bundle_identifier='com.sudokumaster.game',
        info_plist={
            'CFBundleName': 'Sudoku Master',
            'CFBundleDisplayName': 'Sudoku Master',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'NSHighResolutionCapable': True,
        },
    )
