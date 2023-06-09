set SCRIPT=..\sources\analyze.py
set FILE1="pcan1"
set FILE2="pcan2"


py %SCRIPT% -s %FILE1%.trc -o %FILE1%.csv -f pcan
py %SCRIPT% -s %FILE2%.trc -o %FILE2%.csv -f pcan

timeout 10






