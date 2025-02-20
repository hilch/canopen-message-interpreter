# canopen-message-interpreter
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

Python script to interpret CAN traces as CANopen messages according to CiA DS301 / V4.2.0.

See [CiA group](https://can-cia.org/) for specification.

[Controller Area Network (CAN bus)](https://en.wikipedia.org/wiki/CAN_bus) is a vehicle bus standard designed 1983 by Robert Bosch GmbH.

[CANopen](https://en.wikipedia.org/wiki/CANopen) is a higher level communication protocol and device profile specification for embedded systems used in automation based on CAN.

There are many tools available to record CAN messages. Usually they provide simple text files. 

But for CANopen it would mean to translate all bytes manually since they usually do not provide higher level interpreters out of the box.

I did not found any free tools to interpret CANopen at all. And even (expensive) professional tools don't present all data (which I am interessted in).

So this (incomplete and non perfect) tool might help.

Currently supported file formats:
- PCAN- View 1.1
- PCAN- View 2.1
- IXXAT MiniMon V3
  

# Usage

```
usage: analyze.py [-h] -s SOURCE [-o OUTPUT]
( on Windows: py analyze.py [-h] -s SOURCE [-o OUTPUT] )


options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        trace file (*.*)
  -o OUTPUT, --output OUTPUT
                        output file (*.csv)
```
## --source

CAN trace file. 
(currently only [PCAN-View](https://www.peak-system.com/) *.trc is supported)

## --output

output file.
(currently only CSV with ';' as separator is supported).
If paramater is omitted the source file name with appended extension is taken.

## Example

```
py analyze.py -s sample1.trc -o sample1.csv 
```

if the script is started without arguments, an interactive dialog opens




