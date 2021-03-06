#!/usr/bin/env python

import subprocess
from datetime import datetime, timedelta
import os
import tempfile
import socket
import sys
import colorama

import Settings #Custom Backup Settings

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")

def LastModified(Path):
    if os.path.isfile(Path):
        #print "Found a single file."
        SourceLastModified = datetime.fromtimestamp(os.stat(Path).st_mtime)
    elif os.path.isdir(Path):
        #print "Found a directory.  Let\'s walk it..."
        ModificationTimes = []

        for root, dirnames, filenames in os.walk(Path):
            for filename in filenames:
                if os.path.basename(filename) in Settings.ExcludedFileChecks:
                    pass
                else:
                    FileModTime = datetime.fromtimestamp(os.stat(os.path.join(root, filename)).st_mtime)
                    ModificationTimes.append(FileModTime)
                    #print "Modification Date of " + filename + " is: " + str(FileModTime)

        ModificationTimes.sort(reverse=True)
        #print ModificationTimes
        SourceLastModified = ModificationTimes[0]
    else:
        #Fail
        SourceLastModified = datetime.fromtimestamp('0')

    return SourceLastModified

gauth = GoogleAuth()

# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    #gauth.Refresh()
    gauth.LocalWebserverAuth()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)


CurrentTime = datetime.now()

for Source in Settings.BackupSources:
    SourceLastModified = LastModified(Source[1])
    ModificationAge = CurrentTime - SourceLastModified

    #print "Current Time: " + str(CurrentTime) + "\nModifitcation Age: " + str(ModificationAge) + "\nLast Modified: " + str(SourceLastModified)

    if ModificationAge < timedelta(seconds=Settings.Timing):
        sys.stdout.write('Backing up \"' + Source[0] + '\"...   ')
        sys.stdout.flush()

        BackupTime=datetime.today().strftime("%Y%m%d-%H%M%S")

        BackupName=Source[0] + " (" + BackupTime + " via " + socket.gethostname() + ")"
        BackupPath=os.path.join(tempfile.gettempdir(), BackupName + "." + Settings.BackupExt)

        cmd = [Settings.SevenZPath, 'a', BackupPath, Source[1], '-mx9']
        sp = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).wait()

        file2upload = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": Source[2]}]})
        file2upload['title'] = BackupName + "." + Settings.BackupExt
        file2upload.SetContentFile(BackupPath)
        file2upload.Upload()

        try:
            os.remove(BackupPath)
        except WindowsError as e:
            print "Unable to remove file. (Win32 Error)"
            print "DEBUG ME: " + str(e)
            continue

        print "[" + colorama.Fore.GREEN + "DONE" + colorama.Style.RESET_ALL + "]"
    else:
        print "Skipping \"" + Source[0] + "\".   [" + colorama.Fore.WHITE + "PASS" + colorama.Style.RESET_ALL + "]"
