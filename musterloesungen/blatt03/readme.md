Uni Osnabrück, Web-Technologien 2018

Übungsblatt 3
=============


ACHTUNG: Ggf. aktualisierte Fassungen des Aufgabentextes finden Sie nur in Stud.IP.
 


Aufgabe 1 (25 Punkte): Sicherheitslücken in "Buggy MiniTwitter"
---------------------------------------------------------------

Im Aufgabenordner befindet sich eine Anwendung namens "MiniTwitter", die es Nutzern erlaubt, kurze Nachrichten 
abzusenden, die dann allen Nutzern angezeigt werden. 

Es gibt folgende Features:
- Jeder darf Nachrichten lesen.
- Nur angemeldete Nutzer dürfen Nachrichten schreiben. 
- Es gibt normale Nutzer und Admins.
- Admins haben zusätzlich Zugriff auf eine Usermanagement-App.
- In der Usermanagement-App werden alle Nutzer angezeigt. Sie können gelöscht 
  und neue Nutzer angelegt werden.
- Die Nutzerdaten sind in einer SQL-Datenbank abgelegt. (Die Passwörter werden ungehasht 
  und ohne Salt gespeichert, diesen Fehler müssen Sie nicht melden oder beheben.)
- Die Minitwitter-Daten sind in einer Datei abgelegt.

Untersuchen Sie die MiniTwitter-Anwendung auf die in der Vorlesung vorgestellten (und ggf. weitere) Sicherheitslücken. 
Gesucht werden dabei lediglich Sicherheitslücken, die in der Anwendung bzw. dem Servercode selbst liegen. Allgemeinere 
Probleme wie der Schutz gegen Denial-of-Service-Angriffe etc. sind nicht gemeint. 

Finden Sie (mindestens) 5 Sicherheitsproblemem die zu mindestens drei verschiedenen Typen gehören (d.h. es reicht nicht,
5 verschiedene XSS-Lücken zu finden), die Sie in der Datei bugs.txt dokumentieren und jeweils wie folgt angehen:

1. Bennung und Kurzbeschreibung der Sicherheitslücke anhand der in der Vorlesung vorgestellten Kategorien
2. Im Testat müssen Sie die Lücke demonstrieren. Halten Sie also eine nicht modifizierte Kopie des Codes bereit.
3. Beseitigung der Lücke. CSRF-Lücken dürfen hier genannt werden und können dann durch Aufgabe 2 beseitigt werdem.


Aufgabe 2 (25 Punkte): Datenbank-Model für Tweets
-------------------------------------------------

Verlegen Sie die Datenhaltung für die Tweets in die Datenbank. Beachten Sie dabei:
1. Implementieren Sie eigene Model-Klassen. Sie können sich dabei an server/usermodel.py orientieren.
2. Wenn Sie den Kurs "Datenbanksysteme" noch nicht belegt haben, reicht es aus, die derzeit in data/minitwitter.data
   abgelegten Informationen in der Datenbank abzubilden. (Ansonsten verknüpfen Sie die Autrenangabe eines Tweets
   in korrekter Weise mit der users-Tabelle.)
3. Schreiben Sie Test-Code für das Tweets-Model.
4. Stellen Sie alle Zugriffe auf die Tweets-Daten in der MiniTwitterApp (minitwitter.py) auf die Model-Klassen um.


Aufgabe 3 (25 Punkte): AJAXifizierung
------------------------------------

Stellen Sie die Anwendung an mindestens drei sinnvollen Stellen auf AJAX-Requests um. Verwenden Sie dazu reines Javascript,
keine Javascript-Bibliotheken. 

Unter AJAXifizierung ist zu verstehen:
1. Anstelle eines normalen Browser-Requests wird für eine Aktion oder ein Ereignis per Javascript ein XmlHttpRequest erzeugt.
2. Der Server verarbeitet diesen Request und liefert partiellen HTML-Code oder JSON-Daten zurück.
3. Der Client aktualisiert per Javascript den aktuellen DOM-Tree durch Einfügen/Ersetzen anhand des zurückgelieferten 
   HTML-Fragmentes oder durch Verarbeitung der JSON-Antwort.
   
Hinweise:
- Sie sollen keine clientseitigen Templates verwenden, sondern tatsächlich im Wesentlichen server-generiertes HTML einfügen
- Eine JSON-Antwort (oder auch nur ein geeigneter Status-Code) eignen sich besonders dann, wenn nur die Information
  benötigt wird, ob eine Aktion erfolgreich war.
- Auch eine automatische Aktualisierung der Beitragsliste nach einer voreingestellten Zeit wäre sinnvoll.


Aufgabe 4 (25 Punkte): CSRF-Middleware
-------------------------------------

Implementieren Sie für die in Aufgabe 2 und 3 erweiterte Anwendung eine CSRF-Middleware zur systematischen Schließung 
von CSRF-Lücken. Der Schutz soll mithilfe von CSRF-Token funktionieren, die bei der Entgegennahme jedes POST-Requests 
geprüft werden. 
 
Um vor CSRF-Lücken geschützt zu sein, muss eine Anwendung folgendes tun:

1. Die CSRF-Middleware aktivieren.
2. Alle zu schützenden Aktionen auf POST umstellen.
3. Mit jedem POST-Formular/mit jedem POST-Request ein gültiges CSRF-Token übermitteln.

Ihre gesamte Implementation gehört in eine gesonderte Datei `server/middlewares/csrf.py`, Sie sollten den Code des
sonstigen Webservers nicht verändern. Eine Ausnahme ist die Art und Weise, wie die Template-Engine Zugriff auf die 
CSRF-Token bekommt. Sie können entweder an jeder Stelle in nutzenden Apps das Token mit übergeben, oder (empfohlen!)
in der Methode `response#send_template` das Dictionary vor Übergabe an die Templating-Engine erweitern. Diese 
Erweiterung soll aber allgemeingültig sein und nicht speziell auf die CSRF-Middleware zugeschnitten sein, d.h.
Sie könnten z.B. das server-, request-, session- oder response-Objekt immer in das Template-Dictionary aufnehmen. 

Um ggf. AJAX-Requests um das CSRF-Token erweitern zu können, benötigen Sie Zugriff auf die Tokens in Javascript. Das ist 
auf verschiedenste Weise möglich, z.B. indem Sie den Javascript-Code ebenfalls als Template realisieren oder - das 
erscheint zunächt unsinnig - das CSRF-Token in ein Cookie speichern, das der Javascript-Code auslesen kann. (Überlegen 
Sie: Warum und unter welchen Bedingungen ist die CSRF-Token-Übermittlung per Cookie sicher?)
