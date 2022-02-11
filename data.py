
import json
import pandas

# defination des path des path des fichiers d'entrer et de sorti
in_file = "LoL.csv"
out_file = "data2.json"

input = pandas.read_csv(in_file, sep=';')

# il y a des données sous la forme "50%" les lignes suivante serve a retiré le % et a passé la données en numérique
input.Win_percent = pandas.to_numeric(input['Win_percent'].str[:-1])
input.Role_percent = pandas.to_numeric(input['Role_percent'].str[:-1])
input.Pick_percent = pandas.to_numeric(input['Pick_percent'].str[:-1])
input.Ban_percent = pandas.to_numeric(input['Ban_percent'].str[:-1])
i = 1

# Boucle pour parse le fichier .csv
with open('legends2.json', 'w+') as outfile:
    for row in input.to_dict('records'):
        # definition de l'entête nécessaire au _bulk d'OpenSearch
        index_line = '{"index": {"_index": "legends", "_id": %s }}\n' % (i)
        i += 1
        # definition des noms des colonnes pour placer les données
        data = json.dumps(dict(list(
            zip(["Name", "Class", "Role", "Tier", "Score", "Trend", "Win_percent", "Role_percent", "Pick_percent",
                 "Ban_percent", "KDA"],
                row.values())))) + '\n'
        # écriture du fichier de sorti
        outfile.write(index_line + data)
