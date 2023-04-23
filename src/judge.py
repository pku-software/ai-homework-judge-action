from typing import Union, List, Tuple
from cases import Case, MalformedCase
from dataclasses import dataclass
import os
import shutil
import urllib.request
import subprocess
import json


@dataclass
class JudgeResult:
    title: str
    success: bool
    log: str


def prepare(path: str) -> JudgeResult:
    dirname = os.path.dirname(os.path.abspath(__file__))
    remotes = [
        ("https://github.com/pku-software/libai/raw/main/includes/rjsjai.h",
         "includes/real_rjsjai.h"),
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
        "cmake -B ./build" + (" -G \"MinGW Makefiles\"" if os.name == "nt" else "")
    ]
    cfg_r = subprocess.run(
        config_commands[build_system], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = cfg_r.stdout.decode(errors="ignore") + \
        cfg_r.stderr.decode(errors="ignore")
    if cfg_r.returncode != 0:
        return JudgeResult("configure", False, output)

    build_commands = [
        "xmake b -y",
        "cmake --build ./build"
    ]
    build_r = subprocess.run(
        build_commands[build_system], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output += build_r.stdout.decode(errors="ignore") + \
        build_r.stderr.decode(errors="ignore")
    if build_r.returncode != 0:
        return JudgeResult("build", False, output)

    return JudgeResult("build", True, output)


def run_exe(path: str, args: List[str], error: bool = False) -> Tuple[str, int, str]:
    args = [path] + args
    env = {
        "DUMMY_RJSJAI_EXPECT_ERROR": "1"
    } if error else {}
    env.update(os.environ)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate()
    exit_code = proc.returncode
    stdout = stdout.decode(errors="ignore")
    stderr = stderr.decode(errors="ignore")
    return stdout, exit_code, ' '.join(args) + '\n' + stdout + '\n' + stderr


def test(path: str, case: Union[Case, MalformedCase]) -> JudgeResult:
    os.chdir(path)
    exe_path = os.path.join(
        path, "bin", "hw7.exe" if os.name == "nt" else "hw7")
    if not os.path.exists(exe_path):
        return JudgeResult("pretest", False, "Output executable file hw7 does not exist.")
    if isinstance(case, MalformedCase):
        _, code, log = run_exe(exe_path, case.args)
        if code == 0:
            return JudgeResult("test", False, "Malformed case should not pass. Output:\n" + log)
        else:
            return JudgeResult("test", True, "Failed as expected. Output:\n" + log)
    args = case.generate_args()
    output, code, log = run_exe(exe_path, args, error=case.error)
    if case.should_error():
        if code == 0:
            return JudgeResult("test", False, "Case should error but passed. Output:\n" + log)
        elif case.output is not None and os.path.exists(case.output):
            return JudgeResult("test", False, "Case should error, but output file created. Output:\n" + log)
        else:
            return JudgeResult("test", True, "Failed as expected. Output:\n" + log)
    if case.output is not None:
        if not os.path.exists(case.output):
            return JudgeResult("test", False, "Output file does not exist.\nOutput:\n" + log)
        with open(case.output, "r", encoding="utf-8") as f:
            output = f.read()
    try:
        result = json.loads(output)
    except Exception:
        return JudgeResult("test", False, "Failed to parse output as JSON.\nOutput:\n" + log)
    if result["prompt"] != case.prompt:
        return JudgeResult("test", False, f"Prompt mismatch. Expected: {case.prompt}, got: {result['prompt']}.\nOutput:\n{log}")
    if result["status"] != 0:
        return JudgeResult("test", False, f"AI should be success status, got: {result['status']}.\nOutput:\n{log}")
    if result["type"] != int(case.type):
        return JudgeResult("test", False, f"AI Type mismatch. Expected: {case.type}, got: {result['type']}.\nOutput:\n{log}")
    if code != 0:
        return JudgeResult("test", False, f"Program unexpectedly exited with code {code}.\nOutput:\n{log}")
    return JudgeResult("test", True, log)
