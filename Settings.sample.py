#!/usr/bin/env python

#Backup Sources.
BackupSources = [
    ['TestDir1', './', 'root'],
    ['TestFile1', './Temp1', '0B_Yf1ZVa9N1acjhSTsMwdVJnVDQ'],
    ['Test File 2', '/Temp 5.py', '0B_Yf1dsa9N1acjhSTUMwdVJnVDQ']
]

ExcludedFileChecks = [
    '.DS_Store',
    'desktop.ini',
    'thumbs.db'
]

BackupExt = "7z"
Timing = 1800

SevenZPath = "C:\\Program Files\\7-Zip\\7z.exe"
