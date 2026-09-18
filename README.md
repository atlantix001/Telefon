# Fossify Phone filtered — v0.2.3

Private patch/build repository for Fossify Phone 1.11.1.

## Pinned upstream

- repository: `FossifyOrg/Phone`
- tag: `1.11.1`
- commit: `7de52a31a4d3cfc53e6cbc298a17ffca4e69141e`
- upstream package id: `org.fossify.phone`
- upstream versionCode: `22`

No build uses `main`.

## Ziel / Sichtlogik

Die Kontakt-Oberflächen dieser Custom-Version zeigen ausschließlich:

- echten lokalen Gerätespeicher,
- DAVx5-Adressbücher mit Account-Type `at.bitfire.davdroid.address_book`,
- echte SIM-ADN-Kontakte über Android `SimPhonebookContract` (API 31+).

Ausgeblendet werden innerhalb von Fossify Phone:

- Fossify privater Kontaktspeicher (`SMT_PRIVATE`),
- normales DAVx5-Hauptkonto,
- Google,
- Samsung,
- Messenger und sonstige Android-Konten.

Es wird nichts gelöscht oder aus dem Android ContactsProvider entfernt.

## Betroffene UI-Pfade

Die harte Allowlist gilt für:

- Kontakte-Tab,
- Suche im Kontakte-Tab,
- Favoriten,
- Dialpad/T9-Kontaktsuche,
- Speed Dial / Kontakt-Auswahldialog,
- Quellenfilter inklusive Kontaktzahlen.

SIM wird als eigene Quelle `SIM` bzw. `SIM 1` / `SIM 2` geführt. Die SIM-Anzahl kommt direkt aus `ElementaryFiles.RECORD_COUNT`. Das Filterdialog-UI wird erst aufgebaut, wenn Quellen und normale Kontaktzahlen bereit sind, damit gesetzte Häkchen nicht durch einen späten Adapter-Neuaufbau zurückgesetzt werden.

Auf dem verifizierten Pixel-Testgerät liefert `content://com.android.simphonebook/subid/1/adn` 18 ADN-Datensätze. Der Reader verwendet zuerst genau diese Sammelabfrage und fällt bei Bedarf auf Einzeldatensatz-URIs zurück.

## SIM-Verhalten in Phone

Phone liest SIM-Kontakte nur zur Anzeige/Anrufauswahl; es bearbeitet oder löscht sie nicht. Dafür ist die gefilterte Fossify-Contacts-App zuständig.

Synthetische SIM-Kontakte erhalten eine eindeutige negative `id`. Ein synthetischer `rawId` wird bewusst nicht gesetzt, da die aktuelle Commons-`Contact.copy(...)`-Signatur diesen Parameter nicht anbietet. Langdruck-/CAB-Aktionen auf SIM-Kontakten sind deaktiviert, damit Phone keine normalen ContactsProvider-Lösch-/Bearbeitungsaktionen auf SIM-Datensätze anwendet.

Da ein SIM-Datensatz keine normale ContactsProvider-Detail-URI besitzt, fällt ein Detail-Aufruf für einen SIM-Kontakt in Phone auf die normale Anrufaktion zurück.


## Cold-Start-Ablauf

Der Kaltstart übernimmt bewusst den bereits verifizierten Ablauf aus der gefilterten Fossify-Contacts-App:

1. Für den Kontakte-Tab kann sofort eine leichte `RawContacts`-Namens-/Quellen-Vorschau erscheinen.
2. Quellen-Ermittlung und normaler `ContactsHelper`-Kontaktlauf starten unabhängig voneinander.
3. Sobald beide normalen Ergebnisse vorliegen, werden Device-/DAVx5-Kontakte veröffentlicht — **ohne auf SIM zu warten**.
4. Erst nachdem dieses normale Ergebnis für die UI angestoßen wurde, startet die SIM-Ermittlung separat.
5. Ein nicht-leeres sichtbares SIM-Ergebnis wird anschließend mit einem zweiten Refresh ergänzt.

Phone-spezifisch wird die SIM-Ermittlung zusätzlich pro Prozess dedupliziert: parallele Fragment-/Startup-Aufrufe teilen sich eine einzige laufende `SimPhonebookContract`-Abfrage. `RecentsHelper` und `MainActivity.cacheContacts()` lesen beim Startup nur den SIM-Cache und starten keine zweite kalte SIM-Abfrage.

Die direkte SIM-Abfrage in Call-Screening/Caller-ID bleibt bewusst erhalten, da diese Pfade auch ohne zuvor geöffnete Phone-App funktionieren müssen.

## Caller-ID / Anrufauflösung

Caller-ID und Anrufhistorien-Namensauflösung bleiben bewusst **nicht** auf die sichtbaren Konten beschränkt. Fossify Phones bestehender `getAll=true`-Pfad bleibt erhalten, damit Namen aus anderen Android-Konten bei Anrufen weiterhin zuverlässig aufgelöst werden können. Zusätzlich werden direkte SIM-Kontakte in diese Namensauflösung aufgenommen.

Auch die Option zum Blockieren unbekannter Nummern berücksichtigt direkte SIM-Kontakte als bekannte Nummern.

## Reguläre Ersatz-App

Der Workflow baut die reguläre `fossRelease`-Variante mit Package-ID:

`org.fossify.phone`

Die offizielle Fossify Phone-App muss vor der ersten Installation dieser Custom-Version deinstalliert werden, da die Signatur unterschiedlich ist. Danach müssen alle Custom-Updates denselben Key aus diesem Repository verwenden.

## Build

GitHub Actions Workflow:

`.github/workflows/build.yml`

Erwartetes APK:

`Fossify-Phone-filter-0.2.3-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`d0a5480869b97fc295d50fb06e9a3a57100a15b6a3dcf2369e0a790a2a1d2e79`

## Lokale Prüfung

`0002-contacts-style-cold-start.patch` wurde statisch gegen den exakten Post-`0001`-Inhalt der beiden von `0001` neu angelegten Custom-Dateien sowie gegen die von `0001` erzeugten Zielkontexte in `MainActivity`, `ContactsFragment`, `ManageSpeedDialActivity` und `RecentsHelper` mit `git apply --check` und `git diff --check` geprüft.

Ein vollständiger Android-/Gradle-Build wurde in dieser Umgebung nicht ausgeführt; der Compile-/APK-Test erfolgt über GitHub Actions.

## v0.2.2 compile fix

v0.2.1 reached Kotlin compilation and failed at exactly one root error in `SimPhonebook.kt`: the current Commons `Contact.copy(...)` has no named `rawId` parameter.

v0.2.2 removes only `rawId = syntheticId`. The two custom source files remain explicitly included as `new file` entries in the patch. SIM contacts are non-selectable in Phone, so selection behavior does not depend on assigning a synthetic rawId. All other filtering/SIM logic is unchanged. Workflow and signing key are unchanged.

## v0.2.3 cold-start port

Ausgangspunkt ist wieder der unangetastete v0.2.2-Patchstand (`0001`). `0002-contacts-style-cold-start.patch` portiert den funktionierenden Kontakte-Kaltstart in einem zusammenhängenden Patch statt die früheren Diagnose-/Zwischenstände weiterzuführen.

Enthalten sind `RawContacts`-First-Paint, nicht blockierende normale Provider-Veröffentlichung, spätes SIM-Merge, SIM-Source-/Kontakt-Cache, In-Flight-Deduplizierung sowie cache-only Startup-Zugriffe für Recents und `cacheContacts()`. Der Workflow wendet alle Patches lexikographisch an.
