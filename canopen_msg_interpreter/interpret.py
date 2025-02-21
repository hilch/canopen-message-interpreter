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
from canopen_msg_interpreter.cantraces import PCANViewTrace
from pathlib import Path
import os


def analyze(
    source_file,
    eds_file=None,
    outfile=None,
    source_format="pcan",
):
    if source_format == "pcan":
        trace = PCANViewTrace(source_file, eds_file)

    out = outfile
    if out is None:
        out = (
            Path(os.getcwd())
            / Path(source_file).parent
            / Path(Path(source_file).stem + ".csv")
        )
    print(f"Output CANopen CSV analysis to: {out}")

    trace.toCSV(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="trace file (*.*)", required=True)
    parser.add_argument(
        "-o", "--output", help="output file (*.csv)", required=False, default=None
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["pcan"],
        help="trace format type ('pcan')",
        default="pcan",
    )
    parser.add_argument(
        "-e",
        "--eds",
        required=False,
        help="EDS file to better interpret SDO messages",
        default=None,
    )
    args = parser.parse_args()
    analyze(args.source, args.eds, args.output, args.format)
