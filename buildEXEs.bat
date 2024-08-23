:: Clean up build folder.
:: This may be redundant, think cx_Freeze can do this on its own. but this is "more reliable"
@RD /S /Q "build"
:: Then make a new build
python build-Iconinator.py build

:: Copy XBEJson, This extra exe will be removed soonTM
@xcopy XBEJson.exe build\exe.win-amd64-3.10\

:: zip contents of win build folder with todays date.
cd build\exe.win-amd64-3.10
"C:\Program Files\7-Zip\7z.exe" a -tzip UIXinator-20240823.zip * -r -spf
move UIXinator-20240823.zip ..
pause