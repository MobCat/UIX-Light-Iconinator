:: Clean up build folder.
:: This may be redundant, think cx_Freeze can do this on its own. but this is "more reliable"
@RD /S /Q "build"
:: set buildDate
@set buildDate=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%
:: Then make a new build
python build-Iconinator.py build

:: Copy XBEJson, This extra exe will be removed soonTM
@xcopy lib\XBEJson.exe build\exe.win-amd64-3.10\lib\
:: Copy xip.exe for batch editing the default.xip
@xcopy lib\xip.exe build\exe.win-amd64-3.10\lib\

:: zip contents of win build folder with todays date.
cd build\exe.win-amd64-3.10
"C:\Program Files\7-Zip\7z.exe" a -tzip UIXinator-%buildDate%.zip * -r -spf
move UIXinator-%buildDate%.zip ..
pause