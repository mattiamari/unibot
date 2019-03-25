CMD_START = ("Ciao! Sono un bot che ti ricorda il tuo <b>orario delle lezioni</b> UniBo.\n"
            "Scrivi /help per la lista comandi")

COMMAND_LIST = ("<b>Lista comandi</b>\n"
                "/setup per scegliere facoltà, anno e curriculum\n\n"
                "/orario o /oggi per l'orario di oggi\n\n"
                "/domani per l'orario di domani o il prossimo giorno di lezione\n\n"
                "/ricordami per ricevere l'orario del giorno ogni mattina\n\n"
                "/smetti per smettere di ricevere l'orario ogni mattina\n\n\n"
                "<b>Se riscontri un problema non esitare a farcelo sapere entrando nel gruppo</b> "
                "https://t.me/joinchat/GOSjsBP21eU22j3fDHzBOQ\n\n"
                "<i>Version: {}</i>")

NEED_SETUP = ("Come faccio a dirti il tuo orario se non so quale facoltà frequenti?\n"
            "Psss... usa il comando /setup")

SETUP_STEP_START = "Devo chiederti solo un paio di cose"

SETUP_STEP_SEARCH = ("Quale facoltà frequenti? (basta inserire una o più parole chiave, "
                    "per esempio 'medicina' o 'ing inf'")

QUERY_TOO_SMALL = "Mi servono almeno 4 caratteri per fare una ricerca. Prova di nuovo."

COURSE_SEARCH_RESULTS = "Ho trovato questi corsi:"

COURSE_SEARCH_NO_RESULT = "Non ho trovato nessun corso. Prova di nuovo."

COURSE_SEARCH_RESULT_ITEM = "<b>({})</b> {}\n"

COURSE_SEARCH_CHOOSE_RESULT = ("Per scegliere, scrivimi uno dei numeri che vedi tra parentesi "
                                "oppure /cerca per cercare di nuovo")

SELECT_YEAR = "Ottimo, ora dimmi quale anno di corso stai frequentando (scrivi solo il numero 1, 2, 3, ecc)"

YEAR_NOT_VALID = "Sicuro di aver scritto un numero? Riprova."

NO_CURRICULA_FOUND = "Non ho trovato nessun curriculum. Dimmi di nuovo l'anno di corso."

CURRICULA_RESULTS = "Ho trovato questi curriculum:"

CURRICULA_RESULT_ITEM = "<b>({})</b> {}\n"

SETUP_DONE = ("Abbiamo finito! Ora puoi usare tutti i comandi (/help).\n"
            "Puoi cambiare corso e anno semplicemente rifacendo il /setup")

SETUP_STOPPED = "Setup interrotto. Puoi eseguirlo di nuovo con /setup"

REMINDME_ON = "Ti invierò l'orario del giorno ogni mattina intorno alle ore 7.00"
REMINDME_OFF = "Smetterò di inviarti l'orario ogni mattina"

INVALID_SELECTION = "Devi darmi un numero della lista. Riprova."
