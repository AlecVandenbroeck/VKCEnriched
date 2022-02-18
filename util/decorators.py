from time import time


class TimeLogger:
    time_logs = dict()

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        identifier = f"{self.function.__qualname__}"
        # We can add some code
        # before function call
        start_time = time()
        res = self.function(*args, **kwargs)
        # We can also add some code
        # after function call.
        end_time = time()
        if identifier in self.time_logs.keys():
            self.time_logs[identifier] += end_time - start_time
        else:
            self.time_logs[identifier] = end_time - start_time
        return res

    @classmethod
    def reset(cls):
        cls.time_logs = dict()

    @classmethod
    def print_time_logs(cls):
        total_time = 0
        for i in cls.time_logs:
            total_time += cls.time_logs[i]
        for i in cls.time_logs:
            print(f"{i}: {cls.time_logs[i]:.2f} ({(cls.time_logs[i] / total_time * 100):.2f}%)")
