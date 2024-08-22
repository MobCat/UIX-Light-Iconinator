#!/env/Python3.10.4
#/MobCat (2024)

#WARNING:
# This is just a PoC
# It was built in an afternoon, it's very sloppy
# but it sorta works, but still needs some work to be done.
# And even then, I hope this "tool" gets outdated and redundant
# as soon as the xbox or UIX can build this icon list on it's own.

#TODO:
# Figure out the xbx xip packing thing.
# Replace XBEJson with pyxbe when ready.
#TODO QoL:
# Do a better job at DirLST error handler.
# Build a default settings.ini if no ini is found.
# allow for iconinator.py customSettings.ini
# add yes to all for dbcheck

import configparser
import ftplib
import requests
import os
import json        # Remove this lib once pyxbe is working again.
import subprocess  # Remove this lib once pyxbe is working again.

# temp removed, lib has some bugs, it's okie.
#from xbe import Xbe 

# Load settings ini file.
config = configparser.ConfigParser()
config.read('settings.ini')

defultCreds = config.get('Iconinator', 'ftpLogin')
ftpUserPass = defultCreds.split(':')
xboxIP = config.get('Iconinator', 'xboxIP')
gameDirs = json.loads(config.get('Iconinator','gameDirs'))


# Basically just check and setup our ftp connection.
print(f"Connecting to {defultCreds}@{xboxIP}")
try:
	ftp=ftplib.FTP(xboxIP)
	ftp.login(ftpUserPass[0],ftpUserPass[1])
except TimeoutError:
	print("Connection timed out. Is your xbox alive?")
	exit()


def DirLST(ftp_obj, path="."):
	templst = []
	ftp_obj.cwd("/") # Get back to root, so we can index other paths. F/Games, G/Games
	ftp_obj.cwd(path)
	contents = ftp_obj.nlst()
	current_path = ftp_obj.pwd()
	for item in contents:
		if item not in [".", ".."]: #CURSED:
			ftp_obj.cwd(f"{current_path}/{item}")
			if "default.xbe" in ftp_obj.nlst():
				templst.append(f"{current_path}/{item}")
	return templst

def DownloadFTP(ftp_obj, remote_path, local_path):
	try:
		ftp_obj.size(remote_path)
		with open(local_path, "wb") as f:
			ftp_obj.retrbinary("RETR " + remote_path, f.write)
	except ftplib.error_perm as e:
		return f"FTP Error {remote_path}: {e}"

def DownloadWEB(titleID):
	r = requests.get(f'https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/xbx/{titleID[:4]}/{titleID}.xbx', allow_redirects=True)
	open(f'xbx/{titleID}.xbx', 'wb').write(r.content)

UIXpaths = []
titleIDs = [] # Use for later
print("Downloading xbes and extracting title IDs...")
for iniDir in gameDirs:
	try:
		dirlst = DirLST(ftp, iniDir)
	except ftplib.error_perm as e:
		print(f'\nE:{e}\nPlease fix your settings ini')
		exit()

	maxlen = len(dirlst)
	cnt = 1
	for gameDir in dirlst:
		print(f"[{iniDir} {cnt}/{maxlen}] Downloading xbes and extracting title IDs...", end="\r")
		DownloadFTP(ftp, f'{gameDir}/default.xbe', 'default.xbe')

		# pyxbe almost worked, but its having virtual address offset issues..
		# It can't handle malformed xbes or xbes with unexpected data yet..
		#xbe = Xbe.from_file('default.xbe')
		#titleID = hex(xbe.cert.title_id)[2:]

        # Backup, Use XBEJson to dump xbe info as json and read back said json.
		conout = subprocess.run(f'XBEJson.exe default.xbe', stdout=subprocess.PIPE).stdout.decode()
		xbeJson = json.loads(conout)
		titleID = xbeJson['Title_ID'].lower()
		UIXpaths.append(f'{gameDir.split("/")[-1]}={titleID}')
		titleIDs.append(titleID)
		cnt += 1
	cnt = 1

# quick house keeping.
os.remove('default.xbe')


print("\nSaveing and uploading UIX icons config...")
with open('Icons.xbx', 'w') as f:
	f.write(f"[default]\n") # I think if we change this to something like [icons] we can load icons form a icon.xip not default.xip maybe..
	for line in UIXpaths:
		f.write(f"{line}\n")

with open('Icons.xbx', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/UIX Configs/")
	ftp.storbinary("STOR Icons.xbx", f)

# Rip icons from xbox or download new ones.
try:
	iconSelect = input("""[Icon downloader]
1. Download Icons from your console
   (Fast, however you need to run the game first, before you can download it's icon)

2. Download from online database
   (Slow and incomplete, but you don't need to run the game first)
   (Database only contains icons for 'Retail Games')

Press Ctrl+c to quit
Your Icons.xbx file was built and sent to your console but you don't need any new icons

Default input is 1.
Select input: """)
except KeyboardInterrupt:
	print("Goodbye ^__^/")
	exit()

# Setup a place to download icons to.
if not os.path.exists('xbx'):
	os.makedirs('xbx')

if iconSelect == "2":
	print("Downloading...")
	maxlen = len(titleIDs)
	cnt = 1
	for titleID in titleIDs:
		print(f"[{cnt}/{maxlen}] {titleID}.xbx", end="\r")
		DownloadWEB(titleID.upper())
		cnt += 1
else:
	for titleID in titleIDs:
		ftp.cwd("/")
		err = DownloadFTP(ftp, f'E/UData/{titleID}/TitleImage.xbx', f'xbx/{titleID}.xbx')
		if err is not None:
			print(err)
			dbcheck = input("Try and grab it from the online database? [Y/n]: ")
			if dbcheck != "n":
				print(f'Downloading {titleID}.xbx')
				DownloadWEB(titleID)

print("\nEnd of PoC\nMore to come soon™")
#TODO:
# Now we have a folder of xbx icons based on the games in your Icons.xbx list,
# we need to some how pack them into the default.xip
# idk how to do that...