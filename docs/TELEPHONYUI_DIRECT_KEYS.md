# Samsung TelephonyUI – direkte Fragmentziele (One UI 9)

Stand: TelephonyUI aus `SamsungCallSettings.zip`, aktuelle Logcat-Dateien
`TelephonyUI-Anruferinnerungen_Kilngelton.log`,
`TelephonyUI-Anrufebeantworten.log`,
`TelephonyUI-Zusatzdienste.log`, `TelephonyU-Andere.log`,
`TelephonyUI-Anrufrerinformation.log`.

Alle fünf Schritte navigieren in derselben exportierten Activity:
`com.samsung.android.app.telephonyui/.callsettings.ui.preference.CallSettingsActivity`.
Es gibt KEINE separaten START-Events beim Fragmentwechsel. Logtags
`CU.CallSettingsActivityUtil: convertToCallSettingsKey(...)` und
`CU.CommonFragment: ... settingsKey : ...` belegen diese Zuordnung:

| Menüpunkt | root_key |
|---|---|
| Anruferinnerungen und Klingelton | `CALL_ALERTS_AND_RINGTONES` |
| Anrufe beantworten und beenden | `ANSWERING_AND_ENDING_CALLS` |
| Zusatzdienste | `SUPPLEMENTARY_SERVICE_COMMON` |
| Andere Anrufeinstellungen | `OTHER_CALL_SETTINGS` |
| Anrufinformationen (optional) | `CALL_LAYOUT` |

In der DEX-Datei von TelephonyUI liest `CallSettingsActivity.onCreate()` den
String-Extra `root_key` via `Intent.getStringExtra`, wandelt ihn über
`CallSettingsActivityUtil.convertToCallSettingsKey()` in den Enum-Typ
`CallSettingsKey` um und setzt den Anfangszustand. Die gleiche Extra-
Behandlung ist in `onNewIntent` zu sehen.

**Beweisgrenze:** Externes Öffnen ist noch nicht auf dem Gerät getestet.
Der Samsung-Code unterstützt die Übergabe, aber firmwareabhängige
Validierungen oder SIM-Bedingungen können einzelne Ziele umlenken.

### Vier sichere, lesbare ADB-Tests

```powershell
$activity = 'com.samsung.android.app.telephonyui/.callsettings.ui.preference.CallSettingsActivity'
$action = 'com.samsung.android.app.telephonyui.action.OPEN_CALL_SETTINGS'
foreach ($key in @('CALL_ALERTS_AND_RINGTONES','ANSWERING_AND_ENDING_CALLS','SUPPLEMENTARY_SERVICE_COMMON','OTHER_CALL_SETTINGS')) {
    Write-Host "Teste $key"
    .\adb.exe shell am start -n $activity -a $action --es root_key $key
    Read-Host 'Die korrekte Unterseite sichtbar? Eingabetaste für nächsten Test'
}
```

Die bisherigen geprüften Nummernsperr- und WLAN-Telefonie-Links bleiben
unverändert. `CALL_LAYOUT` bleibt vorerst außen vor, da seine Effekte auf
die Samsung-InCall-Oberfläche bezogen sein können, nicht Fossifys UI.
