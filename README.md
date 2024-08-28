# UIXinator
![logo](logo.png)<br>
A selection of tools to automate some of the setup and customization process of [UIX Lite](https://github.com/OfficialTeamUIX/UIX-Lite)

> [!WARNING]  
> This project is in "beta".<br>
> It is unfinished and sloppy. Some icons may brake the launcher<br>
> But it does work, but it also needs work.

# Pre-requirements
You should have [UIX Lite](https://github.com/OfficialTeamUIX/UIX-Lite) already installed and setup. 
<sub>Might build a tool for this lator, idk</sub><br>
Some sort of FTP server running on your xbox, whether this be another custom dashboard or a dedicated FTP app.<br>
I would recommend the UnleashX custom dashboard for FTP, or any FTP server that supports the UnleashX SITE commands.<br>

# Setup (Windows)
The pre-built release pack only contains windows binaries currently. Sorry.<br>
1. Download and extract to a folder the latest build of UIXinator ([UIXinator-20240825.zip](https://github.com/MobCat/UIXinator/releases/download/build-20240825/UIXinator-20240825.zip)).
2. Real xbox:<br>
   Turn your xbox on, make sure it's FTP server is running and it's on the same network as your computer.<br>
   XEMU:<br>
   Make sure your NAT settings are enabled, setup and your emulated xbox is running and ftp server of some kind.<br>See [XEMU FTP Setup](https://xemu.app/docs/ftp/) for more info.<br>
   Then run XEMU first, then run a UIX tool. The tool will now detect XEMUs 2121 port and build a setup for it.<br>
3. Run one of the included tools, for eg `Iconinator.exe` at least once.
4. On first launch of any UIX tool in this pack, you will be prompted to setup a `settings.ini` file, just follow the prompts.<br>
<sub>Basically you just need to enter the end of your xboxs IP, and make sure it's turned on, running it's FTP server and connected to the same network as your computer, easy peasy.<br>
on XEMU you just need to hit enter once or twice, even easier.</sub><br>

Once you have made this `settings.ini` file on first launch of any UIXinator tool, you won't need to do it again.<br>Running the tool exe again will auto load the `settings.ini`.<br>

# Setup (Advance settings ini)
After you have ran one of the UIXinator tools at least once, you should have a new file called `settings.ini` in the root of UIXinator<br>
Make a copy of this and rename it to something like `GamesRoomXbox.ini` if for eg. you have an xbox in your games room you want to edit.<br>
Or you can run one of the UIX tools from the command line like `Iconinator.exe GamesRoomXbox.ini`, <br>
it will notice that `GamesRoomXbox.ini` is missing, and prompt you to make a new one, the same as the default first boot promt.<br>
Open this ini file with notepad or an IDE of your choosing.<br>
You should now see some variables<br>
```ini
[UIXinator]
xbox_ip = This is the ip address of your xbox
xbox_port = the port address of your xbox. 21 for real FTP and 2121 for XEMU.
ftp_login = ftp server username : ftp server password
cleanup = If True, the tool will clean up after its self, deleting the downloaded icon xbx and default.xip
auto_reboot = if True and your FTP server supports UnleashX SITE commands, will relaunch the stock dashboard after have
icon_cdn = URL to a folder XBX icons. formatted like 4D53/4D530064.xbx PublisherHexcode/titleID.xbx
```
You can now edit these variables= to your needs, then save the ini file.
If you wish to use these settings with one of the UIXinator tools, just drag'n'drop the new `GamesRoomXbox.ini`<br>
to the UIXinator tool exe and it will open the tool with your chosen settings.<br>
Or you can run the command again, `Iconinator.exe GamesRoomXbox.ini` now `GamesRoomXbox.ini` excists, the tool will use this config instead of `settings.ini`.<br>

Alternatively, you can just make edits to the default `settings.ini` and run the tools like normal,<br>
if for eg, you want to change your xbox ftp server login to something other then the defaults but don't want to make a full custom settings ini.

# UIXinator tools
### Iconinator
A tool that automates the process of setting up launcher icons<br>
This tool will connect to your xbox via FTP, download a games list and get icons of all the games you have currently installed on your xbox,<br>
build your custom `icons.xbx` icon list and `default.xip` icon pack, then re-upload them to your xbox.<br>

TODO: Get/wait for pyxbe to work more reliabily.<br>
Might be able to just rip icons directly from xbxs with pyxbe, but Idk if that's going to work for homebrew or old xbox games, titles pre XDK 4928..<br>
Really pre XDK 5849 but idk when the spec for icons was fully locked in.<br><br>

# How to Build from source
<i>TODO</i>: Explain this more/better<br><br>
-1. Install 7-zip. You should already have 7-zip..?<br>
0. Make sure you have python 3.10.4 or newer installed, install the requests and cx_Freeze libs.<br>
But you can run `pip install -r requirements.txt` if you want to do it automatically.
1. Clone this repo<br>
2. Download XIP from the [UIX-Lite github](https://github.com/OfficialTeamUIX/UIX-Lite/releases) releases page.<br>
for eg, `XIP-v240824.Rev1.zip`<br>
3. Extract `xip.exe` into the `lib` folder, so it lives next to `XBEJson.exe`<br>
4. Run the `buildEXEs.bat` to build the python exes and make a zip of the whole app for upload.<br>
