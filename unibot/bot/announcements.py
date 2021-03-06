import json
from os import environ, path

sent = []
sent_file = path.join(environ['DATA_PATH'], 'sent_announcements.json')
if path.isfile(sent_file):
    with open(sent_file, 'r') as fp:
        sent = json.load(fp)

announcements = []

announcements.append({
    'seq': 0,
    'msg': ("UniBot è stato aggiornato! 🎉🎉\n"
            "- Ora puoi scegliere l'orario di avviso, prova subito con /ricordami\n"
            "- Aggiunti i comandi /settimana e /prossimasettimana\n"
            "- Le preferenze sono ora uniche per tutto il gruppo: basta che una persona "
            "faccia il /setup e tutti i membri potranno richiedere l'orario")
})

announcements.append({
    'seq': 1,
    'msg': ("UniBot è stato aggiornato! 🎉🎉\n\n"
            "- Ora è possibile cercare i corsi di laurea anche per campus (Bologna, Rimini, ...)\n\n"
            "- Puoi richiedere gli ultimi avvisi con /lastminute (solo per i corsi del campus di Rimini)")
})

announcements.append({
    'seq': 2,
    'msg': ("<b>UniBot è stato aggiornato!</b> 🎉🎉\n"
            "- Con /esami ti invierò le info dei prossimi 3 appelli per ogni materia\n\n\n"
            "Se hai problemi o suggerimenti puoi farcelo sapere tramite il gruppo -> https://t.me/joinchat/GOSjsBP21eU22j3fDHzBOQ")
})

announcements.append({
    'seq': 3,
    'msg': ("<b>UniBot è stato aggiornato!</b> 🎉🎉\n"
            "- /ricordami ora può inviarti sia l'orario del giorno, sia quello del giorno dopo, in due orari impostabili.\n\n\n"
            "Se hai problemi o suggerimenti puoi farcelo sapere tramite il gruppo -> https://t.me/joinchat/GOSjsBP21eU22j3fDHzBOQ")
})

announcements.append({
    'seq': 4,
    'msg': ("<b>UniBot è stato aggiornato!</b> 🎉🎉\n"
            "Aggiunto il supporto ai corsi con l'orario suddiviso per materie (come Storia e Antropologia di Bologna).\n"
            "Se il tuo corso non era supportato, riprova ora!\n"
            "\n\nSe riscontri problemi o hai suggerimenti puoi farcelo sapere tramite il gruppo https://t.me/joinchat/GOSjsBP21eU22j3fDHzBOQ")
})

announcements.append({
    'seq': 5,
    'msg': ("Da oggi UniBot smetterà di funzionare!\n"
            "Per chi volesse mettere in piedi la propria istanza, il codice è disponibile su GitHub (https://github.com/mattiamari/unibot). Fatemi un fischio a @mattia_mm in caso di problemi.\n"
            "Buono studio!")
})


def get_announcements():
    announcements.sort(key=lambda a: a['seq'])
    return [a for a in announcements if a['seq'] not in sent]


def set_sent(msg):
    sent.append(msg['seq'])


def save_sent():
    with open(sent_file, 'w') as fp:
        json.dump(sent, fp)
