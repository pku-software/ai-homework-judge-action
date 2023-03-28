from typing import Callable, List
import abc
from judge import JudgeResult

class ILogger(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exec_func(self, func: Callable[[str], JudgeResult], ws_path: str) -> bool:
        pass

    @abc.abstractmethod
    def end(self) -> None:
        pass

def wrap_exception(func: Callable[[str], JudgeResult]):
    def wrapped(path: str):
        try:
            return func(path)
        except Exception as e:
            return JudgeResult(func.__name__, False, str(e))
    return wrapped

class TermLogger(ILogger):
    def __init__(self) -> None:
        pass

    def exec_func(self, func: Callable[[str], JudgeResult], ws_path: str) -> bool:
        result = wrap_exception(func)(ws_path)
        if result.success:
            print(result.title, "\033[1;32m", "OK", "\033[0m")
        else:
            print(result.title, "\033[1;31m", "Failed", "\033[0m")
            print(result.log)
        return result.success

    def end(self) -> None:
        
        pass

class JsonLogger(ILogger):
    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        self.results: List[JudgeResult] = []
        pass

    def exec_func(self, func: Callable[[str], JudgeResult], ws_path: str) -> bool:
        result = wrap_exception(func)(ws_path)
        self.results.append(result)
        return result.success

    def end(self) -> None:
        pass