# Patch series

Die aktive Patchreihenfolge steht in `patches/series`. Der GitHub-Actions-Workflow wendet ausschließlich die dort aufgeführten Dateien an.

- `0001-device-davx-sim-filter.patch`: Geräte-/DAVx5-/SIM-Filter plus non-blocking SIM-Coldstart. Normale Kontakte werden ohne Warten auf den SIM-Provider veröffentlicht; SIM wird asynchron geladen, gecacht und bei parallelen Verbrauchern per Single-Flight geteilt. Cache und Recents blockieren beim Start nicht auf SIM.

Ein alter `0002-nonblocking-sim-cold-start.patch` aus v0.2.3 kann gelöscht werden. Falls er noch im Repository liegt, wird er nicht angewendet, solange er nicht in `patches/series` steht.
