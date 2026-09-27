"""The sandbox-compatible installed FreeCAD runtime, isolated from desktop settings."""
import os
from pathlib import Path
import sys


def environment(out):
    runtime = Path(os.environ.get("MARKVIII_FREECAD_ROOT", "/snap/freecad/current")).resolve()
    qt = Path(os.environ.get("MARKVIII_QT_ROOT", "/snap/kf6-core24/current")).resolve()
    if not (runtime / "usr/lib/FreeCAD.so").is_file():
        raise ValueError("Installed FreeCAD Python library is missing")
    if not (qt / "usr/lib/x86_64-linux-gnu/libQt6Core.so.6").exists():
        raise ValueError("Installed matching Qt runtime is missing")
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = ":".join(str(p) for p in [
        runtime / "usr/lib", runtime / "usr/lib/x86_64-linux-gnu",
        qt / "usr/lib/x86_64-linux-gnu", qt / "usr/lib"])
    env["PYTHONPATH"] = ":".join(str(p) for p in [runtime / "usr/lib", runtime / "usr/lib/python3/dist-packages"])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["QT_PLUGIN_PATH"] = str(qt / "usr/lib/x86_64-linux-gnu/qt6/plugins")
    for key, name in [("FREECAD_USER_HOME", "user"), ("XDG_CACHE_HOME", "cache"),
                      ("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data")]:
        path = out / "runtime" / name
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    env["MARKVIII_RESOLVED_FREECAD"] = str(runtime)
    return env


def start_gui():
    import FreeCAD as App
    import FreeCADGui as Gui
    if App.Version()[:3] != ["1", "1", "1"]:
        raise ValueError("FreeCAD runtime changed; requalify the tested 1.1.1 installation")
    pref = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    pref.SetBool("SaveThumbnail", False)
    pref.SetInt("CountBackupFiles", 0)
    Gui.showMainWindow()
    Gui.getMainWindow().hide()
    return App, Gui


def close():
    if "FreeCAD" not in sys.modules:
        return
    App = sys.modules["FreeCAD"]
    for name in list(App.listDocuments()):
        App.closeDocument(name)
    if App.GuiUp:
        import FreeCADGui as Gui
        from PySide6 import QtCore, QtWidgets
        QtWidgets.QApplication.processEvents()
        Gui.getMainWindow().deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
