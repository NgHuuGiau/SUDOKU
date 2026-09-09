# PyInstaller build configuration for Sudoku
# Usage: pyinstaller build.spec
# Cross-platform: Windows (exe), Linux (binary), macOS (app)

import sys
import os

block_cipher = None

# Platform-specific settings
IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# Data files to include
datas = [
    ('Picture', 'Picture'),
    ('sounds', 'sounds'),
]

# Hidden imports
hiddenimports = [
    'pygame',
    'tkinter',
    'tkinter.ttk',
    'tkinter.font',
    'tkinter.messagebox',
    'json',
    'datetime',
    'copy',
    'random',
    'math',
    'ctypes',
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
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
        console=False,  # Windowed app (no console)
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='Picture/SUDOKU.ico',
    )
elif IS_MACOS:
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
        codesign_identity=None,
        entitlements_file=None,
        icon='Picture/SUDOKU.icns' if os.path.exists('Picture/SUDOKU.icns') else None,
    )
    
    app = BUNDLE(
        exe,
        name='SudokuMaster.app',
        icon='Picture/SUDOKU.icns' if os.path.exists('Picture/SUDOKU.icns') else None,
        bundle_identifier='com.sudokumaster.game',
        info_plist={
            'CFBundleName': 'Sudoku Master',
            'CFBundleDisplayName': 'Sudoku Master',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'NSHighResolutionCapable': True,
        },
    )
else:  # Linux
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
    )