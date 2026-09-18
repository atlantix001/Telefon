# Fossify Phone filtered — v0.2.4

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

Synthetische SIM-Kontakte erhalten eine eindeutige negative `id`. Sie werden in Phone nicht als auswählbare Langdruck-/CAB-Einträge behandelt, damit keine normalen ContactsProvider-Lösch-/Bearbeitungsaktionen auf SIM-Datensätze angewendet werden. Ein synthetischer `rawId` wird bewusst nicht gesetzt, da die aktuelle Commons-`Contact.copy(...)`-Signatur diesen Parameter nicht anbietet.

Da ein SIM-Datensatz keine normale ContactsProvider-Detail-URI besitzt, fällt ein Detail-Aufruf für einen SIM-Kontakt in Phone auf die normale Anrufaktion zurück.

## Kaltstart / nicht blockierende SIM-Abfrage

Der Kontakte-Tab wartet beim Kaltstart nicht mehr auf den langsamen `SimPhonebookContract`-Provider:

1. ContactsProvider-Quellen und normale Kontakte werden unabhängig gestartet,
2. sobald beide normalen Ergebnisse vorliegen, werden Geräte-/DAVx5-Kontakte sofort veröffentlicht,
3. die SIM-Abfrage läuft separat im Hintergrund,
4. vorhandene sichtbare SIM-Kontakte werden anschließend mit einem zweiten Refresh ergänzt.

Die SIM-Quellen werden nach der Hintergrundabfrage im Speicher gecacht. `MainActivity.cacheContacts()` verwendet ebenfalls nur den bereits vorhandenen SIM-Kontaktcache und löst dadurch keine synchrone SIM-Abfrage im UI-Callback mehr aus. Leere SIM-Ergebnisse erzeugen keinen zweiten identischen Listen-Refresh.

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

Die Workflow-Patches werden in lexikalischer Reihenfolge aus `patches/*.patch` angewendet.

Erwartetes APK:

`Fossify-Phone-filter-0.2.4-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`d0a5480869b97fc295d50fb06e9a3a57100a15b6a3dcf2369e0a790a2a1d2e79`

## Lokale Prüfung

`0002-nonblocking-sim-cold-start.patch` wurde statisch gegen den exakten Post-`0001`-Stand der von `0001` neu angelegten Custom-Dateien sowie gegen den dort erzeugten `MainActivity`-Kontext mit `git apply --check` und `git diff --check` geprüft. Ein vollständiger Android-Build wird weiterhin von GitHub Actions durchgeführt.

## v0.2.4 recents cold-start fix

A cold-start log from the Pixel test device showed that `MainActivity` was displayed quickly, but the UI thread then spent about two seconds handling the initial focus event and skipped hundreds of frames. The remaining startup-time direct SIM read was in `RecentsHelper`: call-history contact resolution still called `getSimPhonebookContacts()` synchronously after the normal ContactsProvider result arrived.

`0003-nonblocking-recents-sim-cache.patch` changes only that startup path to use `getCachedSimPhonebookContacts()`. SIM discovery itself remains on the background path introduced by `0002`; the call-screening path keeps its direct lookup because it must work even when the Phone UI has not populated the in-memory cache.

## v0.2.3 non-blocking SIM cold start

- neuer `0002-nonblocking-sim-cold-start.patch`,
- normaler Kontakte-/Dialpad-Load wird nicht mehr von der SIM-Abfrage gegated,
- SIM-Discovery und SIM-Kontakte laufen separat im Hintergrund und werden bei Bedarf nachgereicht,
- SIM-Quellen und geladene SIM-Kontakte werden im Speicher gecacht,
- `MainActivity.cacheContacts()` liest beim UI-Callback nur den SIM-Cache statt den SIM-Provider synchron erneut zu öffnen,
- Build-Workflow wendet jetzt alle `patches/*.patch` in lexikalischer Reihenfolge an.

## v0.2.2 compile fix

v0.2.1 reached Kotlin compilation and failed at exactly one root error in `SimPhonebook.kt`: the current Commons `Contact.copy(...)` has no named `rawId` parameter.

v0.2.2 removes only `rawId = syntheticId`. The two custom source files remain explicitly included as `new file` entries in the patch. SIM contacts are non-selectable in Phone, so selection behavior does not depend on assigning a synthetic rawId. All other filtering/SIM logic is unchanged. Workflow and signing key are unchanged.
