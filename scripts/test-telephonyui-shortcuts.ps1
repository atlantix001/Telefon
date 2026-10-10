# Read-only entrypoint tests before creating links in Fossify Phone.
# The precise target screens must be chosen by the user; run am start only by hand.
# Requires ADB connected to an unlocked Galaxy S25.
$ErrorActionPreference = 'Stop'
$Pkg = 'com.samsung.android.app.telephonyui'
Write-Host 'TelephonyUI installed:'
& .\adb.exe shell pm list packages --user 0 | Select-String -SimpleMatch $Pkg
Write-Host '\nExported call settings activity and intent filters:'
& .\adb.exe shell dumpsys package $Pkg | Select-String 'CallSettingsActivity|NetSettingsActivity|SimCardMgrActivity|OPEN_CALL_SETTINGS|OPEN_NET_SETTINGS' -Context 1,1 | Select-Object -First 75
Write-Host '\nManual tests (do not run until you select the settings you actually need):'
Write-Host 'adb shell am start -n com.samsung.android.app.telephonyui/com.samsung.android.app.telephonyui.callsettings.ui.preference.CallSettingsActivity'
Write-Host 'adb shell am start -n com.samsung.android.app.telephonyui/com.samsung.android.app.telephonyui.netsettings.ui.NetSettingsActivity'
Write-Host '\nNote: SimCardMgrActivity is exported but requires android.permission.MODIFY_PHONE_STATE; do not try to bypass its permission.'
