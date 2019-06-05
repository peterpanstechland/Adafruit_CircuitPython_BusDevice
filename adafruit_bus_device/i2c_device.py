__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BusDevice.git"

class I2CDevice:

    def __init__(self, i2c, device_address, *, debug=False):
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto(device_address, b'')
        except OSError:
            # some OS's dont like writing an empty bytesting...
            # Retry by reading a byte
            try:
                result = bytearray(1)
                i2c.readfrom_into(device_address, result)
            except OSError:
                raise ValueError("No I2C device at address: %x" % device_address)
        finally:
            i2c.unlock()

        self.i2c = i2c
        self.device_address = device_address
        self._debug = debug

    def readinto(self, buf, **kwargs):
        self.i2c.readfrom_into(self.device_address, buf, **kwargs)
        if self._debug:
            print("i2c_device.readinto:", [hex(i) for i in buf])

    def write(self, buf, **kwargs):
        self.i2c.writeto(self.device_address, buf, **kwargs)
        if self._debug:
            print("i2c_device.write:", [hex(i) for i in buf])

    def write_then_readinto(self, out_buffer, in_buffer, *,
                            out_start=0, out_end=None, in_start=0, in_end=None, stop=True):
        if out_end is None:
            out_end = len(out_buffer)
        if in_end is None:
            in_end = len(in_buffer)
        if hasattr(self.i2c, 'writeto_then_readfrom'):
            if self._debug:
                print("i2c_device.writeto_then_readfrom.out_buffer:",
                      [hex(i) for i in out_buffer[out_start:out_end]])
            self.i2c.writeto_then_readfrom(self.device_address, out_buffer, in_buffer,
                                           out_start=out_start, out_end=out_end,
                                           in_start=in_start, in_end=in_end, stop=stop)
            if self._debug:
                print("i2c_device.writeto_then_readfrom.in_buffer:",
                      [hex(i) for i in in_buffer[in_start:in_end]])
        else:
            self.write(out_buffer, start=out_start, end=out_end, stop=stop)
            if self._debug:
                print("i2c_device.write_then_readinto.write.out_buffer:",
                      [hex(i) for i in out_buffer[out_start:out_end]])
            self.readinto(in_buffer, start=in_start, end=in_end)
            if self._debug:
                print("i2c_device.write_then_readinto.readinto.in_buffer:",
                      [hex(i) for i in in_buffer[in_start:in_end]])

    def __enter__(self):
        while not self.i2c.try_lock():
            pass
        return self

    def __exit__(self, *exc):
        self.i2c.unlock()
        return False
