"""Utilities to get a password and/or the current user name.

getpass(prompt[, stream]) - Prompt for a password, with echo turned off.
getpass_asterisk(prompt[, stream]) - Prompt for a password, with masked output.
getuser() - Get the user name from the environment or password database.

GetPassWarning - This UserWarning is issued when getpass() cannot prevent
                 echoing of the password contents while reading.

On Windows, the msvcrt module will be used.
On the Mac EasyDialogs.AskPassword is used, if available.

<<<>>>
IMPORTANT SECURITY NOTE:
This module has been modified to add getpass_asterisk, which can
echo asterisks in place of password. Echoing of masked password leaks
the length of the password.
Use this utility only in a scenario where passwords are always of fixed length.
This utility was created to receive secret tokens as input which are always of
same size. Echoing the asterisks helped improve user experience.
Use at your own risk. Only use for taking constant length secret inputs.
For feedback, contact: Muhammad Akbar (akbarATsecursive.com)
<<<>>>


"""

# Authors: Piers Lauder (original)
#          Guido van Rossum (Windows support and cleanup)
#          Gregory P. Smith (tty support & GetPassWarning)
#          Muhammad Akbar (modified to allow masked echo)

import os, sys, warnings

__all__ = ["getpass", "getpass_asterisk", "getuser","GetPassWarning"]

class GetPassWarning(UserWarning): pass

def getpass_asterisk(prompt='Password: ', stream=None):
    return getpass(prompt=prompt, stream=stream, mask=True)

def unix_getpass(prompt='Password: ', stream=None, mask=False):
    """Prompt for a password, with echo turned off.

    Args:
      prompt: Written on stream to ask for the input.  Default: 'Password: '
      stream: A writable file object to display the prompt.  Defaults to
              the tty.  If no tty is available defaults to sys.stderr.
    Returns:
      The seKr3t input.
    Raises:
      EOFError: If our input tty or stdin was closed.
      GetPassWarning: When we were unable to turn echo off on the input.

    Always restores terminal settings before returning.
    """
    fd = None
    tty = None
    if mask:
        try:
            fd = sys.stdin.fileno()
        except (AttributeError, ValueError):
            passwd = fallback_getpass(prompt, stream)
        input = sys.stdin
        if not stream:
            stream = sys.stderr
    else:
        try:
            # Always try reading and writing directly on the tty first.
            fd = os.open('/dev/tty', os.O_RDWR|os.O_NOCTTY)
            tty = os.fdopen(fd, 'w+', 1)
            input = tty
            if not stream:
                stream = tty
        except EnvironmentError as e:
            # If that fails, see if stdin can be controlled.
            try:
                fd = sys.stdin.fileno()
            except (AttributeError, ValueError):
                passwd = fallback_getpass(prompt, stream)
            input = sys.stdin
            if not stream:
                stream = sys.stderr

    if fd is not None:
        passwd = None
        try:
            old = termios.tcgetattr(fd)     # a copy to save
            new = old[:]
            new[3] &= ~(termios.ECHO)  # 3 == 'lflags'. Stop echo.
            new[6][termios.VMIN] = 1 # Force return after each character
            new[6][termios.VTIME] = 0 # with no delay
            new[3] = new[3] & ~termios.ICANON # Kill canonical (line by line) mode
            tcsetattr_flags = termios.TCSAFLUSH
            if hasattr(termios, 'TCSASOFT'):
                tcsetattr_flags |= termios.TCSASOFT
            try:
                termios.tcsetattr(fd, tcsetattr_flags, new)
                passwd = _raw_input(prompt, stream, input=input, mask=mask)
            finally:
                termios.tcsetattr(fd, tcsetattr_flags, old)
                stream.flush()  # issue7208
        except termios.error as e:
            if passwd is not None:
                # _raw_input succeeded.  The final tcsetattr failed.  Reraise
                # instead of leaving the terminal in an unknown state.
                raise
            # We can't control the tty or stdin.  Give up and use normal IO.
            # fallback_getpass() raises an appropriate warning.
            if tty:
                del tty  # clean up unused file objects before blocking
            passwd = fallback_getpass(prompt, stream)

    stream.write('\n')
    return passwd


def win_getpass(prompt='Password: ', stream=None, mask=False):
    """Prompt for password with echo off, using Windows getch()."""
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    import msvcrt
    for c in prompt:
        msvcrt.putwch(c)
    pw = ""
    total_chars = 0
    while 1:
        c = msvcrt.getwch()
        if c == '\r' or c == '\n':
            break
        if c == '\003':
            raise KeyboardInterrupt
        if c == '\b' or ord(c) == 127:
            if total_chars > 0:
                pw = pw[:-1]
                total_chars -= 1
                if mask:
                    msvcrt.putwch('\b')
                    msvcrt.putwch(' ')
                    msvcrt.putwch('\b')
        else:
            pw = pw + c
            total_chars += 1
            if mask:
                msvcrt.putwch('*')
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    return pw


def fallback_getpass(prompt='Password: ', stream=None, mask=False):
    warnings.warn("Can not control echo on the terminal.", GetPassWarning,
                  stacklevel=2)
    if not stream:
        stream = sys.stderr
    print("Warning: Password input may be echoed.", file=stream)
    return _raw_input(prompt, stream, mask=False)


def _raw_input(prompt="", stream=None, input=None, mask=False):
    # A raw_input() replacement that doesn't save the string in the
    # GNU readline history.
    if not stream:
        stream = sys.stderr
    if not input:
        input = sys.stdin
    prompt = str(prompt)
    if prompt:
        stream.write(prompt)
        stream.flush()
    line = ""
    total_chars = 0
    if (mask):
        while True:
            c = input.read(1)
            if not c or c == "\n" or c == "\r":
                break;
            elif c == "\b" or ord(c) == 127: # Backspace or delete character
                if total_chars > 0:
                    stream.write("\b \b")
                    stream.flush()
                    line = line[:-1]
                    total_chars -= 1
            else:
                line += c
                total_chars += 1
                stream.write("*")
                stream.flush()
    else:
        # NOTE: The Python C API calls flockfile() (and unlock) during readline.
        line = input.readline()
    if not line:
        raise EOFError
    if line[-1] == '\n':
        line = line[:-1]
    return line


def getuser():
    """Get the username from the environment or password database.

    First try various environment variables, then the password
    database.  This works on Windows as long as USERNAME is set.

    """

    import os

    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user

    # If this fails, the exception will "explain" why
    import pwd
    return pwd.getpwuid(os.getuid())[0]

# Bind the name getpass to the appropriate function
try:
    import termios
    # it's possible there is an incompatible termios from the
    # McMillan Installer, make sure we have a UNIX-compatible termios
    termios.tcgetattr, termios.tcsetattr
except (ImportError, AttributeError):
    try:
        import msvcrt
    except ImportError:
        try:
            from EasyDialogs import AskPassword
        except ImportError:
            getpass = fallback_getpass
        else:
            getpass = AskPassword
    else:
        getpass = win_getpass
else:
    getpass = unix_getpass
