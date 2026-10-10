# v0.2.11: Minimal-Verknüpfungen für Fossify Phone (One UI 9)

Die vom Benutzer genannten Optionen und ihre Erreichbarkeit wurden anhand der
hochgeladenen `SamsungCallSettings.apk` (TelephonyUI) geprüft. **Wichtig:** Die
APK wurde analysiert, aber die Verknüpfungen konnten nicht auf dem echten S25
ausgeführt werden. Bei den Benutzeroberflächen handelt es sich nicht um eine
Vollreplikation von Samsung Call Settings.

| Gewünscht | Umsetzung in 0005 | Begründung |
|---|---|---|
| Nummern sperren | `TelecomManager.createManageBlockedNumbersIntent()` | Öffentlicher Android-API-Einstieg, ggf. anderes UI/anderer Umfang als Samsung-Sonder-Sperrregeln |
| WLAN-Anrufe | `android.settings.WIFI_CALLING_SETTINGS` | Standard-Settings-Intent; Carrier/ROM muss Activity bereitstellen |
| Anruferinnerungen & Klingelton | Über TelephonyUI `CallSettingsActivity` | Keine separat exportierte Unterseiten-Activity nachgewiesen |
| Anrufe beantworten und beenden | Über `CallSettingsActivity` | Ob einzelne Schalter bei Fossify wirken, muss getestet werden |
| Zusatzdienste | Über `CallSettingsActivity` | Rufumleitung/Anklopfen/Caller-ID sind netz- bzw. SIM-abhängig |
| Andere Anrufeinstellungen | Über `CallSettingsActivity` | Nicht direkt exportierte Unterseite |
| Anrufinformationen | Nicht verlinkt | Samsung-UI-spezifische Einstellungen könnten Fossify ignorieren |
| Schnellnachrichten zum Ablehnen | Nicht verlinkt | Samsung-InCallUI-Verhalten; Fossify verwendet möglicherweise eigene Ablehntexte |
| Anrufanzeige bei App-Verwendung | Nicht verlinkt | Samsung-Anruf-Popup statt Fossify-InCallUI |

Die APK exportiert `CallSettingsActivity`, nicht aber jeweils eine eigene
Activity für jeden Preference-Screen. Als direkter Einstieg ist außerdem
`NetSettingsActivity` exportiert. Ein eigenes `startActivity` auf nicht
exportierten Komponenten oder das bloße Erfinden von Navigations-Extras
funktioniert ohne Samsung-Signatur nicht zuverlässig.

Die 0005-Ergänzung erstellt in Fossifys Toolbar-Menü **Telefon- und
Netzeinstellungen** mit einer privaten (nicht exportierten) Activity und drei
Aktionen. Hierfür sind keinerlei zusätzlichen Berechtigungen nötig.

## ADB-Laufzeittests, vor Aktivierung in Fossify

```powershell
# Samsung-Haupt-Anrufeinstellungen, extern ansprechbare Activity
.\adb.exe shell am start -n com.samsung.android.app.telephonyui/com.samsung.android.app.telephonyui.callsettings.ui.preference.CallSettingsActivity

# Generischer WLAN-Anrufe-Einstieg (kann am Gerät fehlen)
.\adb.exe shell am start -a android.settings.WIFI_CALLING_SETTINGS

# Android-Blocked-Numbers-UI (Test nur orientierend; Fossify nutzt TelecomManager API)
.\adb.exe shell am start -a android.telecom.action.MANAGE_BLOCKED_NUMBERS
```

**Erst nach Erfolgsnachweis auf dem Gerät** zusätzliche Direktlinks/Unterseiten
hinzufügen. Vor dem Test bitte Fossify als Standard-Telefon-App festlegen.

## Grenzen des Patches

- Ein vollständig mit v1.11.1 gepinnter Upstream konnte in der Offline-Umgebung
  nicht geladen oder gebaut werden. Die 0005-Strukturänderung und ihre
  Einfügeanker wurden anhand eines synthetischen Fixtures getestet.
- Samsung TelephonyUI muss für die dritte Aktion aktiv sein. Nicht TelephonyUI
  selbst deinstallieren, wenn seine Einstellungen erhalten bleiben sollen.
- Androids Call-Blocking-Liste und Samsungs eigene erweiterte Nummernfilter
  müssen nicht identisch sein.
