set SCRIPT=..\sources\analyze.py
set FILE1="pcan1"
set FILE2="pcan2"
set FILE3="pcan3"
set FILE4="ixxat1"

py %SCRIPT% -s %FILE1%.trc
py %SCRIPT% -s %FILE2%.trc
py %SCRIPT% -s %FILE3%.trc
py %SCRIPT% -s %FILE4%.trc

timeout 4








