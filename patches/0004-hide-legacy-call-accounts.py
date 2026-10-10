#!/usr/bin/env python3
"""Fossify Phone 1.11.1: remove obsolete Calling Accounts entry from Settings toolbar.

This intentionally changes *only* Fossify's own navigation. Android Telecom's
system Calling Accounts UI cannot be edited by a third-party dialer.
Future TelephonyUI shortcuts should be added separately after verifying exported
activity entry points, actual behavior and the user's desired subsections.
"""
from pathlib import Path
import sys

upstream = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream-phone").resolve()
settings = upstream / "app/src/main/kotlin/org/fossify/phone/activities/SettingsActivity.kt"
if not settings.is_file():
    raise SystemExit(f"Fossify SettingsActivity missing: {settings}")
text = settings.read_text(encoding="utf-8")
needle = "findItem(R.id.calling_accounts).isVisible = canLaunchAccountsConfiguration()"
replacement = "removeItem(R.id.calling_accounts) // Hide old Android call-accounts entry; leave telecom configuration untouched."
if replacement in text:
    print("Legacy call-accounts menu item already hidden")
    sys.exit(0)
if text.count(needle) != 1:
    raise SystemExit(f"Expected exactly one call-accounts menu visibility anchor, found {text.count(needle)}; refusing to patch unknown upstream")
settings.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
print("Removed the obsolete Calling Accounts menu entry from Fossify Settings toolbar")
