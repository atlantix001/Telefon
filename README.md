# Fossify Phone filtered — v0.2.0

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

Synthetische SIM-Kontakte erhalten eindeutige negative `id` und `rawId`, weil Fossify Phone `rawId` als Auswahl-Key benutzt. Langdruck-/CAB-Aktionen auf SIM-Kontakten sind deaktiviert, damit Phone keine normalen ContactsProvider-Lösch-/Bearbeitungsaktionen auf SIM-Datensätze anwendet.

Da ein SIM-Datensatz keine normale ContactsProvider-Detail-URI besitzt, fällt ein Detail-Aufruf für einen SIM-Kontakt in Phone auf die normale Anrufaktion zurück.

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

`Fossify-Phone-filter-0.2.0-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`1d5acf6b344098e93d05375ff6626d317a409fd96907d3cd66c281d20ee4f4bb`

## Lokale Prüfung

Der Patch wurde gegen den bereitgestellten Source-Snapshot von Fossify Phone 1.11.1 statisch mit `git apply --check` und `git diff --check` geprüft. In dieser Umgebung wurde kein vollständiger Android-Build behauptet; der Compile-/APK-Test erfolgt über GitHub Actions.
