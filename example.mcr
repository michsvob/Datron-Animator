_libmakros auf_ab -1, Pumpsel -1, ponoff_2kopf -1, spuelen -1, dispon -1, dispoff -1, oadmGetValue -1;

_sprache 0;

Dimension 1;

Variable Wt, Vs, Zf, Zs, Z0, Zd, A, B, Menge, Pd, Teilnichtda, Abstand, Kartuscheleer, 
     Amax, Ax, Ay, Anx, Any, Amaxr, Araupe, Anxr, Anyr, Nochmalspuelen, Abfrage, 
     Teilda, Aufloesung, Zeitbispause, Grenzwert, Zd2, Zdstart, Mengestart, Typ, 
     Postsz, Postsy, Postsx, Possafez, My1, My2, Mx1, Mx2, Ndx, Nkx, Ndy, Nmy, Nmx, 
     Nky, Npz, Lightoffsetz, Sollx, Solly, Currx, Curry, Currz, Movex, Movey, Movez, 
     Lighty, Lightx, Startlight, Endlight, Checkvalue, Currmkoor, Currzeromem, Nadelx, 
     Nadely, Zhkx, Zhky, Tisch2x, Tisch2y, Zhkz, Lightxpos, Lightypos, Currzcorr, 
     Z, Unitsconst, No_value, Text1, V_mseerkennung, Val, Wt_hoehe, Value, Obere_grenze, 
     Untere_grenze, Durchlauf, Wt_hoehe0, V_druckbehaelter, Wt0, Var_spuelen,      V_spuelen,n_teile_vorne,n_teile_mitte,n_teile_hinten,
     Y_start_hinten,Y_start_vorne,Y_start_mitte,X_start;
     

(
  Amax = 30;!Maximale Anzahl an Teilen pro Träger!
  Ax = 30;!Abstand der Teile zueinander auf Träger in X-Richtung!
  Ay = 40;!Abstand der Teile zueinander auf Träger in Y-Richtung!
  Anx = 10;!Anzahl der Spalten!
  Any = 3;!Anzahl der Reihen!
  Wt_hoehe = 49.7;!Soll-Höhe des WT!
  Teilnichtda = 0;
  ; !---------------------------------------------------------------!
  Amaxr = Amax;
  Anxr = Anx;
  Anyr = 0;
  ; !---------------------------------------------------------------!
  Auf_ab 0;!Schlitten auf!
  Relsp 1;
  Mkoord 5, 0;!Koordinatensystem Laser!
  Axyz 1, -280, -50, Zp, 0, 0;!WT-Höhenposition X - Y!
  Axyz 1, Xp, Yp, -6.3, 0, 0;!WT-Höhenposition!
  Submakro Abstandsanzeige;
  Axyz 1, Xp, Yp, 1.41, 0, 0;!Z - erste Position!
  Axyz 1, -260, -80, Zp, 0, 0;!erste Position vorne links-letztes Teil vom Bonden!
  ; !---------------------------------------------------------------!
  Markierung 5;
  ; !Verweile 2, 1, 0, 0, 0, 0, 0;!
  Einaus 1, 150, Teilnichtda, 5, 0, 1;!Wenn kein Teil da ist, ist "Teilnichtda"=1!
  Bedingung Teilnichtda, 0, 1, 10, 200;
  ; !---------------------------------------------------------------!
  Markierung 10;
  Bedingung Anxr, 0, 1, 40, 0;!in der letzten Zeile nicht mehr nach rechts möglich!
  Anxr = Anxr - 1;
  Ixyz 1, Ax, 0, 0, 0, 0;
  Einaus 1, 150, Teilnichtda, 5, 0, 1;
  Bedingung Teilnichtda, 0, 1, 10, 30;
  ; !----------------------------------------------------------------!
  Markierung 30;
  Ixyz 1, -Ax, 0, 0, 0, 0;
  Anxr = Anxr + 1;
  ; !----------------------------------------------------------------!
  Markierung 40;
  Anyr = Anyr + 1;
  Bedingung Anyr, 0, Any, 200, 0;!in der letzten Reihe nicht mehr nach hinten möglich!
  Ixyz 1, 0, Ay, 0, 0, 0;
  Einaus 1, 150, Teilnichtda, 5, 0, 1;
  Bedingung Teilnichtda, 0, 1, 40, 200;
  ; !---------------------------------------------------------------!
  Markierung 200;!wenn Teil gefunden hier hin springen!
  Amaxr = ( Anxr * Any ) - Anyr;
  Amax = Amaxr;
) Teileerkennung;
(
  ; !-----------------Kartuschenwechsel------------------!
  Auf_ab 0;
  Mkoord 1, 0;!Nadelversatz Tisch1!
  Position 11, 0;!Kartuschenwechselposition!
  Auf_ab 1;
  Einaus 0, 200, 0, 1, 0, 1;!Datron nicht aktiv!
  Einaus 0, 200, 0, 2, 0, 1;!Datron nicht fertig!
  Einaus 0, 200, 0, 3, 0, 1;!Datron nicht betriebsbereit!
  Einaus 0, 200, 1, 8, 0, 1;!gelb an!
  Text 1 = "Bitte bestätigen wenn Kartusche gewechselt wurde";
  Melde 1, 0, 0, 0;
  Auf_ab 0;
  ; !Ixyz 1, -98, 478, 25, 0, 0;!
  ; !Submakro Nmess_kartuschenwechsel; noch nicht möglich!
  Position 10, 0;
  Ixyz 1, 0, 0, 50, 0, 0;
  ; !Ixyz 1, 0, -40, -50, 0, 0;!
  Auf_ab 1;
  Spuelen 20, 10, 0, 1, 1;
  Spuelen 5, 4, 0, 1, 1;
  Markierung 1;
  Submakro Nochmalspuelen_rechts 1, 0;
  Bedingung Nochmalspuelen, 0, 1, 1, 0;
  Markierung 20;
  Auf_ab 0;
  Verweile 1, 1, 0, 0, 0, 0, 0;
  ; !Ixyz 1, 0, 15, 0, 0, 0;!
  ; !Ixyz 1, 0, -5, 50, 0, 0;!
  Einaus 0, 200, 1, 3, 0, 1;!Datron betriebsbereit!
  Einaus 0, 200, 0, 8, 0, 1;!gelb aus!
) Kartuschenwechsel_rechts;
(
  Markierung 1;
  Bedingung Nochmalspuelen, 0, 1, 0, 10;
  Spuelen 20, 3, 0, 1, 1;
  Spuelen 5, 4, 0, 1, 1;
  Markierung 10;
) Nochmalspuelen_rechts;

(
  ; !Kontur1!
  Wt = 0.1;!Wartezeit!
  Vs = 3;
  Z0 = - 14.5;!Materialoberflaeche!
  Zd = Z0 + 0.7;!Dispense-ebene!
  Zs = Zd + 3.0;!Sicherheitsebene!
  ; !Menge = 1.0;Dosiervolumen; 100mg!
  ; !Menge = 0.7;Dosiervolumen; 50mg_ON-->3_Off-->2!
  ; !Menge = 0.8;Dosiervolumen; 55mg_ON-->3_Off-->3!
  ; !Menge = 0.9;Dosiervolumen; 65mg_ON-->3_Off-->4!
  ; !Menge = 0.85;Dosiervolumen; 75mg_ON-->3_Off-->5!
  Menge = 0.85;!Dosiervolumen; 65mg_ON-->3_Off-->5!
  A = 75.0;!AFaktor zum Ausgleich des Beschleunigungsfehlers!
  B = 10.0;!BFaktor zum Ausgleich von Geschwindigkeitsfehlern!
  Pd = 0.0;!Pumpendrehrichtung!
  Ponoff_2kopf 1, 1;
  Dispon 3, 180, 1, 1, Z0, Vs, Vs, Menge, A, B, Zd, Zs, Pd;
  ; !Ixyz 0, 10, 0, 0, 0, 0;!
  ; !Kreis 2, 0, 0, 0, 270, 90, 0, 0, 2, 1, 0;1 Z sollte um 1mm rauf gehen!
  ; !Ixyz 0, -12, 0, 0, 0, 0;!
  Ixyz 0, 10.5, 0, 0, 0, 0;
  Kreis 3.5, 0, 0, 0, 270, 90, 0, 0, 2, 1, 0;!1 Z sollte um 1mm rauf gehen!
  Ixyz 0, -8, 0, 0, 0, 0;
  Ixyz 0, 0, -3, 0, 0, 0;
  Ponoff_2kopf 0, 1;
  Dispoff 5, 180, 0.75, 0, Vs, 8, 0.5, Vs, Zs, Wt;!Z-Offset von 0,1 auf 0,5!
  ; !Submakro Rueckzug_rechter_kopf;!
  ; !Kontur1!
) Abdeckraupe;
(
  Bedingung V_mseerkennung, 0, 1, 100, 0;
  Teilnichtda = 0;
  ; !---------------------------------------------------------------!
  Relsp 1;
  Position 9, 0;
  ; !---------------------------------------------------------------!
  Markierung 5;
  Einaus 1, 150, Teilnichtda, 5, 0, 1;!Wenn kein Teil da ist, ist "Teilnichtda"=1!
  Bedingung Teilnichtda, 0, 1, 100, 50;
  ; !---------------------------------------------------------------!
  Markierung 50;!wenn Teil gefunden hier hin springen!
  Position 12, 0;
  Text 3 = "";
  Text 3 = "M wurde erkannt-->falsches Programm geladen!";
  Schreibe 3, 0;
  Melde 3, 0, 0, 0;
  ; !Text 1 = "";!
  ; !Text 1 =  ? ;!
  Abbruch;
  ; !---------------------------------------------------------------!
  Markierung 100;!wenn kein Teil gefunden hier hin springen!
  ; !V_mseerkennung = 1;!
) Mseerkennung;
(
  ; !--------- Rückzug bei UV-Verguss ------------------------------!
  Dispon 2, 0, 0.5, 1, Zp, 1, 1, 2.5, 75, 10, Zp, Zp, 1;
  ; !Dispon 2, 0, 0.5, 0.4, Zp, 1, 1, 1.5, 75, 10, Zp, Zp, 1;!
  Dispoff 2, 0, 0, 0, 1, 0, 0.1, 1, Zp, 0;
) Rueckzug_rechter_kopf;
(
  Durchlauf = 0;
  Untere_grenze = Wt_hoehe - 0.5;
  Obere_grenze = Wt_hoehe + 0.5;
  Markierung 10;
  Value = 0;
  Oadmgetvalue Value;
  Verweile 0.5, 1, 0, 0, 0, 0, 0;
  Oadmgetvalue Value;
  ; !Value = ?;!
  ; !Bedingung Value, 1, 1, 0, 10;bei 30 Messfehler des Lasers!
  Abstand = Value * 20 / 2000 + 30;
  Bedingung Abstand, 0, 30, 50, 0;!bei 30 Messfehler des Lasers!
  String 1, Abstand, 3, 10, 3, 0;
  Schreibe 3, 0;
  Bedingung Abstand, 1, Obere_grenze, 50, 0;
  Bedingung Untere_grenze, 1, Abstand, 50, 100;
  ; !---------------------------------------------------------------!
  Markierung 50;!wenn Abstand falsch!
  Ixyz 1, 0.2, -0.2, 0, 0, 0;
  Ixyz 1, 0, 0, 5, 0, 0;
  Ixyz 1, 0, 0, -5, 0, 0;
  Durchlauf = Durchlauf + 1;
  Bedingung Durchlauf, 0, 10, 0, 10;
  Text 3 = "";
  Text 3 = "Bitte Bewerten: 	Alles in Ordnung --> <OK>	/\	Falscher WT/falsches Programm --> <Abbruch>";
  ; !Schreibe 3, 0;!
  Melde 3, 0, 0, 0;
  ; !Abbruch;!
  ; !---------------------------------------------------------------!
  ; !String 1, Abstand, 3, 10, 3, 0;!
  ; !Schreibe 3, 0;!
  Markierung 100;!wenn Abstand in Toleranz!
) Abstandsanzeige;
(
  Verweile 0, 1, 0, 150, 2, 0, 0;!Pause!
  V_spuelen = 0;
  Auf_ab 0;
  Position 10, 0;
  Ponoff_2kopf 1, 1;
  Spuelen 20, 2, 0, 1, 1;
  Spuelen 5, 4, 0, 1, 1;
  Markierung 100;
  Ponoff_2kopf 0, 1;
  Auf_ab 0;
  Verweile 1, 1, 0, 0, 0, 0, 0;
) Pause_rechts;
(
  ; !-----------------Spülen------------------!
  V_spuelen = V_spuelen + 1;
  Bedingung V_spuelen, 0, 4, 0, 100;
  V_spuelen = 1;
  Auf_ab 0;
  Position 10, 0;
  Ponoff_2kopf 1, 1;
  Spuelen 20, 3, 0, 1, 1;
  Spuelen 5, 4, 0, 1, 1;
  Markierung 100;
  Ponoff_2kopf 0, 1;
  Auf_ab 0;
  Verweile 1, 1, 0, 0, 0, 0, 0;
) Spuelen_rechts;
(
  Axyz 1, X_start, Y_start_hinten, -5, 0, 0;
  X_start=X_start + Ax;
  Relsp 2;
  Setrel 8, 6, -5;
  Submakro Abdeckraupe;
  Relsp 1;
) Bauteil_hinten;
(
  X_start=X_start - Ax;
  Axyz 1, X_start, Y_start_mitte, -5, 0, 0;  
  Relsp 2;
  Setrel 8, -36, -5;
  Submakro Abdeckraupe;
  Relsp 1;
) Bauteil_mitte;
(
  X_start=X_start + Ax;
  Axyz 1, X_start, Y_start_vorne, -5, 0, 0;  
  Relsp 2;
  Setrel 8, -76, -5;
  Submakro Abdeckraupe;
  Relsp 1;
) Bauteil_vorne;

Auf_ab 0;
Mkoord 1, 0;
Verweile 0, 1, 0, 151, 1, 1, 5;!wenn USEROUT1 = 0 auf 5!
Text 1 = "C:\Program Files\Datron\DatronCNC\Disp\Typauswahl.mcr";
Mladen 1, 0;
Markierung 5;

; !Vordruck 1 bar!
V_mseerkennung = 0;!Variable damit M erkennung nur zu Programmbeginn abgefragt wird!
Zeitbispause = 200;
V_spuelen = 0;!Variable Spuelen!
Pumpsel 1;!Dosierkopf rechts!
Ponoff_2kopf 0, 0;
Ponoff_2kopf 0, 1;
Auf_ab 0;
Dispense 0, 0, 0, 0, 0;
Position 12, 0;
; !-------------------------------!
Einaus 0, 201, 0, 2, 0, 1;!setzt USEROUT 2 auf 0 --> Stopper am Bandende unten!
Einaus 0, 201, 0, 3, 0, 1;!setzt USEROUT 3 auf 0 --> UV LED AUS!
Einaus 0, 201, 0, 4, 0, 1;!setzt USEROUT 4 auf 0 --> StartUp Sichtkontrolle vor UV-Trockner AUS!
; !Taktcodierung aktuell 0000 --> 0s Takt!
Einaus 0, 201, 0, 5, 0, 1;!setzt USEROUT 5 auf 0 --> Bit 4 der Taktcodierung AUS 2^3!
Einaus 0, 201, 0, 6, 0, 1;!setzt USEROUT 6 auf 0 --> Bit 3 der Taktcodierung AUS 2^2!
Einaus 0, 201, 0, 7, 0, 1;!setzt USEROUT 7 auf 0 --> Bit 2 der Taktcodierung AN 2^1!
Einaus 0, 201, 0, 8, 0, 1;!setzt USEROUT 8 auf 0 --> Bit 1 der Taktcodierung AN 2^0!
; !-------------------------------!
Markierung 10;
; !-------------------------------!
Amax = 30;!nur wichtig wenn Teileerkennung deaktiviert!
; !-------------------------------!
Bedingung Grafik, 0, 0, 0, 110;
Position 6, 2;!Nullpunkt laden!
Mkoord 1, 0;!Koordinatensystem linker Kopf!
Position 12, 0;
Verweile 0, 1, 0, 3001, -3, 0.5, 220;!wenn Kartusche leer rechts auf 220!
Einaus 0, 200, 0, 8, 0, 1;!gelb aus!
Einaus 0, 200, 0, 1, 0, 1;!Datron nicht aktiv!
Einaus 0, 200, 0, 2, 0, 1;!Datron fertig!
Einaus 0, 200, 1, 3, 0, 1;!Datron betriebsbereit!
; !Verweile 0, 1, 0, 5001, -3, 0.5, 220;wenn Kartusche leer links auf 220!
Verweile 0, 1, 0, 3001, -3, 0.5, 220;!wenn Kartusche leer rechts auf 220!
; !Bedingung 0, 0, 0, 220, 0;zum Testen von Kartuschenwechsel!
Verweile 0, 1, 0, 150, 2, Zeitbispause, 210;!Warte auf START!
Text 1 = " Warte auf Start";
; !Melde 1, 0, 0, 0;!
Einaus 0, 200, 1, 1, 0, 1;!Datron aktiv!
Einaus 0, 200, 0, 2, 0, 1;!Datron nicht fertig!
; !Position 10, 0;!
; !Ixyz 1, 0, -40, -50, 0, 0;!
; !Ixyz 1, 0, 20, 0, 0, 0;!
; !Ixyz 1, 0, -10, 50, 0, 0;!
Relsp 1;
Submakro Spuelen_rechts;
; !Submakro Rueckzug_rechter_kopf;!
; !Submakro Mseerkennung;!
Submakro Teileerkennung;
; !Bedingung Amax, 0, 0, 215, 0;!
; !Amax = 0;!
Markierung 110;
Mkoord 3, 0;!Koordinatensystem rechter Kopf!
Bedingung Amax, 0, 0, 250, 0;


n_teile_hinten=ceil(Amax/Any); Anzahl der Teile in hinterer Reihe, Any ist Anzahl der Reihen
n_teile_vorne=floor(Amax/Any); Anzahl der Teile in vorderer Reihe
n_teile_mitte=Amax-n_teile_hinten-n_teile_vorne

Y_start_hinten = 6; Y-koordinate für die hintere Reihe
Y_start_mitte = Y_start_hinten - Ay; Y-Koordinate für die mittlere Reihe
Y_start_vorne = Y_start_hinten - 2* Ay; Y-Koordinate für die vordere Reihe

X_start= 8 - Ax * n_teile_vorne; X-Koordinate für den ersten Bauteil vorne
Mal n_teile_vorne; 
Submakro Bauteil_vorne;

X_start= 8 + Ax; X-Koordinate für den ersten Bauteil in der Mitte
Mal n_teile_mitte;
Submakro Bauteil_mitte;

X_start= 8 - Ax * n_teile_hinten+Ax; X-Koordinate für den ersten Bauteil vorne
Mal n_teile_hinten; 
Submakro Bauteil_hinten;



Relsp 1;
Markierung 215;
Mkoord 1, 0;!Koordinatensystem linker Kopf!
; !Auf_ab 0;!
; !Position 12, 0;!
; !----------------------------------------------------!
Markierung 250;
Auf_ab 0;
Einaus 0, 200, 1, 2, 0, 1;!Datron fertig!
Einaus 0, 200, 0, 1, 0, 1;!Datron nicht aktiv!
Relsp 1;
Bedingung Grafik, 0, 0, 0, 255;
Bedingung 0, 0, 0, 10, 0;
; !-----------------Pause------------------!
Markierung 210;!Pauseposition!
; !V_mseerkennung = 0;!
Submakro Pause_rechts;
Bedingung 0, 0, 0, 10, 0;
; !-----------------Kartuschenwechsel------------------!
Markierung 220;
Submakro Kartuschenwechsel_rechts;
Bedingung 0, 0, 0, 10, 0;
Markierung 255;
