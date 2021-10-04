# README

To control Thorlabs APT motors, we are wrapping the pyAPT software from https://github.com/freespace/pyAPT. If on linux, install the `libftdi1` package to enable the correct serial communication. The Zaber motor control uses the older zaber.serial module and pySerial. In a future update we will move to the newer API that zaber has released.