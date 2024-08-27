#!/env/Python3.10.4
#/MobCat (2024)

# This tool will download your UIX Lite config and default.xip
# read them, download icons from your xbox UData 

#WARNING:
# This tool is """beta"""
# It works, but it's sloppy and needs work of it's own.

#TODO:
# Try and rip icons from xbes first, then download from UData, and if both of those fail, then finally try an icon CDN download.
# Maybe also figure out if we can "fix" fake xbx images to real ones.

import configparser
import ftplib
from requests import get # get icons from CDN
import os
import socket     # Get users ip, network ip prefix and ping XEMU
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
Iconinator 20240827
Automatically building an icon pack for the games launcher,
based on the content you have installed on your Xbox HDD.
''')

# Function to get users IP
# Just a simple cheat so you don't have to type a full ip address.
def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	portCheck = s.connect_ex(('127.0.0.1', 2121)) == 0
	s.close()

	return ['.'.join(IP.split('.')[:3]), portCheck] # Weird hack but ok.


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
	try:
		if not ipPrefix[1]:
			iniXboxIP = input(f"Enter your xboxs IP address: {ipPrefix[0]}.")
			int(iniXboxIP)
			newXboxPort = 21
			NewXboxIP = f'{ipPrefix[0]}.{iniXboxIP}'
		else:
			XEMUCheck = input("XEMU Detected. Setup Iconinator for XEMU? [Y/n]: ")
			#CURSED: Force a bad int convert so we trip the 
			# except ValueError to "exit" this auto XEMU setup
			if XEMUCheck == 'n': int(XEMUCheck)
			newXboxPort = 2121
			NewXboxIP = '127.0.0.1'

	except (ValueError, KeyboardInterrupt):
		print(f'\nNot a valid IP, or no IP set.')
		CustomIP = input(f"Enter a custom IP Address:Port ").split(':')
		NewXboxIP = CustomIP[0]
		newXboxPort = int(CustomIP[1])

		
	print(f"Saving {settingsINI} with default ftp login creds.\n")
	config['UIXinator'] = {'xbox_IP': NewXboxIP, 'xbox_port': newXboxPort, 'ftp_Login': 'xbox:xbox', 'cleanup': 'True', 'auto_reboot': 'False', 'icon_cdn ': 'https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/xbx'}
	with open(settingsINI, 'w') as newConfig:
		config.write(newConfig)
########################################################################################################################
# Actually load the settings from the settings ini file now.
config.read(settingsINI)
defultCreds = config.get('UIXinator', 'ftp_Login')
ftpUserPass = defultCreds.split(':')
xboxIP      = config.get('UIXinator', 'xbox_IP')
xboxPort    = config.getint('UIXinator', 'xbox_port')
CleanupFlag = config.getboolean('UIXinator', 'cleanup')
iconCDN     = config.get('UIXinator', 'icon_cdn')
rebootUIX   = config.getboolean('UIXinator', 'auto_reboot')

########################################################################################################################
# Setup our ftp connection, based on the server.
# And check it to make sure the server is alive and you have al the right creds.
print(f"Connecting to {defultCreds}@{xboxIP}:{xboxPort}")
try:
	# If xemu
	if xboxIP == '127.0.0.1': 
		class MyFTP(ftplib.FTP):
			def sendport(self, host, port):
				return super(MyFTP, self).sendport('10.0.2.2', port)

		ftp = MyFTP()
		ftp.connect(xboxIP, xboxPort)
		ftp.login(ftpUserPass[0], ftpUserPass[1])
		ftp.set_pasv(False)
	else:
		# Else real xbox.
		ftp = ftplib.FTP()
		ftp.connect(xboxIP, xboxPort)
		ftp.login(ftpUserPass[0], ftpUserPass[1])
		ftp.set_pasv(True)

except TimeoutError:
	print("Connection timed out. Is your xbox alive?")
	input("Press Enter to exit.")
	sys.exit()
except ftplib.error_perm as e:
	print(f"Unable to log into your xbox FTP server with\nUsername: {ftpUserPass[0]}\nPassword: {ftpUserPass[1]}\nPlease edit 'ftpLogin' in your {settingsINI} file.\nFormat is username:password.\n[{e}]")
	input("Press Enter to exit.")
	sys.exit()
except ConnectionRefusedError as e:
	if xboxIP == '127.0.0.1':
		print("ERROR: XEMU is weird, sorry.. Make sure your FTP server is fully booted though.\nPress Enter to exit.")
	else:
		print(f"ERROR: Connection refused by host\nMake sure your FTP server has fully booted.\n{e}\nPress Enter to exit.")
	sys.exit()

########################################################################################################################
# Funky funcs
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
		return f"FTP Error: {remote_path}: {e}"
	except ConnectionRefusedError as e:
		return f"FTP Error: {remote_path}: Your xbox has refused the connection attempt from Iconinator.\nPlease make sure your ftp server has compleated booting and is ready for connections.\n{e}"

def DownloadWEB(titleID):
	r = get(f'{iconCDN}/{titleID[:4].upper()}/{titleID.upper()}.xbx', allow_redirects=True)
	if r.status_code == 200:
		open(f'xbx/{titleID}.xbx', 'wb').write(r.content)
	else:
		return f'WEB ERROR: {r.status_code}'

########################################################################################################################
# Load UIX Config
err = DownloadFTP(ftp, f'C/UIX Configs/config.xbx', f'config.xbx')
if err is None:
	print("Loading UIX Lite Config...")
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
	#TODO: Check [ExtendedPartitions] Partitions=1
	#If 1 only scan F, if 2 Scan F and G, etc..
	ftp.cwd("/")
	contents = ftp.nlst()
	systemBlacklist = ['C', 'X', 'Y', 'Z']
	partishionsLst = [item[-1:] for item in contents if item[-1:] not in systemBlacklist]
	# Now build our finally list of all dashPaths
	dashPaths = []
	for partition in partishionsLst:
		for path in cofigPaths:
			dashPaths.append(f"{partition}/{path}/")

else:
	print(f"\nERROR: Is UIX Lite installed onto C:?\nI can't seem to find your config.xbx.\n{err}")
	input("Press Enter to exit.")
	sys.exit()

print("\nDownloading your icons xip to prepare it for updating...")
err = DownloadFTP(ftp, f'C/xboxdashdata.185ead00/default.xip', f'default.xip')
if err is not None:
	print(err)
	input("Press Enter to exit.")
	sys.exit()

########################################################################################################################
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


print(f"\nFound {len(titleIDs)} titles installed on your xbox currently.\n\nSaving and uploading UIX icons config...")
with open('Icons.xbx', 'w') as f:
	f.write(f"[default]\n") # I think if we change this to something like [icons] we can load icons form a icon.xip not default.xip maybe..
	for line in UIXpaths:
		f.write(f"{line}\n")

with open('Icons.xbx', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/UIX Configs/")
	ftp.storbinary("STOR Icons.xbx", f)


########################################################################################################################
# Rip icons from xbox, if the icon is not in UData, try downloading one.
#BUG: Not all icons are on CND, homebrew uses whatever title IDs they want.
#BUG: If the icon is "fake", we delete it. But we don't do anything to try and fix it.
# We are not ripping icons for xbes yet, this may solve some of these issues, and cause others.
errcnt = 0
badcnt = 0
addcnt = 0
for titleID in titleIDs:
	ftp.cwd("/")
	err = DownloadFTP(ftp, f'E/UData/{titleID}/TitleImage.xbx', f'xbx/{titleID}.xbx')
	if err is not None:
		print(f'{titleID}.xbx Not found on xbox, Downloading from db...         ', end="\r")
		err = DownloadWEB(titleID)
		if err is not None:
			print(f'{titleID}.xbx Not on CDN...                                 ', end="\r")
			errcnt += 1
		else:
			addcnt += 1
	else:
		addcnt += 1

	# Shitty check
	# if the icon is not a correctly formatted xbx image, throw it away.
	if os.path.isfile(f'xbx/{titleID}.xbx'):
		with open(f'xbx/{titleID}.xbx', 'rb') as file:
			fileMagic = file.read(4)
		if fileMagic.hex() != '58505230':
			print(f'{titleID}.xbx Was "fake". Removing..')
			os.remove(f'xbx/{titleID}.xbx')
			badcnt += 1
			addcnt -= 1
			#TODO: Maybe we could replace with a missing icon?
			#Or lol just wait for someone to make a CND with pre formatted xbxs
			#These xbx icons from my DB are direct rips from the game, so if the dev played it fast'n'lose with the spec
			#it brakes the launcher but not the memory view for some reason.
print(f"Done. {addcnt} icons where added to your default.xip icon pack.")


if errcnt > 0 or badcnt > 0:
	print(f"""
{errcnt} icons where missing from the CDN
{badcnt} icons where 'fake' xbx icons (renamed DDS, PNG, BMP, etc..)
Missing Icons is normal for homebrew apps.
Please run the game or homebrew first, 
so this tool can grab the icon from it's save data.
Weird formatted icons was just part of early xbox dev,
we have to fix these icons ourselves and put them on the CDN.""")

print("\nUpdating your icons xip...")
subprocess.call("lib/xip.exe -m -c default.xip xbx/*.xbx", stdout=subprocess.DEVNULL)

with open('default.xip', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/xboxdashdata.185ead00/")
	ftp.storbinary("STOR default.xip", f)

if CleanupFlag:
	os.remove('default.xip')
	os.remove('Icons.xbx')
	shutil.rmtree("xbx")

if rebootUIX:
	print("Hot rebooting to UIX Lite.")
	ftp.sendcmd('SITE EXEC /C/xboxdash.xbe')

ftp.quit()

input("\nAll done \\^__^/\nYour UIX Lite launcher icons have been updated.\nPress Enter to exit.")

#Note:
# When/if we try and build custom xip from users installed games
# Check if the default.xbe is 6924 bytes in side, we assume this is an xiso attacher and wont have an icon
# So we need to rip it from the save data or download one from the title id database.
# If we don't wanna play it fast'n'lose with basic file size checking
# We could load and check the raw data of the xbe
# 0x00001AA0 to 0x00001AAD == '\Device\CdRom1'
# 0x00001AF8 to 0x00001AFF == '!"# .iso'
# Note that space is 0x00 not 0x23.

# In the config, we may be able to set PartitionScanCompleted=false
# then boot back to dashboard after we have edited icons or uploaded new games
# So UIX auto re-scans partitions for games on boot.