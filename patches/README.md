# Patches

Patches are applied in lexical order to the pinned Fossify Phone 1.11.1 source tree.

- `0001-device-davx-sim-filter.patch`: device/DAVx5 allow-list plus direct Android `SimPhonebookContract` support for the Phone UI, Dialpad, source filter and call/name resolution.
- `0002-nonblocking-sim-cold-start.patch`: ports the Contacts cold-start strategy to Phone. Normal source/contact loading runs in parallel, normal contacts publish without waiting for SIM, SIM source visibility uses a cache, concurrent startup consumers share one asynchronous SIM read, and startup cache/recents paths use cached SIM data instead of synchronously blocking, and Recents is refreshed once after the SIM warm-up completes.

The regular build keeps package id `org.fossify.phone` and uses the fixed custom signing key in `signing/`.
