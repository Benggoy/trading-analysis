#!/usr/bin/env python3
"""
setup.py for creating Mac app bundle using py2app
Alternative to PyInstaller - more Mac-native
"""

from setuptools import setup
import sys
import os

# Check if running on macOS
if sys.platform != 'darwin':
    print("This setup script is for macOS only")
    sys.exit(1)

APP = ['ultimate_rsi_tracker.py']
DATA_FILES = [
    ('', ['watchlist.json']) if os.path.exists('watchlist.json') else [],
    ('', ['sample_portfolio.csv']) if os.path.exists('sample_portfolio.csv') else []
]

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'Ultimate Enhanced RSI Tracker',
        'CFBundleDisplayName': 'Ultimate Enhanced RSI Tracker',
        'CFBundleGetInfoString': "Ultimate Enhanced RSI Stock Tracker with Charts",
        'CFBundleIdentifier': 'com.benggoy.ultimate-enhanced-rsi-tracker',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Benggoy. All rights reserved.',
        'NSHighResolutionCapable': True,
    },
    'packages': ['yfinance', 'pandas', 'numpy', 'matplotlib', 'plotly', 'tkinter'],
    'includes': ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.simpledialog', 'tkinter.filedialog'],
    'excludes': ['matplotlib.tests', 'numpy.tests', 'pandas.tests'],
    'optimize': 2,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='Ultimate Enhanced RSI Tracker',
    version='2.0.0',
    description='Ultimate Enhanced RSI Stock Tracker with Charts & Portfolio Import',
    author='Benggoy',
    python_requires='>=3.8',
)
