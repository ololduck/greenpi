# GreenPi

This is a complete solution to monitor a desktop plant.

We get the following readings:

* temperature
* light level
* soil moisture

## Usage

This is a simple Raspberry Pi shield, which stacks on the raspberry's GPIOs.

Here is the schematic:

![GreenPi schematic](GreenPi_schematic.png)

## TODO

* get rid of xively, use some sqlite db instead, for instance. Provide a mini flask app to graph data.
* use a config file, instead of environment variables?

