import time

# Ported from https://github.com/dirigeants/klasa/blob/master/src/lib/util/Stopwatch.js
class Stopwatch:
    def __init__(self, digits = 2):

        # digits is useless right now since i couldn't find a way to embed this
        # into a :.f expression, so it is always 2 anyway for now
        self.digits = digits
        self._start = time.perf_counter()
        self._end = None

    @property
    def duration(self):
        return self._end - self._start if self._end else time.perf_counter() - self._start

    @property
    def running(self):
        return not self._end

    def restart(self):
        self._start = time.perf_counter()
        self._end = None
        return self

    def reset(self):
        self._start = time.perf_counter()
        self._end = self._start
        return self

    def start(self):
        if not self.running:
            self._start = time.perf_counter() - self.duration
            self._end = None
        return self

    def stop(self):
        if self.running:
            self._end = time.perf_counter()
        return self

    def __str__(self):
        time = self.duration
        if time >= 1000:
            return f"{(time / 1000):.2f}s"
        if time >= 1:
            return f"{time:.2f}ms"
        return f"{(time * 1000):.2f}μs"
