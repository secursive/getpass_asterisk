# getpass_asterisk
An alternative implementation for getpass that echoes masked password (such as asterisks).

## Usage
Usage is identical to getpass.

```python
# getpass_asterisk(prompt[, stream]) - Prompt for a password, with masked output.

from getpass_asterisk.getpass_asterisk import getpass_asterisk
password = getpass_asterisk("Enter password: ")
```
