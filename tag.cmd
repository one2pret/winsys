@echo off
if "%1" == "" goto error
if "%2" == "" goto error

svn copy %1\trunk %1\tags\%2
svn commit %1\tags\%2 -m "Tagged %1 for release %2"
chdir %1\tags
zip -r %1-%2.zip %2
chdir ..\..
move %1\tags\%1-%2.zip downloads
svn add downloads\%1-%2.zip
svn commit downloads\%1-%2.zip -m "Zipped release %2 of %1"

goto finish

:error
echo Usage:
echo   tag project version
echo   tag active_directory 7.1

:finish