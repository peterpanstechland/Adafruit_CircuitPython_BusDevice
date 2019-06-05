__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BusDevice.git"

class SPIDevice:
    def __init__(self, spi, chip_select=None, *,
                 baudrate=100000, polarity=0, phase=0, extra_clocks=0):
        self.spi = spi
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.extra_clocks = extra_clocks
        self.chip_select = chip_select
        if self.chip_select:
            self.chip_select.switch_to_output(value=True)

    def __enter__(self):
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=self.baudrate, polarity=self.polarity,
                           phase=self.phase)
        if self.chip_select:
            self.chip_select.value = False
        return self.spi

    def __exit__(self, *exc):
        if self.chip_select:
            self.chip_select.value = True
        if self.extra_clocks > 0:
            buf = bytearray(1)
            buf[0] = 0xff
            clocks = self.extra_clocks // 8
            if self.extra_clocks % 8 != 0:
                clocks += 1
            for _ in range(clocks):
                self.spi.write(buf)
        self.spi.unlock()
        return False
