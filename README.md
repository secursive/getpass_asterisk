# getpass_asterisk
An alternative implementation for getpass that echoes masked password (such as asterisks).

## Security Note
> :warning: This module has been modified to add getpass_asterisk, which can echo asterisks in place of password. **Echoing of masked password leaks the length of the password**. Use this utility only in a scenario where passwords are always of fixed length. This utility was created to receive secret tokens as input which are always of same size. Echoing the asterisks helped improve user experience. Use at your own risk. Only use for taking constant length secret inputs.

## Installation
pip can be used to install getpass_asterisk.

```bash
pip install getpass_asterisk
```

## Usage
Usage is identical to getpass.

```python
# getpass_asterisk(prompt[, stream]) - Prompt for a password, with masked output.

from getpass_asterisk.getpass_asterisk import getpass_asterisk
password = getpass_asterisk("Enter password: ")
```

## Feedback
For feedback, contact: Muhammad Akbar (akbarATsecursive.com).
