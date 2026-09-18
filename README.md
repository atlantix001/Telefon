# Fossify Phone filtered — v0.2.3-r5

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

`Fossify-Phone-filter-0.2.3-r5-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`b126d11f52875a1be6cc8b828dc38bcc5523aa086c77c89c102969adcf3763d7`

## Lokale Prüfung

Die Patchsyntax wurde lokal mit `git apply --numstat` geprüft. Der konsolidierte `0002` wurde zusätzlich mit `git apply --check` und `git diff --check` gegen einen Post-`0001`-Validierungsbaum mit den tatsächlichen betroffenen Code-Kontexten geprüft. Der vollständige Clone von Fossify Phone 1.11.1 und damit die endgültige Patch-/Compile-Prüfung erfolgt im GitHub-Actions-Workflow.

## v0.2.2 compile fix

v0.2.1 reached Kotlin compilation and failed at exactly one root error in `SimPhonebook.kt`: the current Commons `Contact.copy(...)` has no named `rawId` parameter.

v0.2.2 removes only `rawId = syntheticId`. The two custom source files remain explicitly included as `new file` entries in the patch. SIM contacts are non-selectable in Phone, so selection behavior does not depend on assigning a synthetic rawId. All other filtering/SIM logic is unchanged. Workflow and signing key are unchanged.

## v0.2.3-r3 hard first-paint barrier

This clean rebuild starts from the original v0.2.2 repository. Contacts and Favorites are the only immediate startup refreshes. MainActivity cache work and Recents are delayed by 3 seconds, and SIM discovery is delayed by 3.5 seconds after the authoritative normal-contact result. This intentionally prevents Phone-specific provider consumers from overlapping the first contact frame after reboot.

## v0.2.3-r4 workflow correction

This release fixes a packaging/build error in the previous clean cold-start test repositories.
The repository contained `0002` and `0003`, but the GitHub Actions workflow still applied only
`0001-device-davx-sim-filter.patch`. Therefore r2/r3 APKs built from those repositories did not
contain the advertised cold-start changes.

The workflow now applies every `patches/*.patch` in lexical order with `git apply --check` before
each application, then runs `git diff --check`. The patch contents themselves are unchanged from
r3; this release exists to ensure they are actually present in the APK.


## v0.2.3-r5 patch-chain correction

r5 fixes the patch-generation error exposed by the first r4 GitHub Actions run. The old `0002`
contained hunks generated from incomplete synthetic file fragments, and the old `0003` was generated
from the same kind of fixture. That is why `git apply --check` failed after `0001`.

r5 removes `0003` entirely and folds its intended startup-barrier changes into one consolidated
`0002-contacts-style-cold-start.patch`. The redundant ManageSpeedDial hunk is removed because `0001`
already contains that change. The ContactsFragment, RecentsHelper, CallContactHelper and MainActivity
hunks now use the actual post-`0001` code context/line regions.

The workflow still applies every `patches/*.patch` lexically with `git apply --check` before applying
it. r5 therefore has the intentionally short patch chain `0001 -> 0002`.
