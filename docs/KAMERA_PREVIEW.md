# Samsung-Kamera: Vorschau auf Google Fotos umleiten, ohne Root

Nachgewiesener Aufruf beim Tippen auf die Samsung-Kamera-Miniatur:

```
act=android.intent.action.QUICK_VIEW
cmp=com.sec.android.gallery3d/com.samsung.android.gallery.app.activity.external.ImageQuickViewActivity
result code=-92
```

Da die Kamera eine **explizite** Component adressiert, kann Android die
Standard-App für Bilder oder ein `VIEW`-Intent-Filter von Google Fotos nicht
als Ersatz verwenden. Ein fremdes Paket mit `com.sec.android.gallery3d`
würde außerdem an der Signatur-/Systempaketbindung scheitern.

- **Logcat-Auslöser**: funktioniert zeitweise, ist aber nach dem Booten wegen
  der Android-Logzugriffsbestätigung nicht zuverlässig.
- **MacroDroid-Schwebebutton**: verhindert den eigentlichen Kamera-Klick und
  damit den Fehlertoast. Ein start-/geschlossen-Trigger per Accessibility
  hat auf dem S25 merkliche Verzögerung und kann beim Booten ausfallen;
  feste Bildschirmkoordinaten stimmen nach Rotation nicht mehr.
- **Shortcuts/Quick-Settings-Kachel mit Voraktivierung**: startet erst das
  Overlay, danach die Kamera; zuverlässig nur für Startwege über diese Kachel
  oder Verknüpfung, nicht für Sperrbildschirm/Seitentaste.
- **Eigener AccessibilityService + TYPE_ACCESSIBILITY_OVERLAY**: mögliche
  Entwicklungsrichtung; würde Kamera-Fensterereignisse selbst auswerten,
  Overlayzustand und Bildschirmausrichtung automatisch aktualisieren.
  Ein schnelleres oder fehlerfreies Funktionieren auf One UI 9 ist **noch
  nicht getestet** und kann nicht versprochen werden. Auch dafür ist eine
  zusätzliche App mit Bedienungshilfe- und Overlay-Rechten nötig.

Das Original der Samsung-Galerie-Activity ist ohne Root, passende
Samsung-Signatur oder modifizierte Kamera nicht transparent durch Google Fotos
ersetzbar. Dieser Teil ist unabhängig vom Fossify-Phone-Patch.
