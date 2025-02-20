#!/usr/bin/python3
# This file is part of https://github.com/hilch/canopen-message-interpreter.
#
#    canopen-message-interpreter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    canopen-message-interpreter is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with canopen-message-interpreter.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import sys
from modules.cantraces import OpenTraceFile
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

initial_directory = str(Path.home())

def show_interactive_window():

    def open_file_dialog():
        global initial_directory
        file_paths = filedialog.askopenfilenames(f=[
            ('PCAN Trace files','.trc'),
            ('IXXAT Trace files','.csv'),
            ('any extension','.*')            
            ], 
            initialdir=initial_directory
        )
        if file_paths:
            initial_directory = str(Path(file_paths[0]).parent)
            for f in file_paths:
                trace = OpenTraceFile( f ) 
                trace.toCSV( f + '.csv' )

    # Create the main window
    root = tk.Tk()
    root.geometry("320x300")
    root.title("analyze CANopen traces")

    # label for help message
    label = tk.Label(root, text=\
    """    usage: 
        analyze.py [-h] [-s SOURCE] [-o OUTPUT]

    options:
        -h, --help  show this help message and exit
        -s SOURCE, --source SOURCE 
            trace file (*.*)
        -o OUTPUT, --output OUTPUT 
            output file (*.csv)

    example: 
        analyze.py -s trace1.trc
               
        """, justify= tk.LEFT)
    label.pack(pady=10)

     # Create a button to open file dialog
    file_button = tk.Button(root, text="Open SourceFile(s)", command=open_file_dialog)
    file_button.pack(pady=10)

    root.mainloop()
                   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help = "trace file (*.*)" )
    parser.add_argument("-o", "--output", help = "output file (*.csv)")


    args = parser.parse_args()

    if len(sys.argv) == 1: # no arguments were given
        show_interactive_window()

    if args.source:
        trace = OpenTraceFile( args.source )                
        if trace:
            if args.output:
                trace.toCSV( args.output )
            else:
                trace.toCSV( args.source + '.csv' )
             

