#!/usr/bin/env python3
"""Fossify Phone 1.11.1: replace button-style settings with native-style rows.

TelephonyUI 18.1.00 / One UI 9: the exported CallSettingsActivity reads Intent
string extra `root_key` and resolves it via `CallSettingsActivityUtil`.
Keys obtained from five user-recorded fragment-navigation logs.

The external launches still require on-device verification. No privileged
permissions, reflection, or non-exported activities are used.
"""
from pathlib import Path
import sys

upstream = Path(sys.argv[1] if len(sys.argv) > 1 else 'upstream-phone').resolve()
target = upstream / 'app/src/main/kotlin/org/fossify/phone/activities/MinimalCallSettingsActivity.kt'
if not target.exists():
    raise SystemExit('Apply patch 0005 before 0006; missing MinimalCallSettingsActivity')

new_source = '''package org.fossify.phone.activities

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.telecom.TelecomManager
import android.util.TypedValue
import android.view.Gravity
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

/**
 * Minimal phone settings with normal, theme-aware preference-like rows.
 * TelephonyUI root_key handling verified in the Samsung APK, while the
 * individual external deep links must still be confirmed on the device.
 */
class MinimalCallSettingsActivity : Activity() {

    private fun dp(value: Int): Int =
        (value * resources.displayMetrics.density + 0.5f).toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "Telefon- und Netzeinstellungen"

        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, dp(8), 0, dp(12))
        }

        fun addRow(label: String, onClick: () -> Unit) {
            val row = TextView(this).apply {
                text = label
                textSize = 16f
                gravity = Gravity.CENTER_VERTICAL
                minHeight = dp(56)
                setPadding(dp(20), dp(10), dp(20), dp(10))
                isClickable = true
                isFocusable = true
                val textColor = TypedValue()
                if (theme.resolveAttribute(android.R.attr.textColorPrimary, textColor, true)) {
                    if (textColor.resourceId != 0) {
                        setTextColor(resources.getColorStateList(textColor.resourceId, theme))
                    } else {
                        setTextColor(textColor.data)
                    }
                }
                val ripple = TypedValue()
                if (theme.resolveAttribute(android.R.attr.selectableItemBackground, ripple, true)
                    && ripple.resourceId != 0) {
                    setBackgroundResource(ripple.resourceId)
                }
                setOnClickListener { onClick() }
            }
            column.addView(row, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            ))
        }

        addRow("Nummern sperren") {
            val telecom = getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            val intent = telecom?.createManageBlockedNumbersIntent()
            if (intent != null) launchSafely(intent) else showUnavailable()
        }
        addRow("Anruferinnerungen und Klingelton") {
            openSamsungPage("CALL_ALERTS_AND_RINGTONES")
        }
        addRow("Anrufe beantworten und beenden") {
            openSamsungPage("ANSWERING_AND_ENDING_CALLS")
        }
        addRow("WLAN-Anrufe") {
            launchSafely(Intent("android.settings.WIFI_CALLING_SETTINGS"))
        }
        addRow("Zusatzdienste") {
            openSamsungPage("SUPPLEMENTARY_SERVICE_COMMON")
        }
        addRow("Andere Anrufeinstellungen") {
            openSamsungPage("OTHER_CALL_SETTINGS")
        }
        addRow("Alle Samsung-Anrufeinstellungen") {
            openSamsungPage(null)
        }

        setContentView(ScrollView(this).apply {
            setFillViewport(true)
            addView(column)
        })
    }

    private fun openSamsungPage(rootKey: String?) {
        val intent = Intent("com.samsung.android.app.telephonyui.action.OPEN_CALL_SETTINGS")
            .setClassName(
                "com.samsung.android.app.telephonyui",
                "com.samsung.android.app.telephonyui.callsettings.ui.preference.CallSettingsActivity"
            )
        if (rootKey != null) intent.putExtra("root_key", rootKey)
        launchSafely(intent)
    }

    private fun showUnavailable() {
        Toast.makeText(this, "Einstellung auf diesem Gerät nicht verfügbar", Toast.LENGTH_LONG).show()
    }

    private fun launchSafely(intent: Intent) {
        try {
            startActivity(intent)
        } catch (_: android.content.ActivityNotFoundException) {
            showUnavailable()
        } catch (_: SecurityException) {
            showUnavailable()
        }
    }
}
'''

current = target.read_text('utf-8')
if current == new_source:
    print('Already applied patch 0006')
    sys.exit(0)
if ('class MinimalCallSettingsActivity : Activity()' not in current
    or 'fun addExplanation(msg: String)' not in current
    or 'addAction("Weitere Samsung-Anrufeinstellungen"' not in current):
    raise SystemExit('Unexpected pre-0006 settings screen; refusing overwrite')
target.write_text(new_source, encoding='utf-8')
print('Applied patch 0006: theme-aware single-line rows and Samsung root_key links')
