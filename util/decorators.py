from time import time
from functools import update_wrapper, partial


class TimeLogger:
    time_logs = dict()

    def __init__(self, function):
        self.function = function
        update_wrapper(self, function)

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)

    def __call__(self, obj, *args, **kwargs):
        identifier = f"{self.function.__qualname__}"
        # We can add some code
        # before function call
        start_time = time()
        res = self.function(obj, *args, **kwargs)
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
            time_hours = int(cls.time_logs[i]//3600)
            time_rem = cls.time_logs[i] % 3600
            time_mins = int(time_rem//60)
            time_secs = time_rem % 60
            if time_hours != 0:
                print(f"{i}: {time_hours}h{time_mins}m{time_secs:.2f}s ({(cls.time_logs[i] / total_time * 100):.2f}%)")
            elif time_mins != 0:
                print(f"{i}: {time_mins}m{time_secs:.2f}s ({(cls.time_logs[i] / total_time * 100):.2f}%)")
            else:
                print(f"{i}: {time_secs:.2f}s ({(cls.time_logs[i] / total_time * 100):.2f}%)")
        total_time_hours = int(total_time // 3600)
        total_time_rem = total_time % 3600
        total_time_mins = int(total_time_rem // 60)
        total_time_secs = total_time_rem % 60
        if total_time_hours != 0:
            print(f"Total time: {total_time_hours}h{total_time_mins}m{total_time_secs:.2f}s")
        elif total_time_mins != 0:
            print(f"Total time: {total_time_mins}m{total_time_secs:.2f}s")
        else:
            print(f"Total time: {total_time_secs:.2f}s")
