"""
Test script for getpass_asterisk.

Written by: Muhammad Akbar (akbar@secursive.com)

IMPORTANT SECURITY NOTE:
Echoing of masked password leaks the length of the password.
Use this utility only in a scenario where passwords are always of fixed length.
This utility was created to receive secret tokens as input which are always of
same size. Echoing the asterisks helped improve user experience.

"""

from getpass_asterisk.getpass_asterisk import getpass_asterisk

print("Token: {}".format(str(getpass_asterisk()).strip()))

