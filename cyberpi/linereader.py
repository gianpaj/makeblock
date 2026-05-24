# Byte-stream -> newline-delimited line framer.
# Pure logic; no UART import. Feed it bytes; it yields complete lines.
# Drops over-long lines via the supplied `on_overflow` callback.


class LineReader:
    def __init__(self, max_len=512, on_overflow=None):
        self._buf = bytearray()
        self._max = max_len
        self._on_overflow = on_overflow

    def feed(self, chunk):
        # Generator: yields one bytes() per completed line.
        for b in chunk:
            if b == 0x0A:  # \n
                if self._buf:
                    line = bytes(self._buf)
                    self._buf = bytearray()
                    yield line
            elif b == 0x0D:  # \r — ignore
                continue
            else:
                if len(self._buf) >= self._max:
                    self._buf = bytearray()
                    if self._on_overflow is not None:
                        self._on_overflow()
                else:
                    self._buf.append(b)
