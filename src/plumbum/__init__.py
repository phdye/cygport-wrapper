# Minimal shim for tests without the external plumbum dependency
from cygport.vendor.miniplumbum import local, BG, RETCODE

class FG(RETCODE):
    """Foreground execution modifier (simplified)."""
    def __rand__(self, cmd):
        cmd.run()
        return cmd
