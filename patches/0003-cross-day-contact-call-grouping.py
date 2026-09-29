#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream-phone").resolve()

ADAPTER = ROOT / "app/src/main/kotlin/org/fossify/phone/adapters/RecentCallsAdapter.kt"
RECENTS = ROOT / "app/src/main/kotlin/org/fossify/phone/helpers/RecentsHelper.kt"
LAYOUT = ROOT / "app/src/main/res/layout/item_recent_call.xml"


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing upstream file: {path}")
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, repl: str, label: str, flags: int = 0) -> str:
    new_text, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one regex match, found {count}")
    return new_text


def replace_kotlin_function(text: str, signature_fragment: str, replacement: str, label: str) -> str:
    start = text.find(signature_fragment)
    if start < 0:
        raise SystemExit(f"{label}: function signature not found")
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit(f"{label}: opening brace not found")

    depth = 0
    in_string = False
    escaped = False
    i = brace
    while i < len(text):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    return text[:start] + replacement + text[end:]
        i += 1
    raise SystemExit(f"{label}: matching closing brace not found")


def patch_recents_helper() -> None:
    text = read(RECENTS)

    if ".sortedByDescending { it.startTS }" not in text:
        pattern = r"(?m)^(\s*)\.map \{ it\.copy\(groupedCalls = null\) \}\s*$"
        match = re.search(pattern, text)
        if not match:
            raise SystemExit("RecentsHelper: previous-recents flatten/map anchor not found")
        indent = match.group(1)
        replacement = match.group(0) + f"\n{indent}.sortedByDescending {{ it.startTS }}"
        text = text[:match.start()] + replacement + text[match.end():]

    if "groupCallsByContact(calls = recentCalls)" not in text:
        text = replace_once(
            text,
            "groupSubsequentCalls(calls = recentCalls)",
            "groupCallsByContact(calls = recentCalls)",
            "RecentsHelper callback",
        )

    # Keep the existing same-SIM and real-contact-name safeguards; only the day
    # boundary stops being a grouping criterion.
    if "differentDay" in text:
        text, removed_day = re.subn(
            r"(?m)^\s*val differentDay = callA\.dayCode != callB\.dayCode\s*\n",
            "",
            text,
            count=1,
        )
        if removed_day != 1:
            raise SystemExit("RecentsHelper: day-boundary declaration not found")
        text, changed_condition = re.subn(
            r"differentSim\s*\|\|\s*differentDay\s*\|\|\s*namesAreBothRealAndDifferent",
            "differentSim || namesAreBothRealAndDifferent",
            text,
            count=1,
        )
        if changed_condition != 1:
            raise SystemExit("RecentsHelper: day-boundary condition not found")

    if "private fun groupCallsByContact(calls: List<RecentCall>)" not in text:
        replacement = '''private fun groupCallsByContact(calls: List<RecentCall>): List<RecentCall> {
        val result = mutableListOf<RecentCall>()
        calls.forEach { call ->
            val groupIndex = result.indexOfFirst { groupedCall -> shouldGroupCalls(groupedCall, call) }
            if (groupIndex == -1) {
                result += call
            } else {
                val groupedCall = result[groupIndex]
                val groupedCalls = groupedCall.groupedCalls?.toMutableList() ?: mutableListOf(groupedCall)
                groupedCalls += call
                result[groupIndex] = groupedCall.copy(groupedCalls = groupedCalls)
            }
        }
        return result
    }'''
        text = replace_kotlin_function(
            text,
            "private fun groupSubsequentCalls(calls: List<RecentCall>): List<RecentCall>",
            replacement,
            "RecentsHelper grouping function",
        )

    required = [
        "groupCallsByContact(calls = recentCalls)",
        "private fun groupCallsByContact(calls: List<RecentCall>)",
        ".sortedByDescending { it.startTS }",
        "differentSim || namesAreBothRealAndDifferent",
    ]
    for needle in required:
        if needle not in text:
            raise SystemExit(f"RecentsHelper verification failed: {needle}")
    if "differentDay" in text:
        raise SystemExit("RecentsHelper verification failed: day boundary still participates in grouping")

    write(RECENTS, text)


def patch_adapter() -> None:
    text = read(ADAPTER)

    if "private fun normalizeCallType(type: Int)" not in text:
        marker = "    private inner class RecentCallViewHolder"
        pos = text.find(marker)
        if pos < 0:
            raise SystemExit("RecentCallsAdapter: RecentCallViewHolder anchor not found")
        helpers = '''    private fun normalizeCallType(type: Int) = when (type) {
        Calls.OUTGOING_TYPE -> Calls.OUTGOING_TYPE
        Calls.MISSED_TYPE -> Calls.MISSED_TYPE
        else -> Calls.INCOMING_TYPE
    }

    private fun getCallTypeDrawable(type: Int) = when (normalizeCallType(type)) {
        Calls.OUTGOING_TYPE -> outgoingCallIcon
        Calls.MISSED_TYPE -> incomingMissedCallIcon
        else -> incomingCallIcon
    }

'''
        text = text[:pos] + helpers + text[pos:]

    if "itemRecentsTypeSecondary" not in text:
        pattern = r'''(?ms)^(\s*)val drawable = when \(call\.type\) \{\s*\n\s*Calls\.OUTGOING_TYPE -> outgoingCallIcon\s*\n\s*Calls\.MISSED_TYPE -> incomingMissedCallIcon\s*\n\s*else -> incomingCallIcon\s*\n\s*\}\s*\n\s*itemRecentsType\.setImageDrawable\(drawable\)'''
        match = re.search(pattern, text)
        if not match:
            raise SystemExit("RecentCallsAdapter: single call-type icon block not found")
        indent = match.group(1)
        replacement = f'''{indent}val callTypes = (call.groupedCalls ?: listOf(call))
{indent}    .map {{ normalizeCallType(it.type) }}
{indent}    .distinct()
{indent}    .take(3)
{indent}val callTypeViews = listOf(
{indent}    itemRecentsType,
{indent}    itemRecentsTypeSecondary,
{indent}    itemRecentsTypeTertiary,
{indent})
{indent}callTypeViews.forEachIndexed {{ index, imageView ->
{indent}    val type = callTypes.getOrNull(index)
{indent}    imageView.beVisibleIf(type != null)
{indent}    if (type != null) {{
{indent}        imageView.setImageDrawable(getCallTypeDrawable(type))
{indent}    }}
{indent}}}'''
        text = text[:match.start()] + replacement + text[match.end():]

    new_diff = "oldItem.groupedCalls?.map { it.id to it.type } == newItem.groupedCalls?.map { it.id to it.type }"
    if new_diff not in text:
        text, count = re.subn(
            r"oldItem\.groupedCalls\?\.size\s*==\s*newItem\.groupedCalls\?\.size",
            new_diff,
            text,
            count=1,
        )
        if count != 1:
            raise SystemExit("RecentCallsAdapter: groupedCalls DiffUtil anchor not found")

    for needle in ["itemRecentsTypeSecondary", "itemRecentsTypeTertiary", new_diff]:
        if needle not in text:
            raise SystemExit(f"RecentCallsAdapter verification failed: {needle}")

    write(ADAPTER, text)


def patch_layout() -> None:
    text = read(LAYOUT)

    if "@+id/item_recents_type_secondary" not in text:
        pattern = r'''(?ms)(^[ \t]*<ImageView\b(?:(?!^[ \t]*<).)*?android:id="@\+id/item_recents_type"(?:(?!^[ \t]*<).)*?/>)'''
        match = re.search(pattern, text)
        if not match:
            # Fallback that does not depend on attribute ordering.
            start = text.find("<ImageView")
            target = -1
            while start >= 0:
                end = text.find("/>", start)
                if end < 0:
                    break
                block = text[start:end + 2]
                if 'android:id="@+id/item_recents_type"' in block:
                    target = start
                    match_end = end + 2
                    break
                start = text.find("<ImageView", end + 2)
            if target < 0:
                raise SystemExit("item_recent_call.xml: primary call-type ImageView not found")
            insert_at = match_end
        else:
            insert_at = match.end(1)

        extra = '''

    <ImageView
        android:id="@+id/item_recents_type_secondary"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:layout_marginStart="@dimen/tiny_margin"
        android:padding="@dimen/tiny_margin"
        android:src="@drawable/ic_call_received_vector"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="@+id/item_recents_date_time"
        app:layout_constraintDimensionRatio="1:1"
        app:layout_constraintStart_toEndOf="@+id/item_recents_type"
        app:layout_constraintTop_toTopOf="@id/item_recents_date_time"
        tools:visibility="visible" />

    <ImageView
        android:id="@+id/item_recents_type_tertiary"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:layout_marginStart="@dimen/tiny_margin"
        android:padding="@dimen/tiny_margin"
        android:src="@drawable/ic_call_made_vector"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="@+id/item_recents_date_time"
        app:layout_constraintDimensionRatio="1:1"
        app:layout_constraintStart_toEndOf="@+id/item_recents_type_secondary"
        app:layout_constraintTop_toTopOf="@id/item_recents_date_time"
        tools:visibility="visible" />'''
        text = text[:insert_at] + extra + text[insert_at:]

    old_constraint = 'app:layout_constraintStart_toEndOf="@+id/item_recents_type"'
    new_constraint = 'app:layout_constraintStart_toEndOf="@+id/item_recents_type_tertiary"'
    # There are now two occurrences of old_constraint: the secondary icon and the
    # date TextView. Only replace the one inside the date TextView block.
    date_start = text.find('android:id="@+id/item_recents_date_time"')
    if date_start < 0:
        raise SystemExit("item_recent_call.xml: date TextView not found")
    date_end = text.find("/>", date_start)
    if date_end < 0:
        raise SystemExit("item_recent_call.xml: date TextView closing tag not found")
    date_block = text[date_start:date_end + 2]
    if new_constraint not in date_block:
        if old_constraint not in date_block:
            raise SystemExit("item_recent_call.xml: date start constraint anchor not found")
        date_block = date_block.replace(old_constraint, new_constraint, 1)
        text = text[:date_start] + date_block + text[date_end + 2:]

    for needle in ["@+id/item_recents_type_secondary", "@+id/item_recents_type_tertiary", new_constraint]:
        if needle not in text:
            raise SystemExit(f"item_recent_call.xml verification failed: {needle}")

    write(LAYOUT, text)


def main() -> None:
    patch_recents_helper()
    patch_adapter()
    patch_layout()
    print("Applied structure-aware cross-day call grouping patch")
    print(f"  {RECENTS.relative_to(ROOT)}")
    print(f"  {ADAPTER.relative_to(ROOT)}")
    print(f"  {LAYOUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
