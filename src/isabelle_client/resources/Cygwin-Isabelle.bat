@echo off

set TEMP_WINDOWS=%TEMP%
set HOME=%HOMEDRIVE%%HOMEPATH%
set PATH=%ISABELLE_INST_DIR%\bin;%PATH%
set LANG=en_US.UTF-8
set CHERE_INVOKING=true
set arg1=%1
set unquoted_arg1=%arg1:"=%

"%ISABELLE_INST_DIR%\contrib\cygwin\bin\bash" --login -i ^
    -c "isabelle %unquoted_arg1%"