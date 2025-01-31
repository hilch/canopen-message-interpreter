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
from modules.cantraces import PCANViewTrace, IXXATTrace

                   
                         
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help = "trace file (*.*)", required= True )
    parser.add_argument("-o", "--output", help = "output file (*.csv)")
    parser.add_argument('-f', "--format", choices = ['pcan', 'ixxat'], help = "trace format type ('pcan')", required= True )
    try:
        args = parser.parse_args()
        if args.source:
            if args.format == 'pcan':
                trace = PCANViewTrace( args.source )         
            elif args.format == 'ixxat':
                trace = IXXATTrace( args.source )                         
                
            if args.output:
                trace.toCSV( args.output )
             
    except argparse.ArgumentError:
        print("wrong or missing arguments")
    except SystemExit:
        pass
