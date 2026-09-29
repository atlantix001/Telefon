# Patch series

Die aktive Patchreihenfolge steht in `patches/series`. Der GitHub-Actions-Workflow wendet ausschließlich die dort aufgeführten Dateien an.

- `0001-device-davx-sim-filter.patch`: Geräte-/Adressbuch-/SIM-Filter plus non-blocking SIM-Coldstart. Normale Kontakte werden ohne Warten auf den SIM-Provider veröffentlicht; SIM wird asynchron geladen, gecacht und bei parallelen Verbrauchern per Single-Flight geteilt. Cache und Recents blockieren beim Start nicht auf SIM.

- `0002-capability-based-address-books.patch`: ersetzt die DAVx5-Hardcodierung durch eine provider-neutrale Prüfung des konkreten Kontos. Account-Quellen werden nur gezeigt, wenn Kontakte `getIsSyncable(...) > 0` sind und per Konto automatisch synchronisiert werden. Kalender-only-/deaktivierte Konten bleiben damit draußen. Bei unbekanntem Android-Syncstatus ist ein exakter `ContactsContract.Settings`-/`Groups`-/`RawContacts`-Eintrag nötig. Bekannte Messenger-Spiegel bleiben ausgeschlossen; die `phone_storage`-Label-Heuristik bleibt entfernt.

- `0003-cross-day-contact-call-grouping.patch`: erweitert die optionale Anruflisten-Gruppierung von nur aufeinanderfolgenden Anrufen desselben Tages auf eine durchgehende Gruppierung derselben Rufnummer über die gesamte geladene Historie. Die bestehende SIM-Trennung bleibt erhalten. Im Gruppeneintrag werden bis zu drei unterschiedliche Statusarten (eingehend, ausgehend, verpasst) gleichzeitig mit den vorhandenen farbigen Symbolen angezeigt; der neueste Anruf bleibt der repräsentative Eintrag und die Detailansicht enthält weiterhin alle Einzelanrufe.


Ein alter `0002-nonblocking-sim-cold-start.patch` aus v0.2.3 kann gelöscht werden. Falls er noch im Repository liegt, wird er nicht angewendet, solange er nicht in `patches/series` steht.
