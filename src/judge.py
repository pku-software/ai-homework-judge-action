from typing import Union
from cases import Case, MalformedCase
from dataclasses import dataclass
import os
import shutil
import urllib.request
import subprocess

@dataclass
class JudgeResult:
    title: str
    success: bool
    log: str


def prepare(path: str) -> JudgeResult:
    dirname = os.path.dirname(os.path.abspath(__file__))
    remotes = [
        ("https://github.com/pku-software/libai/raw/main/includes/rjsjai.h", "includes/real_rjsjai.h"),
        ("https://github.com/pku-software/ai_homework_template/raw/main/src/ai.h", "src/ai.h"),
        ("https://github.com/pku-software/ai_homework_template/raw/main/src/main.cpp", "src/main.cpp")
    ]
    for url, target in remotes:
        full_path = os.path.join(path, target)
        if not os.path.exists(full_path):
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            urllib.request.urlretrieve(url, full_path)
    
    copies = [
        ("rjsjai.h", "includes"),
        ("librjsjai.a", "lib"),
    ]
    for file, dir in copies:
        full_path = os.path.join(path, dir)
        os.makedirs(full_path, exist_ok=True)
        shutil.copy(os.path.join(dirname, "../dummy", file), full_path)
    
    return JudgeResult("prepare", True, "")

def build(path: str) -> JudgeResult:
    os.chdir(path)
    if os.path.exists("xmake.lua"):
        build_system = 0
    elif os.path.exists("CMakeLists.txt"):
        build_system = 1
    else:
        return JudgeResult("pre-configure", False, "No build system found.")
    
    config_commands = [
        "xmake f -y" + (" -pmingw" if os.name == "nt" else ""),
        "cmake -B ./build"
    ]
    cfg_r = subprocess.run(config_commands[build_system], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = cfg_r.stdout.decode(errors="ignore") + cfg_r.stderr.decode(errors="ignore")
    if cfg_r.returncode != 0:
        return JudgeResult("configure", False, output)

    build_commands = [
        "xmake b -y",
        "cmake --build ./build"
    ]
    build_r = subprocess.run(build_commands[build_system], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output += build_r.stdout.decode(errors="ignore") + build_r.stderr.decode(errors="ignore")
    if build_r.returncode != 0:
        return JudgeResult("build", False, output)
    
    return JudgeResult("build", True, output)

def test(path: str, case: Union[Case, MalformedCase]) -> JudgeResult:
    if isinstance(case, MalformedCase):
        pass
    else:
        pass
    return JudgeResult("test", False, "Not implemented yet.")