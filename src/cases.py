from dataclasses import dataclass, KW_ONLY
from enum import IntEnum
from typing import Union, List
import random


class AiType(IntEnum):
    CHAT = 2
    DRAW = 3
    WOLFRAM = 4


def type_switch_name(type: AiType) -> str:
    return {
        AiType.CHAT: "--chat",
        AiType.DRAW: "--draw",
        AiType.WOLFRAM: "--math"
    }[type]


def type_enable_term_output(type: AiType) -> bool:
    return type == AiType.CHAT


@dataclass
class Case:
    type: AiType
    prompt: str
    output: Union[None, str]
    short_output_switch: bool = False
    _: KW_ONLY
    error: bool = False

    def generate_args(self) -> List[str]:
        args = [type_switch_name(self.type), self.prompt]
        if self.output is not None:
            output_args = [
                "-o" if self.short_output_switch else "--output",
                self.output
            ]
            if random.random() < 0.5:
                args = output_args + args
            else:
                args += output_args
        return args

    def should_error(self) -> bool:
        if self.error:
            return True
        if not type_enable_term_output(self.type) and self.output is None:
            return True
        return False


@dataclass
class MalformedCase:
    args: List[str]


def get_cases() -> List[Union[Case, MalformedCase]]:
    return [
        Case(AiType.CHAT, "c1", None, False),
        Case(AiType.CHAT, "c2", "chat_output2.txt", False),
        Case(AiType.CHAT, "c3", None, True),
        Case(AiType.CHAT, "c4", "chat_output4.txt", True),

        Case(AiType.CHAT, "c1e", None, False, error=True),
        Case(AiType.CHAT, "c2e", "chat_output2e.txt", False, error=True),
        Case(AiType.CHAT, "c3e", None, True, error=True),
        Case(AiType.CHAT, "c4e", "chat_output4e.txt", True, error=True),

        Case(AiType.DRAW, "d1", None, False),
        Case(AiType.DRAW, "d2", "draw_output2.bmp", False),
        Case(AiType.DRAW, "d3", None, True),
        Case(AiType.DRAW, "d4", "draw_output4.bmp", True),

        Case(AiType.DRAW, "d1e", None, False, error=True),
        Case(AiType.DRAW, "d2e", "draw_output2e.bmp", False, error=True),
        Case(AiType.DRAW, "d3e", None, True, error=True),
        Case(AiType.DRAW, "d4e", "draw_output4e.bmp", True, error=True),

        Case(AiType.WOLFRAM, "m1", None, False),
        Case(AiType.WOLFRAM, "m2", "math_output2.bmp", False),
        Case(AiType.WOLFRAM, "m3", None, True),
        Case(AiType.WOLFRAM, "m4", "math_output4.bmp", True),

        Case(AiType.WOLFRAM, "m1e", None, False, error=True),
        Case(AiType.WOLFRAM, "m2e", "math_output2e.bmp", False, error=True),
        Case(AiType.WOLFRAM, "m3e", None, True, error=True),
        Case(AiType.WOLFRAM, "m4e", "math_output4e.bmp", True, error=True),

        MalformedCase([]),
        MalformedCase(["--unrecognized"]),
        MalformedCase(["--output"]),
        MalformedCase(["--chat"]),
        MalformedCase(["--chat", "--unrecognized"]),
        MalformedCase(["--chat", "p", "--unrecognized"]),
        MalformedCase(["--chat", "no_filename", "-o"]),
        MalformedCase(["--chat", "no_filename", "--output"]),
        MalformedCase(["--output", "no_type.txt"]),
        MalformedCase(["-o", "no_type.txt"]),
        MalformedCase(["--chat", "multiple", "arguments"]),
        MalformedCase(["--chat", "multiple", "--draw", "type"]),
        MalformedCase(["--chat", "--draw", "multiple_type"]),
        MalformedCase(["--chat", "--chat", "duplicate_type"]),
    ]
