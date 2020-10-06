"""
JupyterQtWidget is the widget that gets embedded in Excel and hosts
a tabbed browser widget containing the Jupyter notebook.
"""
from .kernel import start_kernel, launch_jupyter
from .browser import Browser
from .qtimports import QWidget, QVBoxLayout
import win32gui, win32ui
import subprocess


class JupyterQtWidget(QWidget):

    def __init__(self, parent=None, scale=None, initial_path=None):
        super().__init__(parent)

        # proc gets set to the subprocess when the jupyter is started
        self.proc = None

        # Get the scale from the window DPI
        if scale is None:
            LOGPIXELSX = 88
            hwnd = self.winId()
            if isinstance(hwnd, str):
                hwnd = int(hwnd, 16 if hwnd.startswith("0x") else 10)
            screen = win32gui.GetDC(hwnd)
            try:
                scale = win32ui.GetDeviceCaps(screen, LOGPIXELSX) / 96.0
            finally:
                win32gui.ReleaseDC(hwnd, screen)

        # Create the browser widget
        self.browser = Browser(self, scale=scale)
        self.browser.closed.connect(self.close)

        # Add the browser to the widgets layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)

        # Start the kernel and open Jupyter in a new tab
        app = start_kernel()
        self.proc, url = launch_jupyter(app.connection_file, cwd=initial_path)
        self.browser.create_tab(url)

    def closeEvent(self, event):
        # Kill the Jupyter subprocess using taskkill (just killing the process using POpen.kill
        # doesn't terminate any child processes)
        if self.proc is not None:
            while self.proc.poll() is None:
                si = subprocess.STARTUPINFO(wShowWindow=subprocess.SW_HIDE)
                subprocess.check_call(['taskkill', '/F', '/T', '/PID', str(self.proc.pid)],
                                      startupinfo=si,
                                      shell=True)
