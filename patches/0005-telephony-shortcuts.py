#!/usr/bin/env python3
"""Add a guarded system-call-settings bridge to Fossify Phone 1.11.1.

Applies after 0004. Avoids private/non-exported Samsung Preference fragments.
The two direct actions are supported Android entry points, while other Samsung
settings remain accessible through the exported Samsung CallSettingsActivity.
"""
from pathlib import Path
import sys

upstream = Path(sys.argv[1] if len(sys.argv) > 1 else 'upstream-phone').resolve()
settings = upstream / 'app/src/main/kotlin/org/fossify/phone/activities/SettingsActivity.kt'
manifest = upstream / 'app/src/main/AndroidManifest.xml'
new_activity = upstream / 'app/src/main/kotlin/org/fossify/phone/activities/MinimalCallSettingsActivity.kt'

if not settings.exists() or not manifest.exists():
    raise SystemExit('Pinned Fossify Phone 1.11.1 source structure missing; refusing patch')

text = settings.read_text('utf-8')
anchor = 'removeItem(R.id.calling_accounts) // Hide old Android call-accounts entry; leave telecom configuration untouched.'
if text.count(anchor) != 1 and 'MinimalCallSettingsActivity::class.java' not in text:
    raise SystemExit('Expected exactly one patch 0004 menu anchor; refusing to modify another version')

menu_code = '''removeItem(R.id.calling_accounts) // Hide old Android call-accounts entry; leave telecom configuration untouched.
            // Custom minimal settings bridge. This code runs in the existing Menu receiver.
            // Use a private ID to avoid interfering with Fossify's resource IDs.
            if (findItem(0x53435011) == null) {
                add(0, 0x53435011, 999, "Telefon- und Netzeinstellungen").apply {
                    setShowAsAction(android.view.MenuItem.SHOW_AS_ACTION_NEVER)
                    setOnMenuItemClickListener {
                        startActivity(android.content.Intent(this@SettingsActivity, MinimalCallSettingsActivity::class.java))
                        true
                    }
                }
            }'''
if 'MinimalCallSettingsActivity::class.java' not in text:
    text = text.replace(anchor, menu_code, 1)
    settings.write_text(text, 'utf-8')

app_manifest = manifest.read_text('utf-8')
entry = '''        <!-- Private shortcut screen: no new exported components or permissions. -->
        <activity
            android:name=".activities.MinimalCallSettingsActivity"
            android:exported="false"
            android:label="Telefon- und Netzeinstellungen" />
'''
if 'MinimalCallSettingsActivity' not in app_manifest:
    if app_manifest.count('</application>') != 1:
        raise SystemExit('Application manifest closing tag unexpected; refusing patch')
    app_manifest = app_manifest.replace('</application>', entry + '    </application>', 1)
    manifest.write_text(app_manifest, 'utf-8')

source = r'''package org.fossify.phone.activities

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.telecom.TelecomManager
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

/** Minimal, private bridge to public system settings; no priv-app or signature APIs. */
class MinimalCallSettingsActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "Telefon- und Netzeinstellungen"
        val density = resources.displayMetrics.density
        fun dp(n: Int) = (density * n + 0.5f).toInt()

        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(14), dp(16), dp(20))
        }
        val header = TextView(this).apply {
            text = "Telefon- und Netzeinstellungen"
            textSize = 23f
            setPadding(0, dp(8), 0, dp(12))
        }
        column.addView(header)
        fun addExplanation(msg: String) {
            column.addView(TextView(this).apply {
                text = msg
                textSize = 14f
                setPadding(0, dp(4), 0, dp(13))
            })
        }
        fun addAction(name: String, description: String, action: () -> Unit) {
            column.addView(Button(this).apply {
                text = name
                isAllCaps = false
                setOnClickListener { action() }
            }, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
            addExplanation(description)
        }

        addAction("Nummern sperren", "Android-Telecom-Sperrliste; kann sich von Samsung-Sonderfunktionen unterscheiden.") {
            val telecom = getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            val intent = telecom?.createManageBlockedNumbersIntent()
            if (intent != null) launchSafely(intent) else showUnavailable()
        }
        addAction("WLAN-Anrufe", "Öffnet die vom Gerät bereitgestellte WLAN-Telefonie-Einstellung, sofern verfügbar.") {
            launchSafely(Intent("android.settings.WIFI_CALLING_SETTINGS"))
        }
        addAction("Weitere Samsung-Anrufeinstellungen", "Anruferinnerungen und Klingelton; Anrufe beantworten und beenden; Zusatzdienste (Rufumleitung, Anklopfen, Rufnummernanzeige); andere Anrufeinstellungen. Die Unterseiten sind nicht als separat exportierte Activities nachgewiesen.") {
            launchSafely(Intent("com.samsung.android.app.telephonyui.action.OPEN_CALL_SETTINGS").setClassName(
                "com.samsung.android.app.telephonyui",
                "com.samsung.android.app.telephonyui.callsettings.ui.preference.CallSettingsActivity"
            ))
        }
        addExplanation("Nur sichtbar sind Optionen, die dein Gerät und der Netzbetreiber unterstützen. Samsung TelephonyUI muss für die Samsung-Anrufeinstellungen installiert bleiben. Samsung-Dialer-spezifische Anzeige- und Ablehnoptionen sind bewusst nicht verlinkt.")
        setContentView(ScrollView(this).apply { addView(column) })
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
if new_activity.exists() and new_activity.read_text('utf-8') != source:
    raise SystemExit('Custom settings activity already exists with different contents; refusing overwrite')
new_activity.parent.mkdir(parents=True, exist_ok=True)
new_activity.write_text(source, 'utf-8')
print('Applied guarded minimal call settings bridge (three entries, no privileged APIs)')
