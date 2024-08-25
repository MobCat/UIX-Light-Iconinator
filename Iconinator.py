#!/env/Python3.10.4
#/MobCat (2024)

# This tool will download your UIX Lite config and default.xip
# read them, download icons from your xbox UData 

#WARNING:
# This tool is """beta"""
# It works, but it's sloppy and needs work of it's own.

#TODO:
# Try and rip icons from xbes first, then download from UData, and if both of those fail, then finally try an icon CDN download.

import configparser
import ftplib
from requests import get # get icons from CDN
import os
from socket import socket, AF_INET, SOCK_DGRAM # Get users ip / network ip prefix.
import sys        # Silly little sys.exit()
import json       # Remove this lib once pyxbe is working again and we can remove XBEJson.exe.
import subprocess # Needed for xip.exe and XBEJson.exe
import shutil

# temp removed, lib has some bugs, it's okie.
#from xbe import Xbe 

# Logo Banner
print('''
────────────────────────────────────────────────────────────────────────────────────
░░   ░░░   ░░         ░░   ░░░   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒▒   ▒▒▒▒▒▒ ▒▒▒▒▒ ▒▒▒   ▒▒       ▒▒▒▒      ▒▒▒▒ ▒▒▒▒▒▒▒   ▒▒▒▒▒▒▒▒▒▒▒▒      
███ █████ ██████   ███████  █  █████████   ███   ██████   █      ██  ███  ██  ██  ██
███ █████ ██████   ███████  █  ████   ██   ███   ███      ███ █████  ███  ██    ██  
▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒▒   ▒▒▒▒▒▒ ▒▒▒▒▒ ▒▒▒   ▒▒   ▒▒▒   ▒▒  ▒▒   ▒▒▒ ▒▒ ▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒
░░░░     ░░░░         ░░   ░░░   ░░   ░░   ░░░   ░░░    ░ ░░░░  ░░░░░   ░░░░  ░░░░░░
────────────────────────────────────────────────────────────────────────────────────
Iconinator 20240825
Automatically building an icon pack for the games launcher,
based on the content you have installed on your Xbox HDD.
''')

# Function to get users IP
# Just a simple cheat so you don't have to type a full ip address.
def getIP():
	s = socket(AF_INET, SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()
	return '.'.join(IP.split('.')[:3]) # Weird hack but ok.


# Load custom or default settings ini based on command args.
config = configparser.ConfigParser()
if len(sys.argv) == 1:
	print("Loading default settings.ini")
	settingsINI = 'settings.ini'
else:
	settingsINI = sys.argv[1]
	print(f"Loading {settingsINI}")

# Build a new config if the config we are trying to load does not exist.
if not os.path.isfile(settingsINI):
	print(f"{settingsINI} Does not exist, lets make one.")
	ipPrefix = getIP()
	iniXboxIP = input(f"Enter your xboxs IP address: {ipPrefix}.")
	try:
		int(iniXboxIP)
	except ValueError:
		print(f'{ipPrefix}.{iniXboxIP} is not a number.')
		sys.exit()

	print(f"Saving {settingsINI} with default ftp login creds.\n")
	config['UIXinator'] = {'xbox_IP': f'{ipPrefix}.{iniXboxIP}', 'ftp_Login': 'xbox:xbox', 'cleanup': 'True', 'auto_reboot': 'False', 'iconCDN': 'https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/xbx'}
	with open(settingsINI, 'w') as newConfig:
		config.write(newConfig)

# Actually load the settings from the settings ini file now.
config.read(settingsINI)
defultCreds = config.get('UIXinator', 'ftp_Login')
ftpUserPass = defultCreds.split(':')
xboxIP      = config.get('UIXinator', 'xbox_IP')
CleanupFlag = config.getboolean('UIXinator', 'cleanup')
iconCDN     = config.get('UIXinator', 'iconCDN')
rebootUIX   = config.getboolean('UIXinator', 'auto_reboot')

# Basically just check and setup our ftp connection.
print(f"Connecting to {defultCreds}@{xboxIP}")
try:
	ftp=ftplib.FTP(xboxIP)
	ftp.login(ftpUserPass[0],ftpUserPass[1])
except TimeoutError:
	print("Connection timed out. Is your xbox alive?")
	sys.exit()
except ftplib.error_perm:
	print(f"Unable to log into your xbox FTP server with\nUsername: {ftpUserPass[0]}\nPassword: {ftpUserPass[1]}\nPlease edit 'ftpLogin' in your {settingsINI} file.\nFormat is username:password.")
	sys.exit()

def DirLST(ftp_obj, path="."):
	templst = []
	ftp_obj.cwd("/") # Get back to root, so we can index other paths. F/Games, G/Games
	try:
		ftp_obj.cwd(path)
	except:
		return templst

	contents = ftp_obj.nlst()
	current_path = ftp_obj.pwd()
	for item in contents:
		if item not in [".", ".."]: #CURSED:
			ftp_obj.cwd(f"{current_path}/{item}")
			if "default.xbe" in ftp_obj.nlst():
				templst.append(f"{current_path}/{item}")
	return templst

def DownloadFTP(ftp_obj, remote_path, local_path):
	ftp_obj.cwd("/")
	try:
		ftp_obj.size(remote_path)
		with open(local_path, "wb") as f:
			ftp_obj.retrbinary("RETR " + remote_path, f.write)
	except ftplib.error_perm as e:
		return f"FTP Error {remote_path}: {e}"

def DownloadWEB(titleID):
	r = get(f'{iconCDN}/{titleID[:4].upper()}/{titleID.upper()}.xbx', allow_redirects=True)
	if r.status_code == 200:
		open(f'xbx/{titleID}.xbx', 'wb').write(r.content)
	else:
		return f'ERROR: {r.status_code}'

# Load UIX Config
err = DownloadFTP(ftp, f'C/UIX Configs/config.xbx', f'config.xbx')
if err is None:
	print("Loading UIX Lite Config..")
	UIXconfig = configparser.ConfigParser()
	UIXconfig.read('config.xbx')
	cofigPaths = []
	for option in UIXconfig.options('LauncherMenu'):
		if option.startswith('path') and UIXconfig.get('LauncherMenu', option): # TXT is Uppercase, ConfigParser reads it as lowercase??
			path = UIXconfig.get('LauncherMenu', option)
			cofigPaths.extend(path.split(';'))

	# Remove dupes
	cofigPaths = list(set(cofigPaths))
	# Cleanup
	if CleanupFlag:
		os.remove('config.xbx')

	# Janky build a list of all dash paths for all partitions, E/Games, F/Games, etc..
	ftp.cwd("/")
	contents = ftp.nlst()
	systemBlacklist = ['C', 'X', 'Y', 'Z']
	partishionsLst = [item[-1:] for item in contents if item[-1:] not in systemBlacklist]
	# Now build our finally list of all dashPaths
	dashPaths = []
	for partition in partishionsLst:
		for path in cofigPaths:
			dashPaths.append(f"{partition}/{path}/")
	#print(contents)

	#print(dashPaths)
	#sys.exit()

else:
	print(f"{err}\nIs UIX Lite installed onto C? I can't seem to find your config.xbx")
	sys.exit()

print("Downloading your icons xip to prepare it for updating...")
err = DownloadFTP(ftp, f'C/xboxdashdata.185ead00/default.xip', f'default.xip')
if err is not None:
	print(err)
	sys.exit()

###########################################
# Check if we have a place to save icons too.
if not os.path.exists('xbx'):
    os.makedirs('xbx')

UIXpaths = []
titleIDs = [] # Use for later
print("Downloading xbes and extracting title IDs...\nPlease wait, some large xbes will take time to download...")
for iniDir in dashPaths:
	dirlst = DirLST(ftp, iniDir)
	if len(dirlst) != 0:
		maxlen = len(dirlst)
		cnt = 1
		for gameDir in dirlst:
			print(f"[{iniDir} {cnt}/{maxlen}] Downloading xbes and extracting title IDs...              ", end="\r")
			DownloadFTP(ftp, f'{gameDir}/default.xbe', 'default.xbe')

			# pyxbe almost worked, but it's having virtual address offset issues..
			# It can't handle malformed xbes or xbes with unexpected data yet..
			#xbe = Xbe.from_file('default.xbe')
			#titleID = hex(xbe.cert.title_id)[2:]

			# Backup, Use XBEJson to dump xbe info as json and read back said json.
			conout = subprocess.run(f'lib/XBEJson.exe default.xbe', stdout=subprocess.PIPE).stdout.decode()
			xbeJson = json.loads(conout)
			titleID = xbeJson['Title_ID'].lower()
			UIXpaths.append(f'{gameDir.split("/")[-1]}={titleID}')
			titleIDs.append(titleID)
			cnt += 1
		cnt = 1
	else:
		#input(f"{iniDir} Does not exist on your xbox.")
		print(f"[{iniDir} ?/?] This file path does not exist on your xbox.                              ", end="\r")

# quick house keeping.
os.remove('default.xbe')


print(f"\nFound {len(titleIDs)} titles installed on your xbox currently.\nSaving and uploading UIX icons config...")
with open('Icons.xbx', 'w') as f:
	f.write(f"[default]\n") # I think if we change this to something like [icons] we can load icons form a icon.xip not default.xip maybe..
	for line in UIXpaths:
		f.write(f"{line}\n")

with open('Icons.xbx', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/UIX Configs/")
	ftp.storbinary("STOR Icons.xbx", f)


#####################################################

# Rip icons from xbox, if the icon is not in UData, try downloading one.
#BUG: Not all icons are on CND, homebrew uses whatever title IDs they want.
# We are not ripping icons for xbes yet, this may solve some of these issues, and cause others.
errcnt = 0
for titleID in titleIDs:
	ftp.cwd("/")
	err = DownloadFTP(ftp, f'E/UData/{titleID}/TitleImage.xbx', f'xbx/{titleID}.xbx')
	if err is not None:
		print(f'{titleID}.xbx Not found on xbox, Downloading from db...         ', end="\r")
		err = DownloadWEB(titleID)
		if err is not None:
			print(f'{titleID}.xbx Not on CDN...                                 ', end="\r")
			errcnt += 1

if errcnt > 0:
	print(f"""
{errcnt} icons where missing from the CDN
This is normal for homebrew apps.
Please run the game or homebrew first
then this tool can grab the icon from the games save data.""")

print("\nUpdating your icons xip...")
subprocess.call("lib/xip.exe -m -c default.xip xbx/*.xbx", stdout=subprocess.DEVNULL)

with open('default.xip', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/xboxdashdata.185ead00/")
	ftp.storbinary("STOR default.xip", f)

if CleanupFlag:
	os.remove('default.xip')
	shutil.rmtree("xbx")

if rebootUIX:
	print("Hot rebooting to UIX Lite.")
	ftp.sendcmd('SITE EXEC /C/xboxdash.xbe')

ftp.quit()

input("All done \\^__^/\n Your UIX Lite launcher icons have been updated.\nPress Enter to exit.")

#Note:
# When/if we try and build custom xip from users installed games
# Check if the default.xbe is 6924 bytes in side, we assume this is an xiso attacher and wont have an icon
# So we need to rip it from the save data or download one from the title id database.
# If we don't wanna play it fast'n'lose with basic file size checking
# We could load and check the raw data of the xbe
# 0x00001AA0 to 0x00001AAD == '\Device\CdRom1'
# 0x00001AF8 to 0x00001AFF == '!"# .iso'
# Note that space is 0x00 not 0x23.