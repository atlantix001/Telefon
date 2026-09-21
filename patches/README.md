# Patch series

Die aktive Patchreihenfolge steht in `patches/series`. Der GitHub-Actions-Workflow wendet ausschließlich die dort aufgeführten Dateien an.

- `0001-device-davx-sim-filter.patch`: Geräte-/Adressbuch-/SIM-Filter plus non-blocking SIM-Coldstart. Normale Kontakte werden ohne Warten auf den SIM-Provider veröffentlicht; SIM wird asynchron geladen, gecacht und bei parallelen Verbrauchern per Single-Flight geteilt. Cache und Recents blockieren beim Start nicht auf SIM.

- `0002-capability-based-address-books.patch`: ersetzt die DAVx5-Hardcodierung durch eine provider-neutrale `ContactsContract`-Prüfung ohne `isUserVisible()`/`supportsUploading()`-Pflicht, ergänzt einen Syncability-Fallback, blendet bekannte Messenger-Kontaktspiegel aus und zeigt Google nur bei aktivierter Kontakte-Synchronisation für das konkrete Google-Konto. Die `phone_storage`-Label-Heuristik bleibt entfernt.

Ein alter `0002-nonblocking-sim-cold-start.patch` aus v0.2.3 kann gelöscht werden. Falls er noch im Repository liegt, wird er nicht angewendet, solange er nicht in `patches/series` steht.
