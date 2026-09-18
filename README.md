# Fossify Phone filtered — v0.2.7

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

## Kaltstart / nicht blockierende Quellen- und SIM-Abfrage

Der Kontakte-Tab wartet beim Kaltstart weder auf Fossifys vollständige Quellen-Ermittlung noch auf den langsamen `SimPhonebookContract`-Provider:

1. die erlaubten Geräte-/DAVx5-Quellen werden direkt und leichtgewichtig aus `RawContacts` ermittelt,
2. normale Kontakte werden mit `getAll = false` geladen und anschließend durch die harte Allowlist gefiltert,
3. die SIM-Abfrage läuft separat im Hintergrund,
4. normale Kontakte werden veröffentlicht, sobald RawContacts-Allowlist und ContactsProvider-Ergebnis vorliegen,
5. vorhandene sichtbare SIM-Kontakte werden anschließend mit einem zweiten Refresh ergänzt.

`MainActivity.cacheContacts()` verwendet ebenfalls `getAll = false` und nur den bereits vorhandenen SIM-Kontaktcache. Dadurch wird im UI-Startup kein vollständiger Fossify-Quellenlauf mehr angefordert. Leere SIM-Ergebnisse erzeugen keinen zweiten identischen Listen-Refresh.

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

`Fossify-Phone-filter-0.2.7-1.11.1.apk`

## Signing freeze

Dieser Key wurde als initialer fester Key für die Phone-Filter-Linie erzeugt und darf ab jetzt nicht mehr geändert werden.

- alias: `fossify-phone-filter`
- keystore SHA-256: `d09def770497c58e34d3eba954f8a1acdf4904b4a2b651b223d6cb06abc7817e`
- certificate SHA-256: `A0:B9:DB:71:6E:10:FD:0D:75:6C:B4:69:FE:DB:07:B8:C8:78:CF:0A:F1:E0:95:2F:5E:55:E7:94:BF:30:DA:9A`

Workflow SHA-256:

`d0a5480869b97fc295d50fb06e9a3a57100a15b6a3dcf2369e0a790a2a1d2e79`

## Lokale Prüfung

`0006-cold-start-diagnostics.patch` wurde syntaktisch mit `git apply --check` und `git diff --check` gegen den Post-`0005`-Kontext der von den bisherigen Patches veränderten Stellen geprüft. Zusätzlich bleibt der Signing-Key byte-identisch. Ein vollständiger Android-/Gradle-Build wird weiterhin von GitHub Actions durchgeführt.

## v0.2.7 cold-start diagnostics

`0006-cold-start-diagnostics.patch` ist absichtlich ein reiner Diagnose-Patch. Er ändert keine Filter- oder Ladeentscheidung, sondern schreibt Zeitmarker unter dem Logcat-Tag `FossifyColdStart`. Erfasst werden insbesondere:

- `ContactsFragment.refreshItems()` inklusive sichtbarem `gotContacts()`,
- `FavoritesFragment.refreshItems()`,
- `loadVisiblePhoneContacts()` inklusive RawContacts-Allowlist und ContactsHelper-Callback,
- `MainActivity.cacheContacts()`,
- der Recents-Kontakt-Zusammenbau,
- SIM-Quellen-, SIM-Kontakt- und SIM-Verzeichnisabfragen.

Jeder Marker enthält `+N ms` seit dem ersten Diagnoseereignis sowie den Threadnamen. Damit lässt sich der verbleibende 2–3-Sekunden-Blocker aus einem gefilterten Log eindeutig einem Pfad zuordnen. Nach der Diagnose kann `0006` wieder entfernt oder durch den eigentlichen Fix ersetzt werden.

## v0.2.6 no-full-source-enumeration cold-start fix

Der Kaltstart-Log von v0.2.5 zeigt die `MainActivity`-Surface um 10:46:13.589 und bereits 7 ms später das Auftauen von `org.fossify.contacts`. Der Phone-Hauptthread taucht im Log erst rund 2,94 s später wieder auf. `0004` hatte damit zwar den expliziten `getMyContactsCursor()`-Zugriff entfernt, aber nicht die zwei indirekten Vollquellenpfade.

`0005-avoid-full-source-enumeration-on-startup.patch` entfernt diese beiden verbliebenen Startup-Pfade:

- `loadVisiblePhoneContacts()` verwendet nicht mehr `ContactsHelper.getContactSources()` als Gate und lädt normale Kontakte nicht mehr mit `getAll = true`; die harte Device/DAVx5-Allowlist wird stattdessen direkt über `RawContacts.ACCOUNT_NAME`/`ACCOUNT_TYPE` aufgebaut.
- `MainActivity.cacheContacts()` wechselt ebenfalls von `getAll = true` auf `getAll = false`.

Damit kann Commons im Kontakt-Startup nicht mehr über `getAll = true` auf die vollständige Quellenliste inklusive `SMT_PRIVATE` wechseln. SIM bleibt weiterhin vollständig separat im Hintergrund und wird aus dem Cache ergänzt.

## v0.2.5 private-provider cold-start fix

Der zweite Kaltstart-Log zeigt direkt nach dem Aufbau der `MainActivity` eine Prozessbeziehung von `org.fossify.phone` zu `org.fossify.contacts`. `ContactsFragment` ruft `MainActivity.cacheContacts()` noch vor der sichtbaren Veröffentlichung der Kontaktliste auf. Dort wurde bisher trotz der harten Allowlist weiterhin bedingungslos `getMyContactsCursor()` geöffnet; erst danach wurde geprüft, ob `SMT_PRIVATE` ignoriert ist.

`0004-skip-private-cache-provider-on-startup.patch` entfernt diesen für die gefilterte Variante unnötigen Private-Contacts-Providerzugriff aus `cacheContacts()`. Normale Android-/DAVx5-Kontakte sowie der bereits im Hintergrund gefüllte SIM-Cache bleiben unverändert. Der private Pfad in `RecentsHelper` wird in diesem Diagnose-Patch bewusst noch nicht gleichzeitig verändert, damit die im Log belegte Startup-Ursache isoliert getestet werden kann.

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
