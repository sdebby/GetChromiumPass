# BrowserSecretSeeker - Browser Password Extractor

## Overview
A Python script for extracting saved passwords from Chromium-based browsers (Chrome, Edge, Opera) on Windows systems. The tool can display passwords, or save them to a timestamped file.
Can be used in rubber ducky operation script.

> [!NOTE]  
> The code will work on local admin rights.

## Skill set:
- Python 3.x
- Win32 Crypto API
- SQLite3
- AES Decryption
- Chromium Browser Architecture

## Requirements
```bash
pip install pycryptodome pywin32 sqlite3
```

# Behind the scenes:
The tool performs these key operations:

1. Locates browser profile directories
2. Extracts the master encryption key
3. Copies and queries the Login Data SQLite database
4. Decrypts passwords using AES-GCM
5. Formats and displays/saves results

# Run
```bach
python GetPass.py
python GetPass.py -s
```

> [!CAUTION]
> This tool is for educational purposes and personal password recovery only. Always comply with applicable laws and regulations.

## Feedback
If you have any feedback, please reach out to us at shmulik.debby@gmail.com
