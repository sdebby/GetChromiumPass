# 12.01.2025
# Description: This script extracts saved passwords from Microsoft Edge, Chrome and Opera browser.
# installing pip install pywin32 sqlite3 pycryptodome

# Note: Local admin rights are required to decrypt the passwords.

import argparse
import os
import json
import base64
import sqlite3
import shutil
import tempfile
import win32crypt
from Crypto.Cipher import AES
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

EdgePath = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State")
EdgeLoginData = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data")

ChromePath = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
ChromeLoginData = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data")

OperaPath = os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable\Local State")
OperaLoginData = os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable\Login Data")

def get_master_key(DBpath):
    try:
        with open(DBpath, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]  # Remove DPAPI prefix
        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
        # print(f'Masker key:{master_key}')
        return master_key
    except FileNotFoundError:
        print(f"Error: Could not find Local State file")
        return None
    except Exception as e:
        print(f"Failed to get master key: {e}")
        return None

def decrypt_password(encrypted_password, master_key):
    try:
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)[:-16].decode()
        return decrypted_pass
    except Exception as e:
        print(f"Failed to decrypt password: {e}")
        return None

def extract_passwords(DBpath,DBKeyPath):
    master_key = get_master_key(DBKeyPath)
    if not master_key:
        return []
    
    # Create a temporary copy of the database
    temp_db = os.path.join(tempfile.gettempdir(), "edge_login_data.db")
    
    try:
        shutil.copy2(DBpath, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        password_list = []
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            
            if not url or not username or not encrypted_password:
                continue
                
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if decrypted_password:
                password_list.append({
                    "url": url,
                    "username": username,
                    "password": decrypted_password
                })
                
        conn.close()
        return password_list
        
    except Exception as e:
        print(f"Error extracting passwords: {e}")
        return []
    finally:
        try:
            os.remove(temp_db)  # Clean up temporary file
        except:
            pass

def StartHere(LoginData: str, Path: str) -> None: #Extract and display passwords for a specific browser.
    passwords = extract_passwords(LoginData, Path)
    for entry in passwords:
        print(f"URL: {entry['url']}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}\n")

def format_password_output(browser_name: str, passwords: List[Dict[str, str]]) -> str: #Format password entries for a specific browser into a readable string.
    header = f"\n{browser_name} Passwords:\n{'=' * 50}\n"
    
    entries = []
    for entry in passwords:
        entry_str = [
            f"URL: {entry['url']}",
            f"Username: {entry['username']}",
            f"Password: {entry['password']}",
            "-" * 50
        ]
        entries.append("\n".join(entry_str))
    
    return header + "\n".join(entries)

def save_to_file(all_passwords: str, output_dir: Optional[Path] = None) -> bool: #Save extracted passwords to a file with timestamp.
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"browser_passwords_{timestamp}.txt"
        
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            filepath = output_dir / filename
        else:
            filepath = Path(filename)
            
        header = [
            "Browser Passwords Export",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            all_passwords
        ]
        
        filepath.write_text("\n".join(header), encoding="utf-8")
        print(f"Passwords saved to: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving passwords: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get passwords from chromium based browsers")
    parser.add_argument('-s', '--save', action='store_true', help="Save passwords to file")

    args = parser.parse_args()
    if args.save:
        all_output = ""
        
        # Edge passwords
        edge_passwords = extract_passwords(EdgeLoginData, EdgePath)
        all_output += format_password_output("Microsoft Edge", edge_passwords)
        
        # Chrome passwords
        chrome_passwords = extract_passwords(ChromeLoginData, ChromePath)
        all_output += format_password_output("Google Chrome", chrome_passwords)
        
        # Opera passwords
        opera_passwords = extract_passwords(OperaLoginData, OperaPath)
        all_output += format_password_output("Opera", opera_passwords)
        
        save_to_file(all_output)
    else:
        print(' -- Passwords extracted from Microsoft Edge --\n ')
        StartHere(EdgeLoginData, EdgePath)
        print('-' * 35)
        
        print(' \n** Passwords extracted from Chrome **\n ')
        StartHere(ChromeLoginData, ChromePath)
        print('*' * 35)

        print(' \n== Passwords extracted from Opera ==\n ')
        StartHere(OperaLoginData, OperaPath)
        print('=' * 35)
