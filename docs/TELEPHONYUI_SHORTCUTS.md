# One UI 9: TelephonyUI – geprüfte Android-Einstiegspunkte

Quelle: vom Gerät exportierte `SamsungCallSettings.apk`, Paketname
`com.samsung.android.app.telephonyui`; deren binäres AndroidManifest.xml
wurde ausgelesen. `exported=true` bedeutet, dass eine fremde App die Activity
grundsätzlich adressieren kann. Android-Permissions, App-Logik, SIM-Status,
Länder- und Carrier-Konfiguration gelten weiterhin.

| Activity | AndroidManifest | Permission | Eignung |
|---|---|---|---|
| `callsettings.ui.preference.CallSettingsActivity` | `exported=true` | keine Activity-Permission | Prüfbarer Haupteinstieg für Anrufeinstellungen |
| `netsettings.ui.NetSettingsActivity` | `exported=true` | keine Activity-Permission | Prüfbarer Haupteinstieg für Mobilfunk-/Netzwerkeinstellungen |
| `callsettings.ui.roamingautodial.RoamingAutoDialSettingsActivity` | `exported=true` | keine Activity-Permission | Nur falls Roaming Auto Dial genutzt wird |
| `callsettings.ui.callingaccounts.MakeCallsWithDialogActivity` | `exported=true` | keine Activity-Permission | Dialog, nicht identisch mit beliebigen Unterseiten |
| `netsettings.ui.simcardmanager.SimCardMgrActivity` | `exported=true` | `android.permission.MODIFY_PHONE_STATE` | **Nicht** frei für Fossify startbar, nicht als Shortcut vorsehen |
| `callsettings.ui.callbackground.CallBackgroundExternalActivity` | `exported=true` | `com.samsung.android.app.telephonyui.permission.ACCESS_CALL_BACKGROUND_SETTING` | Anbieterspezifische Berechtigung; nicht als frei startbar ansehen |
| `callsettings.ui.callbackground.CallBackgroundBaseActivity` | `exported=false` | – | Kein direkter Fremd-App-Start |
| `callsettings.ui.tty.TtyModeDialogActivity` | `exported=false` | – | Kein direkter Fremd-App-Start |

**Vollständige Intent-Actions der zwei Kandidaten:**

- CallSettings: `com.samsung.android.app.telephonyui.action.OPEN_CALL_SETTINGS`
- NetSettings: `com.samsung.android.app.telephonyui.action.OPEN_NET_SETTINGS`

**Nur bei installiertem TelephonyUI** sind Tests möglich:

```powershell
.\adb.exe shell am start -n com.samsung.android.app.telephonyui/com.samsung.android.app.telephonyui.callsettings.ui.preference.CallSettingsActivity
.\adb.exe shell am start -n com.samsung.android.app.telephonyui/com.samsung.android.app.telephonyui.netsettings.ui.NetSettingsActivity
```

Die Tests öffnen zunächst nur die jeweiligen Haupteinstellungen. Ob ein bestimmter
Unterpunkt per zusätzlichen Intent-Extras direkt geöffnet werden kann, ist
**nicht** aus dem Manifest nachgewiesen. Keine nicht-exportierten Activities
oder geschützten Telefondienste für die Fossify-App freischalten oder
mit erfundenen Intent-Extras ansprechen.

**Weitere Entwicklung:** Zunächst die vom Benutzer gewünschten Unterpunkte
benennen; dann auf dem Gerät die zugehörigen Intents und nötigen Extras beim
manuellen Öffnen per Logcat ermitteln. Erst danach `0005` mit tatsächlich
funktionierenden, defensiv behandelten Menülinks erstellen.
