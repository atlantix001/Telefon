#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-upstream-phone}"
OUT="${2:-Fossify-Phone-source-snapshot-1.11.1}"

rm -rf "$OUT"
mkdir -p "$OUT/upstream"

copy_if_exists() {
  local src="$1"
  local dst="$OUT/upstream/$1"
  if [[ -e "$SRC/$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    cp -a "$SRC/$src" "$dst"
  fi
}

# Exact app code/resources and build metadata.
copy_if_exists app/src/main
copy_if_exists app/build.gradle.kts
copy_if_exists build.gradle.kts
copy_if_exists settings.gradle.kts
copy_if_exists gradle.properties
copy_if_exists gradle/libs.versions.toml
copy_if_exists gradle/wrapper/gradle-wrapper.properties
copy_if_exists .fossify/release-marker.txt
copy_if_exists CHANGELOG.md
copy_if_exists LICENSE
copy_if_exists README.md

# Inventory focused on every place where Phone resolves or displays contacts.
{
  echo "Pinned Fossify Phone contact-source inventory"
  echo "Generated from: $(git -C "$SRC" rev-parse HEAD)"
  echo
  grep -RInE \
    'ContactSource|contact.?source|ContactsHelper|contactsHelper|getContacts|loadContacts|RawContacts|ContactsContract|ACCOUNT_(TYPE|NAME)|account(Type|Name)|private contacts|private_contacts|SMT_PRIVATE|favorites|speed.?dial|caller|contactId|phonebook' \
    "$SRC/app/src/main/kotlin" "$SRC/app/src/main/res" 2>/dev/null || true
} > "$OUT/contact-source-inventory.txt"

find "$OUT/upstream" -type f | sort > "$OUT/source-files.txt"

cat > "$OUT/PIN.txt" <<PIN
Repository: https://github.com/FossifyOrg/Phone.git
Tag: 1.11.1
Commit: $(git -C "$SRC" rev-parse HEAD)
PIN

zip -qr "$OUT.zip" "$OUT"
sha256sum "$OUT.zip" | tee "$OUT.zip.sha256"
