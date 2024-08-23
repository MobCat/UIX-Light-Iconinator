# UIX-Lite Iconinator
Automatically build and pack game icons for the games launcher in UIX Lite beta.

> [!WARNING]  
> This project is just a PoC<br>
> It is unfinished, sloppy, and hopefully will be made redundant soon.<br>
> Also haven't done a good job explaining wtf is going on here either..

# How to setup and use
1. Click the green Code button, then Download ZIP
2. Extract the project zip <i>somewhere</i>
3. (optional) If you don't already have the `requests` library installed, or you have no idea what that means<br>
run `pip install -r requirements.txt` command in the root of where you extracted the zip to.
4. Edit the `settings.ini` with notepad or your IDE of choice.
```
[Iconinator]
xboxIP = 192.168.1.81
ftpLogin = xbox:xbox
gameDirs = [
	"F/Games/",
	"E/Games/",
	"E/Apps/"
	]
```
You need to at least edit `xboxIP` to the IP of your xbox, this info is normally found somewhere on your custom dashboard or under a network settings menu.<br>
If you want to scan more file paths on your xbox then the default, for eg `G/Games/` you will need to add that to the config 
```
gameDirs = [
  "F/Games/",
  "E/Games/",
  "G/Games/",
  "E/Apps/",
  "F/Homebrew/",
  "F/Emulators/"
  ]
```
BUG: Please note, the script does not have good error handling for paths that don't exist on your xbox but are in the config.<br><br>
5. (optional) If you do not wish to download icons from the internet or you have custom icons or homebrew icons,<br>
you will have to launch the game on your console at least once. So save data is generated, and this tool can download the save icon.<br>
TODO: Once I get pyxbe working, we might be able to just rip icons from xbxs, but Idk if that's going to work for homebrew or not..<br><br>
6. Just run `python Iconinator.py` <sub>(or `python3 Iconinator.py` if you are on linux)</sub><br>
and the script will scan your `gameDirs` on your xbox, find all the default.xbe files, extract the title ids, build a new icons.xbx file<br>
and give you the option to download icons from the internet, download from your console (default, just press enter) or skip if you have icons but just wanted to update icons.xbx
