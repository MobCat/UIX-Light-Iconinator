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
# add yes to all for dbcheck

import configparser
import ftplib
import requests
import os
import socket                    # Probs dont need the whole sockets lib...
import sys                       # Silly little sys.exit()
import json                      # Remove this lib once pyxbe is working again.
import subprocess                # Remove this lib once pyxbe is working again.

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
Iconinator 20240823
''')

# Function to get users IP
# Just a simple cheat so you dont have to type a full ip addess.
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
	return '.'.join(IP.split('.')[:3]) # Weid hack but ok.



# Load custom or default settings ini based on command args.
config = configparser.ConfigParser()
if len(sys.argv) == 1:
	print("Loading default settings.ini")
	settingsINI = 'settings.ini'
else:
	settingsINI = sys.argv[1]
	print(f"Loading {settingsINI}")

# Build a new config if the config we are trying to load does not excist.
if not os.path.isfile(settingsINI):
	print(f"{settingsINI} Does not excist, lets make one.")
	ipPrefix = getIP()
	iniXboxIP = input(f"Enter your xboxs IP address: {ipPrefix}.")
	try:
		int(iniXboxIP)
	except ValueError:
		print(f'{ipPrefix}.{iniXboxIP} is not a number.')
		sys.exit()

	print(f"Saving {settingsINI} with default ftp login creds.\n")
	#config['UIXinator'] = {'xboxIP': iniXboxIP, 'ftpLogin': 'xbox:xbox'}
	jsonConfig = {}
	config['UIXinator'] = {'xbox_IP': f'{ipPrefix}.{iniXboxIP}', 'ftp_Login': 'xbox:xbox'}
	with open(settingsINI, 'w') as newConfig:
		config.write(newConfig)

# Actually load the settings from the settings ini file now.
config.read(settingsINI)
defultCreds = config.get('UIXinator', 'ftp_Login')
ftpUserPass = defultCreds.split(':')
xboxIP = config.get('UIXinator', 'xbox_IP')


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
	try:
		ftp_obj.size(remote_path)
		with open(local_path, "wb") as f:
			ftp_obj.retrbinary("RETR " + remote_path, f.write)
	except ftplib.error_perm as e:
		return f"FTP Error {remote_path}: {e}"

def DownloadWEB(titleID):
	r = requests.get(f'https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/xbx/{titleID[:4]}/{titleID}.xbx', allow_redirects=True)
	open(f'xbx/{titleID}.xbx', 'wb').write(r.content)

# Load UIX Config
err = DownloadFTP(ftp, f'C/UIX Configs/config.xbx', f'config.xbx')
if err is None:
	print("Loading UIX Lite Config..")
	UIXconfig = configparser.ConfigParser()
	UIXconfig.read('config.xbx')
	cofigPaths = []
	for option in UIXconfig.options('LauncherMenu'):
		if option.startswith('path') and UIXconfig.get('LauncherMenu', option): # TXT is Uppercase, ConfigParser reades it as lowercase??
			path = UIXconfig.get('LauncherMenu', option)
			cofigPaths.extend(path.split(';'))

	# Remove dupes
	cofigPaths = list(set(cofigPaths))
	# Cleanup
	os.remove('config.xbx')

	# Janky build a list of all dash paths for all partisions, E/Games, F/Games, etc..
	ftp.cwd("/")
	contents = ftp.nlst()
	systemBlacklist = ['C', 'X', 'Y', 'Z']
	partishionsLst = [item[-1:] for item in contents if item[-1:] not in systemBlacklist]
	# Now build our finaly list of all dashPaths
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


###########################################
UIXpaths = []
titleIDs = [] # Use for later
print("Downloading xbes and extracting title IDs...\nPlease wait, some large xbes will take time to download...")
for iniDir in dashPaths:
	dirlst = DirLST(ftp, iniDir)
	if len(dirlst) != 0:
		maxlen = len(dirlst)
		cnt = 1
		for gameDir in dirlst:
			print(f"[{iniDir} {cnt}/{maxlen}] Downloading xbes and extracting title IDs...       ", end="\r")
			DownloadFTP(ftp, f'{gameDir}/default.xbe', 'default.xbe')

			# pyxbe almost worked, but it's having virtual address offset issues..
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
	else:
		#input(f"{iniDir} Does not excist on your xbox.")
		print(f"[{iniDir} ?/?] This file path does not exist on your xbox.                      ", end="\r")

# quick house keeping.
os.remove('default.xbe')


print(f"\nFound {len(titleIDs)} titles installed on your xbox currently.\nSaveing and uploading UIX icons config...")
with open('Icons.xbx', 'w') as f:
	f.write(f"[default]\n") # I think if we change this to something like [icons] we can load icons form a icon.xip not default.xip maybe..
	for line in UIXpaths:
		f.write(f"{line}\n")

with open('Icons.xbx', "rb") as f:
	ftp.cwd("/")
	ftp.cwd("C/UIX Configs/")
	ftp.storbinary("STOR Icons.xbx", f)


# Check to see if you have a some custom icons installed
#BUG: This check will fail if UIX Lite is not installed, *However* the download config and sys exit stage *should* cover it.. should..
#BUGBUG: If default.xip is *missing* from your xbox, this script will just crash. we should do a try: or smh, but tbh if default.xip is missing you have bigger issues that launcher icons can't solve.
NewDownload = False
ftp.cwd("/")
xipSize = ftp.size('C/xboxdashdata.185ead00/default.xip')
if xipSize <= 1081701:
	GetAIO = input(f'''
It appears you have the stock icon pack installed, or not a lot of icons installed.
Would you like to D̲ownload a pre-made icon pack or
Build a C̲ustom icon pack from content installed on your xbox.

(PLEASE NOTE: In this beta only downloading custom icons is implemented. Just prese Enter.
idk how to build my own xip file yet.)
Input selection [D/c]: ''')
	if GetAIO != 'c':
		print("Downloading custom icon pack...")
		#TODO: Check if we already have it downloaded so we dont overwright it.
		#TODO: Change this link to the UIX github repo or somewhere more "officle" then my repo.
		url = 'https://raw.githubusercontent.com/MobCat/UIXinator/main/default.xip'
		response = requests.get(url, stream=True)
		total_size = int(response.headers.get('content-length', 0))
		progress_bar_size = 50
		with open('default.xip', 'wb') as f:
			for data in response.iter_content(1024): #1 Kibibyte chunk size
				f.write(data)
				progress = int(f.tell() * progress_bar_size / total_size)
				print(f"\r[{'█' * progress}{' ' * (progress_bar_size - progress)}] {f.tell()/1024/1024:.2f} MB / {f.tell() * 100 / total_size:.2f}% ", end="")
				
		print("\nDownload complete.\nUploading default.xip to your xbox..")
		with open('default.xip', "rb") as f:
			ftp.cwd("/")
			ftp.cwd("C/xboxdashdata.185ead00/")
			ftp.storbinary("STOR default.xip", f)
		NewDownload = True

#Kinda a weird check but I want to skip asking the user to reupload something they JUST downloaded
#It felt awkward
if os.path.exists('default.xip') and NewDownload != True:
	reupCheck = input("\nIt appears you already have a default.xip ready to go,\nWould you like to re-upload it and install it to your xbox? [Y/n]: ")
	if reupCheck != 'n':
		print("Uploading default.xip to your xbox..")
		with open('default.xip', "rb") as f:
			ftp.cwd("/")
			ftp.cwd("C/xboxdashdata.185ead00/")
			ftp.storbinary("STOR default.xip", f)

print("All Done \\^__^/")
print("\nEnd of Beta\nMore to come soon™")
input("Press Enter to exit.")
sys.exit()

##################################################################################################################################
# "Dead" code line
# It's not dead, just not ready yet. but it works. so I'm not removing it, I'm just waiting for external tools and stuffs.
##################################################################################################################################

# Rip icons from xbox or download new ones.
try:
	iconSelect = input("""
[Icon downloader]
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
	sys.exit()

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


#TODO:
# Now we have a folder of xbx icons based on the games in your Icons.xbx list,
# we need to some how pack them into the default.xip
# idk how to do that...

#Note:
# When/if we try and build custom xip from users installed games
# Check if the default.xbe is 6924 bytes in side, we assume this is an xiso attacher and wont have an icon
# So we need to rip it from the save data or download one from the title id database.
# If we dont wanna play it fast'n'lose with basic file size checking
# We could load and check the raw data of the xbe
# 0x00001AA0 to 0x00001AAD == '\Device\CdRom1'
# 0x00001AF8 to 0x00001AFF == '!"# .iso'
# Note that space is 0x00 not 0x23.