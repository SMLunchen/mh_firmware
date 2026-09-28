#!/usr/bin/env python3
# trunk-ignore-all(ruff/F821)
# trunk-ignore-all(flake8/F821): For SConstruct imports
import glob
import os
from os.path import exists, join

Import("env")

# ---------------------------------------------------------------------------
# The pioarduino custom-sdkconfig libs cache (framework-arduinoespressif32-libs/
# <mcu>_<suffix>) is shared machine-wide, but the rebuild-needed check only
# compares against THIS project's sdkconfig marker files. Any other project
# rebuilding the shared folder silently drops our settings (DSI ISR flags,
# SDIO pins) and the next build here links against them: display flicker,
# artifacts, broken co-processor transport.
#
# Detect a foreign rebuild via a sentinel this env always sets and, if it is
# missing, delete the project marker files so pioarduino rebuilds the libs
# with the correct configuration in this run.
# ---------------------------------------------------------------------------

SENTINEL = "CONFIG_LCD_DSI_ISR_CACHE_SAFE"


def libs_sdkconfig_headers():
    libs_dir = env.PioPlatform().get_package_dir("framework-arduinoespressif32-libs")
    mcu = env.BoardConfig().get("build.mcu", "")
    if not libs_dir or not mcu:
        return []
    headers = []
    for d in glob.glob(join(libs_dir, mcu + "_*")):
        for flavor in ("qio_qspi", "dio_qspi"):
            p = join(d, flavor, "include", "sdkconfig.h")
            if exists(p):
                headers.append(p)
    return headers


headers = libs_sdkconfig_headers()
if headers and not any(SENTINEL in open(p).read() for p in headers):
    print("*** shared IDF libs cache was rebuilt by another project -> forcing rebuild ***")
    for name in ("sdkconfig.defaults", "sdkconfig." + env["PIOENV"]):
        path = join(env.subst("$PROJECT_DIR"), name)
        if exists(path):
            os.remove(path)
