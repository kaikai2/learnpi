# Chip : Pi
# VCC = G2/G4 (5V)
# CLK = G23 (GPIO11 SPIO_SCLK)
# CE = G24 (GPIO8 SPIO_CE0_N)
# MOSI = G19 (GPIO10 SPIO_MOSI)
# GND = G6 (Ground)

import spidev
import time
spi=spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=500000
heart=[0x00,0x66,0xff,0xff,0xff,0x7e,0x3c,0x18]
def f():
    for i in range(8):
        spi.xfer([~heart[i], 0xff, 0xff, 1<<i])
        time.sleep(0.001)

for i in range(1000):
    f()
    
spi.xfer([0])
    
spi.close()
