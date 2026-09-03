set SCRIPT=..\sources\analyze.py
set FILE1="pcan1"
set FILE2="pcan2"
set FILE3="pcan3"
set FILE4="pcan4"
set FILE5="ixxat1"

python %SCRIPT% -s %FILE1%.trc
python %SCRIPT% -s %FILE2%.trc
python %SCRIPT% -s %FILE3%.trc
python %SCRIPT% -s %FILE4%.trc
python %SCRIPT% -s %FILE5%.trc

timeout 4








