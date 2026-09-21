# Fossify Phone filtered — v0.2.6

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
- reguläre Android-Kontaktadressbücher, die provider-neutral über `ContactsContract`-SyncAdapter/Syncability erkannt werden; kein CardDAV-Anbieter ist fest verdrahtet,
- echte SIM-ADN-Kontakte über Android `SimPhonebookContract` (API 31+).

Ausgeblendet werden innerhalb von Fossify Phone:

- Fossify privater Kontaktspeicher (`SMT_PRIVATE`),
- technische bzw. nur lesbare Kontaktquellen,
- Konten ohne reguläre Kontakte-Sync-Funktion,
- bekannte Messenger-/Kontaktspiegel-Konten; Google wird zusätzlich ausgeblendet, wenn die Kontakte-Synchronisation für das konkrete Google-Konto deaktiviert ist.

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


## Coldstart / SIM-Pipeline in v0.2.4

Der in Fossify Contacts verifizierte Coldstart-Ansatz wurde auf die Phone-spezifischen Ladepfade übertragen. Die normale ContactsProvider-Liste wird nicht mehr von `SimPhonebookContract` blockiert:

1. normale Quellenabfrage und normale Kontaktabfrage starten parallel,
2. sobald beide normalen Ergebnisse vorliegen, wird die vollständige Geräte-/Adressbuch-Liste sofort veröffentlicht,
3. SIM-Quellen werden für UI-/Filterpfade aus einem In-Memory-Cache gelesen, statt dort erneut synchron entdeckt zu werden,
4. die langsame SIM-Abfrage läuft separat im Hintergrund und ergänzt die sichtbare Liste nur dann mit einem zweiten Ergebnis, wenn SIM-Kontakte vorhanden sind,
5. mehrere gleichzeitige Phone-Startpfade teilen sich eine laufende SIM-Abfrage (Single-Flight), damit der SIM-Provider beim Kaltstart nicht parallel mehrfach abgefragt wird,
6. `MainActivity`-Kontaktcache und die erste Anruflistenauflösung verwenden nur bereits gecachte SIM-Daten und blockieren deshalb den Start nicht; sobald der SIM-Warmup fertig ist, wird die Anrufliste einmal nicht-blockierend neu geladen, damit SIM-Namen nachgezogen werden.

Die direkte SIM-Auflösung für anrufkritische Pfade außerhalb des normalen App-Coldstarts (z. B. Caller-ID/Unknown-Number-Prüfung) bleibt erhalten.

## SIM-Verhalten in Phone

Phone liest SIM-Kontakte nur zur Anzeige/Anrufauswahl; es bearbeitet oder löscht sie nicht. Dafür ist die gefilterte Fossify-Contacts-App zuständig.

Synthetische SIM-Kontakte erhalten eindeutige negative `id`. Ein separates synthetisches `rawId` wird bewusst nicht gesetzt, da die in Phone verwendete Commons-Version dieses Feld nicht über `Contact.copy(...)` anbietet. Langdruck-/CAB-Aktionen auf SIM-Kontakten sind deaktiviert, damit Phone keine normalen ContactsProvider-Lösch-/Bearbeitungsaktionen auf SIM-Datensätze anwendet.

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

`Fossify-Phone-filter-0.2.6-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`168acb0bbdd5623c35993b79252f74213e41f1dc9d5ed07957501bf3ed77525b`

## Lokale Prüfung

Der v0.2.4-Hotfix vermeidet die fehleranfällige Patch-auf-Patch-Kette: Der Coldstart-Fix ist direkt in `patches/0001-device-davx-sim-filter.patch` integriert. Die Unified-Diff-Struktur wurde vollständig geprüft (`git apply --numstat`), alle Hunk-Zähler stimmen, und die neuen MainActivity-Kontexte entsprechen dem gepinnten 1.11.1-Upstream. Der vollständige Kotlin-/APK-Compile-Test erfolgt über GitHub Actions.


## v0.2.6 provider-neutrale Adressbücher + Google-Syncstatus

v0.2.6 lockert den in v0.2.5 noch zu strengen Capability-Filter für CardDAV-Clients. Ein echtes Kontaktadressbuch muss weder `SyncAdapter.isUserVisible()` noch `supportsUploading()` melden. Stattdessen genügt ein Contacts-SyncAdapter für den Account-Type; zusätzlich gibt es einen provider-neutralen Fallback über `ContentResolver.getIsSyncable()` für das konkrete Konto. Bekannte Messenger-/Kontaktspiegel-Typen bleiben explizit ausgeschlossen.

Google (`com.google`) ist eine gezielte Sonderregel: Das Google-Telefonbuch erscheint nur, wenn `ContentResolver.getSyncAutomatically(account, ContactsContract.AUTHORITY)` für dieses Google-Konto aktiv ist. Der globale Master-Sync-Schalter wird absichtlich nicht berücksichtigt. Es gibt keinerlei feste CardDAV-/DAVx5-Allowlist.

## v0.2.4 coldstart hotfix

- Coldstart-/SIM-Änderungen direkt in `patches/0001-device-davx-sim-filter.patch` integriert,
- neue `patches/series` als explizite Liste der tatsächlich anzuwendenden Patches,
- ein eventuell noch vorhandener alter `0002-nonblocking-sim-cold-start.patch` wird ignoriert und kann später gelöscht werden,
- normale Kontaktliste wartet nicht auf SIM,
- SIM-Quellen/-Kontakte werden gecacht und asynchron geladen,
- parallele Startverbraucher teilen sich eine laufende SIM-Abfrage,
- Cache und erste Recents-Auflösung blockieren beim Start nicht auf SIM.

**Wichtig bei GitHub-Web-Uploads:** `.github/workflows/build.yml` wurde in v0.2.4 erneut geändert und muss mit hochgeladen/ersetzt werden. Der versteckte `.github`-Ordner darf nicht fehlen.

## v0.2.2 compile fix

v0.2.1 reached Kotlin compilation and failed at exactly one root error in `SimPhonebook.kt`: the current Commons `Contact.copy(...)` has no named `rawId` parameter.

v0.2.2 removes only `rawId = syntheticId`. The two custom source files remain explicitly included as `new file` entries in the patch. SIM contacts are non-selectable in Phone, so selection behavior does not depend on assigning a synthetic rawId. All other filtering/SIM logic is unchanged. Workflow and signing key are unchanged.


## v0.2.4 hotfix

Der Coldstart-Fix ist jetzt direkt in `0001` integriert. Der Workflow verwendet `patches/series`; ein alter `0002` wird ignoriert.
