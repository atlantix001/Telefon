# Fossify Phone contact-source filter preflight v0.1.0

Source-only preflight for a Fossify Phone customization matching the already tested Fossify Contacts filter.

## Target behavior

The final regular replacement app should expose contacts only from:

- real device/phone storage visible through Android ContactsProvider;
- DAVx5 address-book accounts (`at.bitfire.davdroid.address_book`);
- real SIM contact accounts.

It should hide contacts from Google, Samsung, ordinary DAVx5 main accounts, Fossify private storage, messenger/app accounts and all other unrelated Android contact accounts. No Android accounts or contacts are deleted; the filter only changes what Fossify Phone resolves/displays.

The final app will use the regular package ID `org.fossify.phone` and a fixed custom signing key, so the official Fossify Phone app must be uninstalled once before the first custom install. Later custom versions can update in place with the same key.

## Pinned upstream

- FossifyOrg/Phone `1.11.1`
- exact commit `7de52a31a4d3cfc53e6cbc298a17ffca4e69141e`

The preflight does **not** compile an APK. It only fetches the exact pinned source and creates a compact snapshot plus an inventory of contact-resolution code. This lets the real filter patch be based on the exact Phone 1.11.1 implementation rather than guesses.

## Run

Run the `Fossify Phone source snapshot` workflow manually in GitHub Actions, download the artifact `Fossify-Phone-source-snapshot-1.11.1`, and provide that ZIP for the patch/build step.

No signing key is created or used in this preflight.
