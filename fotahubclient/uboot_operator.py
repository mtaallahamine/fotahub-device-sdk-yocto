import subprocess

UBOOT_SETENV_TOOL = 'fw_setenv'
UBOOT_PRINTENV_TOOL = 'fw_printenv'

class UBootError(Exception):
    pass

class UBootOperator(object):

    def set_uboot_env_var(self, name, value=None):
        if value != None:
            self.logger.info("Setting U-Boot environment variable '{}' to '{}'".format(name, value))
        else:
            self.logger.info("Deleting U-Boot environment variable '{}'".format(name))

        try:
            cmd = [UBOOT_SETENV_TOOL, name]
            if value != None:
                cmd.append(value)
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as err:
            raise UBootError("Failed to change U-Boot environment variable '{}'".format(name)) from err

    def isset_uboot_env_var(self, name):
        self.logger.info("Checking if U-Boot environment variable '{}' is set".format(name))

        cmd = [UBOOT_PRINTENV_TOOL, '|', 'grep', name]
        process = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.stdout and not process.stderr

    def reboot(self):
        self.logger.info("Rebooting system to activate staged OS update")
        
        try:
            subprocess.run("reboot", check=True)
        except subprocess.CalledProcessError as err:
            raise OSError("Failed to reboot system") from err
