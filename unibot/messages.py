CMD_START = ("Ciao! Sono un bot che ti ricorda il tuo <b>orario delle lezioni</b> UniBo.\n"
            "Scrivi /help per la lista comandi")

COMMAND_LIST = ("<b>Lista comandi</b>\n"
                "/setup per scegliere facoltà, anno e curriculum\n\n"
                "/orario o /oggi per l'orario di oggi\n\n"
                "/domani per l'orario di domani\n\n"
                "/settimana per l'orario della settimana in corso\n\n"
                "/prossimasettimana per l'orario della prossima settimana\n\n"
                "/ricordami per ricevere l'orario ogni giorno\n\n"
                "/nonricordarmi per smettere di ricevere l'orario ogni mattina\n\n\n"
                "<b>Se riscontri un problema non esitare a contattarci tramite il gruppo</b> "
                "https://t.me/joinchat/GOSjsBP21eU22j3fDHzBOQ\n\n"
                "<i>Version: {}</i>")

NEED_SETUP = "Non mi hai ancora detto quale facoltà frequenti. Fallo subito con /setup"

SETUP_STEP_START = ("Devo chiederti solo un paio di cose ma puoi usare il comando /annulla "
                    "per uscire in qualsiasi momento")

SETUP_STEP_SEARCH = ("Quale facoltà frequenti? (basta inserire una o più parole chiave, "
                    "per esempio 'medicina' o 'ing inf'")

QUERY_TOO_SHORT = "Mi servono almeno 4 caratteri (punteggiatura esclusa) per fare una ricerca. Prova di nuovo."

COURSE_SEARCH_RESULTS = "Ho trovato questi corsi:"

COURSE_SEARCH_NO_RESULT = "Non ho trovato nessun corso. Prova di nuovo."

COURSE_SEARCH_RESULT_ITEM = "<b>({})</b> {}\n"

COURSE_SEARCH_CHOOSE_RESULT = ("Per scegliere, scrivimi uno dei numeri che vedi tra parentesi "
                                "oppure /cerca per cercare di nuovo")

SELECT_YEAR = "Ottimo, ora dimmi quale anno di corso stai frequentando (scrivi solo il numero)"

YEAR_NOT_VALID = "Sicuro di aver scritto un numero? Riprova."

NO_CURRICULA_FOUND = "Non ho trovato nessun curriculum. Dimmi di nuovo l'anno di corso oppure /annulla."

CURRICULA_RESULTS = "Ho trovato questi curriculum:"

CURRICULA_RESULT_ITEM = "<b>({})</b> {}\n"

SETUP_DONE = ("Abbiamo finito! Ora puoi usare tutti i comandi (/help).\n"
            "Puoi cambiare corso e anno semplicemente rifacendo il /setup")

SETUP_STOPPED = "Setup interrotto. Puoi eseguirlo di nuovo con /setup"

INVALID_SELECTION = "Devi darmi un numero della lista. Riprova."

CANCELED = "Annullato"

REMINDME_START = "A che ora vuoi essere avvisato? (inserisci un orario, ad esempio 7.10 o 11)"
REMINDME_TIME_INVALID = "L'orario che hai inserito non è valido. Inserisci un orario 00:00 - 23:59 o /annulla"
REMINDME_END = "Perfetto, ti avviserò ogni giorno alle {} (ora italiana)"
REMINDME_OFF = "Smetterò di inviarti l'orario ogni mattina"

NO_LESSONS_TODAY = "Oggi non hai lezioni"
NO_LESSONS_TOMORROW = "Domani non avrai lezioni"
