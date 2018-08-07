import shutil
import os
import sublime
import sublime_plugin
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig

default_name = 'dotty'

coursier_command = 'coursier'
if os.name == 'nt':
    coursier_command = 'coursier.bat'

coursier_path = os.path.join(os.path.dirname(__file__), coursier_command)

server_pkg_name = 'dotty-language-server'
artifact = "ch.epfl.lamp:dotty-language-server_0.7:0.7.0-RC1"
classPath = artifact

fetch_command = ["java", "-jar", coursier_path, "fetch", "-p", artifact]

launch_command = [
    coursier_path, "launch",
    artifact, "-M",
    "dotty.tools.languageserver.Main", "--", "-stdio"
]

run_command = [
    "java", "-classpath", classPath, "dotty.tools.languageserver.Main",
    "-stdio"
]

default_config = ClientConfig(
    name=default_name,
    binary_args=launch_command,
    tcp_port=None,
    scopes=["source.scala"],
    syntaxes=["Packages/Scala/Scala.sublime-syntax"],
    languageId='scala',
    enabled=False,
    init_options=dict(),
    settings=dict(),
    env=dict())


def java_is_installed() -> bool:
    return shutil.which("java") is not None


def sbt_is_installed() -> bool:
    return shutil.which("sbt") is not None


def has_dotty_ide_file(window) -> bool:
    if len(window.folders()) < 1:
        return False
    path = window.folders()[0]
    return os.path.exists(os.path.join(path, ".dotty-ide.json"))


class LspDottySetupCommand(sublime_plugin.WindowCommand):
    def run(self):
        if not java_is_installed():
            sublime.message_dialog(
                "Please install the JDK before running setup")
        elif not sbt_is_installed():
            sublime.message_dialog("Please install SBT before running setup")
        # elif not server_is_installed():
        else:
            if sublime.ok_cancel_dialog(
                "{} was not available\n Install now?".format(
                        server_pkg_name)):
                self.window.run_command(
                    "exec", {
                        "cmd": fetch_command,
                    })


class LspDottyPlugin(LanguageHandler):
    def __init__(self):
        self._name = default_name
        self._config = default_config

    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not java_is_installed():
            window.status_message(
                "The JDK must be installed to run {}".format(server_pkg_name))
            return False
        if not sbt_is_installed():
            window.status_message(
                "SBT must be installed to run {}".format(server_pkg_name))
            return False

        if not has_dotty_ide_file(window):
            window.status_message(
                "A dotty project file must be generated before starting {}"
                .format(server_pkg_name))
            return False

        return True

    def on_initialized(self, client) -> None:
        pass  # extra initialization here.
