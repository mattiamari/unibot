CMD_START = ("Ciao! Sono un bot che ti ricorda il tuo <b>orario delle lezioni</b> UniBo.\n"
             "Scrivi /help per la lista comandi")

_COMMANDS = ["/help - Mostra l'elenco dei comandi disponibili",
             "/setup - Imposta facoltà e anno di corso per ricevere l'orario",
             "/oggi - Mostra l'orario delle lezioni di oggi",
             "/domani - Mostra l'orario delle lezioni di domani",
             "/settimana - Mostra l'orario della settimana in corso",
             "/prossimasettimana - Mostra l'orario della prossima settimana",
             "/ricordami - Ricevi l'orario di lezione automaticamente all'orario scelto",
             "/nonricordarmi - Smetti di ricevere l'orario automaticamente",
             "/lastminute - Mostra gli avvisi dalla pagina Last Minute",
             "/esami - Mostra le info dei prossimi 3 appelli d'esame per ogni materia"]

COMMAND_LIST = ("<b>Lista comandi</b>\n{}"
                "\n\n\n<b>Se riscontri un problema non esitare a contattarci tramite il gruppo</b> "
                "https://t.me/joinchat/GOSjsE9XIKETP9DWbaRugQ\n\n"
                "<i>Version: {{}}</i>").format('\n\n'.join(_COMMANDS))

NEED_SETUP = "Non mi hai ancora detto quale facoltà frequenti. Fallo subito con /setup"

SETUP_STEP_START = ("Devo chiederti solo un paio di cose ma puoi usare il comando /annulla "
                    "per fermarmi in qualsiasi momento")

SETUP_STEP_SEARCH = ("Quale facoltà frequenti? (basta inserire una o più parole chiave, "
                     "anche abbreviate, per esempio 'medicina' o 'ing inf'")

QUERY_TOO_SHORT = "Mi servono almeno 4 caratteri (punteggiatura esclusa) per fare una ricerca. Prova di nuovo."

COURSE_SEARCH_RESULTS = "Ho trovato questi corsi:"

COURSE_SEARCH_NO_RESULT = "Non ho trovato nessun corso. Prova di nuovo."

COURSE_SEARCH_RESULT_ITEM = "<b>({})</b> {}\n"

COURSE_SEARCH_CHOOSE_RESULT = ("Per scegliere, scrivimi uno dei numeri che vedi tra parentesi "
                               "oppure /cerca per cercare di nuovo")

COURSE_NOT_SUPPORTED = "Mi dispiace ma questo corso non è supportato perchè {}."

SELECT_YEAR = "Ottimo, ora dimmi quale anno di corso stai frequentando (scrivi solo il numero)"

YEAR_NOT_VALID = "Sicuro di aver scritto un numero? Riprova."

NO_CURRICULA_FOUND = "Non ho trovato nessun curriculum. Ripetimi l'anno di corso oppure /annulla."

CURRICULA_RESULTS = "Ho trovato questi curriculum:"

CURRICULA_RESULT_ITEM = "<b>({})</b> {}\n"

SETUP_DONE = ("Abbiamo finito! Ora puoi usare tutti i comandi (/help).\n"
              "Puoi cambiare corso e anno semplicemente rifacendo il /setup")

SETUP_STOPPED = "Setup interrotto. Puoi eseguirlo di nuovo con /setup"

INVALID_SELECTION = "Devi darmi un numero della lista. Riprova."

CANCELED = "Annullato"

REMINDME_START = ("A che ora vuoi essere avvisato? Inserisci 'oggi' o 'domani' seguito dall'orario.\n"
                  "Con 'oggi' ti invierò l'orario del giorno, con 'domani' l'orario del giorno dopo.\n"
                  "Puoi usare /ricordami più volte per impostare entrambi gli orari.")
REMINDME_TIME_INVALID = "L'orario che hai inserito non è valido. Inserisci un orario 00:00 - 23:59 o /annulla"
REMINDME_END = "Perfetto, ti avviserò ogni giorno con l'orario di {} alle {} (ora italiana)"

NOREMINDME_BOTH_ACTIVE = ("Sono attivi entrambi i promemoria, quale vuoi disattivare?\n"
                          "Scrivi 'oggi' o 'domani'")
NOREMINDME_INVALID_DAY = "Scrivi 'oggi' o 'domani' oppure /annulla"
NOREMINDME_OFF = "Smetterò di inviarti l'orario ogni giorno"
NOREMINDME_OFF_DAY = "Smetterò di inviarti l'orario di {}"

NO_LESSONS = "Nessuna lezione"
YOUR_LESSONS_TODAY = "Le tue lezioni di oggi"
YOUR_LESSONS_TOMORROW = "Le tue lezioni di domani"
NO_LESSONS_WEEK = "Nessuna lezione questa settimana."
NO_REMIND_THIS_WEEK = "Per il resto della settimana non ti scriverò, lo farò solo se l'orario dovesse cambiare."

FETCH_ERROR = "Non sono riuscito ad ottenere i dati. Riprova più tardi."
SCHEDULE_FETCH_ERROR = "Non sono riuscito ad ottenere l'orario. Riprova più tardi."

NOT_SUPPORTED_LASTMINUTE = "Last Minute è supportato solo dal campus di Rimini."
NO_NEWS = "Nessuna news"

NO_EXAMS = "Nessun esame trovato."

TERM_TODAY = 'oggi'
TERM_TOMORROW = 'domani'
