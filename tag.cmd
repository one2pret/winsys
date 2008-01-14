@echo off
if "%1" == "" goto error
if "%2" == "" goto error

svn copy %1\trunk %1\tags\%2
svn commit %1\tags\%2 -m "Tagged for release %2"
chdir %1\tags
zip -r %1-%2.zip %2
pscp %1-%2.zip tgolden@scandium:web/timgolden.me.uk/python/downloads
del %1-%2.zip
chdir ..\..

goto finish

:error
echo Usage:
echo   tag project version
echo   tag active_directory 7.1

:finish