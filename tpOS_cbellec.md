# TP OpenSearch

## But

Le but de ce TP est, apres le choix d'un dataset, de créer une version rapidement intégrable dans OpenSearch par
la méthode _bulk, puis de proposer un mapping adapté aux données et en fin faire 5 requêtes et 5 aggrégation utile
à la compréhension du dataset.

## Choix du dataset

Pour ma part j'ai choisi un dataset sur les statistiques des champions sur les parties classé du jeu league of legends.
Ce dataset contient 234 ligne et 11 colonnes, je vais vous décrire les différente colonnes.

- **Name** str : Le nom du champion ;
- **Class** str : La classe du champion qui ne peux prendre que 6 valeur (Fighter, Assassin, Mage, Marksman, Support, Tank);
- **Role** str : Role du champion dans la partie, ne peut prendre que 5 valeur (Top, Mid, ADC, Support, Jungle) ;
- **Tier** str : Classement du couple {Role, Champion}, ne peux pendre que 6 valeur (God, S, A, B, C, D) ;
- **Score** int : Score global du couple {Rol, Champion} ;
- **Trend** int : Tendance du couple {Role, Champion} ;
- **Win %** int : Taux de victoire du champion dans le role ;
- **Role %** int : Taux de choix du role par champion ;
- **Pick %** int : Taux de choix du champion ;
- **Ban %** int : Taux de bannissement du champion ;
- **KDA** int : Ratio calculer par la formule (Kill + Assist)/Death 

## Integration 

Le dataset est au format .csv pour pouvoir l'intégrer dans OpenSearch par la méthode _bulk il faut d'un part le formater 
en json et d'autre part ajouter un entête pour chaque entrée de la forme 
```json
{"index": {"_index": "index", "_id": i }}
```
j'ai donc écris un script python pour formater le dataset
```python
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
```
Et j'ai bien à la sorti un json formater pour OpenSearch

```json
{"index": {"_index": "legends", "_id": 1 }}
{"Name": "Aatrox", "Class": "Fighter", "Role": "TOP", "Tier": "A", "Score": 55.11, "Trend": -3.14, "Win_percent": 48.97, "Role_percent": 94.09, "Pick_percent": 4.33, "Ban_percent": 1.97, "KDA": 1.92}
{"index": {"_index": "legends", "_id": 2 }}
{"Name": "Ahri", "Class": "Mage", "Role": "MID", "Tier": "A", "Score": 55.85, "Trend": 2.64, "Win_percent": 50.71, "Role_percent": 93.24, "Pick_percent": 4.56, "Ban_percent": 1.04, "KDA": 2.55}
```
Il n'y a plus qu'a l'importer en bulk avec la commande :
```commandline
curl -u admin:admin --insecure -XPUT https://localhost:9200/_bulk -H "Content-Type: application/json" --data-binary @legends.json
```

## Mapping

## Requêtes

- Pour ma premiere requête je vais chercher le champion le mieux classer et avec la plus haute popularité :
```json
{
	"query": {
		"term": {
			"Tier.keyword":"God"
		}
	},
	"sort":[{"Trend": "desc"}]
}
```
Je fait donc une recherche par terme pour n'avoir que les champions God tier et je les classe en fonction de leurs popularités.
```json
{
	"took": 2,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 23,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
			{
            "_index": "legends",
            "_type": "_doc",
            "_id": "63",
            "_score": null,
            "_source": {
                "Name": "Janna",
                "Class": "Support",
                "Role": "SUPPORT",
                "Tier": "God",
                "Score": 90.63,
                "Trend": 38.71,
                "Win_percent": 53.21,
                "Role_percent": 95.09,
                "Pick_percent": 12.8,
                "Ban_percent": 6.93,
                "KDA": 3.24
            },
            "sort": [
                38.71
            ]
			},
          {
            "_index": "legends",
            "_type": "_doc",
            "_id": "147",
            "_score": null,
            "_source": {
              "Name": "Senna",
              "Class": "Marksman",
              "Role": "SUPPORT",
              "Tier": "God",
              "Score": 77.51,
              "Trend": 31.08,
              "Win_percent": 52.29,
              "Role_percent": 67.4,
              "Pick_percent": 10.67,
              "Ban_percent": 7.43,
              "KDA": 2.72
            }
```
- Pour ma seconde requête je vais chercher les champions avec une tendance positive.

```json
{
  "query": {
    "range": {
      "Trend": {"gte":0.0}
    }
  }
}
```

- Pour ma troisième requête je vais chercher le champion le plus jouer au TOP.
```json
{
	"query" : {
		"term": {
			"Role.keyword":"TOP"
		}
	},
  "sort" : [{"Pick_percent":"desc"}]
}
```

- Pour ma quatrième requête je vais chercher les champions support et les classe en fonction de leurs KDA.
```json
{
	"query" : {
		"term": {
                  "Role.keyword":"SUPPORT"
		}
	},
  "sort" : [{"KDA":"desc"}]
}
```

- Pour ma derniere requête je vais chercher les champions qui sont jouer 80% du temps dans leurs role.
```json
{
  "query": {
    "range": {
      "Role_percent": {"gte":80}
    }
  }
}
```

## Aggrégations

- Pour ma premiere aggrégations je vais chercher à savoir combien il y a de champion par role.
```json
{
  "size":0,
  "aggs": {
    "championBuckets": {
      "filters": {
            "filters" : {
                 "TOP": {
                "match" : {
                    "Role.keyword" : "TOP"
                }
            },
            "MID": {
                "match" : {
                    "Role.keyword" : "MID"
                }
            },
            
            "JUNGLE": {
                "match" : {
                    "Role.keyword" : "JUNGLE"
                }
            },
            "ADC": {
                "match" : {
                    "Role.keyword" : "ADC"
                }
            },
            "SUPPORT": {
                "match" : {
                    "Role.keyword" : "SUPPORT"
                }
            } 
        }
      }
    }
  }
}
```
resultat : 
```json
{
	"took": 4,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 234,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
		]
	},
	"aggregations": {
            "championBuckets": {
                "buckets": {
                    "ADC": {
                        "doc_count": 29
                    },
                    "JUNGLE": {
                        "doc_count": 46
                    },
                    "MID": {
                        "doc_count": 59
                    },
                    "SUPPORT": {
                        "doc_count": 40
                    },
                    "TOP": {
                        "doc_count": 60
                    }
                }
            }
	}
}
```
- Pour ma seconde aggrégation je vais chercher le KDA moyenne des champions ADC
```json
{
  "size":0,
	"query" : {
      "term": {
        "Role.keyword":"ADC"
      }
	},
  "aggs": {
    "KDAavg": {
      "avg":{
        "field":"KDA"		
      }
    }
  }
}
```
Avec cette aggrégation je peux voir que le KDA moyen des joueurs ADC est de 2.4

- Pour ma troisième aggrégation je vais chercher à savoir le nombre de champions disponible dans league of legend car 
dans le base de données un champion peux apparaître plusieurs fois (il peut être joué dans plusieurs role)
```json
{
  "size":0,
  "aggs": {
    "unique_champion": {
      "cardinality":{
        "field":"Name.keyword"		
      }
    }
  }
}
```
Je peux donc dire maintenant qu'il y a 158 champions dans League of Legends

- Pour ma quatrième requête j'aimerais savoir si le KDA est correler
```json
{
  "size": 0,
  "aggs": {
    "matrix_stats_KDA": {
      "matrix_stats": {
        "fields": ["Trend", "Win_percent"]
      }
    }
  }
}
```
Resultat :
```json
{
	"took": 13,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 234,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
		]
	},
	"aggregations": {
		"matrix_stats_KDA": {
			"doc_count": 234,
			"fields": [
				{
                    "name": "Win_percent",
                    "count": 234,
                    "mean": 50.011666615804046,
                    "variance": 3.0231184079816416,
                    "skewness": -0.3589026350617301,
                    "kurtosis": 3.5767231260069376,
                    "covariance": {
                        "Win_percent": 3.0231184079816416,
                        "Trend": 4.161489495331893
                    },
                    "correlation": {
                        "Win_percent": 1.0,
                        "Trend": 0.35314277075040784
                    }
                },
                    {
                        "name": "Trend",
                        "count": 234,
                        "mean": -0.11837605730845374,
                        "variance": 45.93479762522602,
                        "skewness": 0.9193463882632679,
                        "kurtosis": 15.01808236213293,
                        "covariance": {
                            "Win_percent": 4.161489495331893,
                            "Trend": 45.93479762522602
                        },
                        "correlation": {
                            "Win_percent": 0.35314277075040784,
                            "Trend": 1.0
                        }
                    }
                ]
		}
	}
}
```
On peux voir que la popularité d'un champion est corréler a 0.35 avec le taux de victoire donc la popularité un champion
n'ai pas lié avec le taux de victoire.


- Pour ma derniere aggrégation les statistiques relatif au KDA et ADC.
```json
{
  "size":0,
	"query" : {
		"term": {
			"Role.keyword":"ADC"
		}
	},
  "aggs": {
    "KDAstats": {
      "stats":{
        "field":"KDA"		
      }
    }
  }
}
```
On obtient: 
```json
{
	"took": 9,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 29,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
		]
	},
	"aggregations": {
		"KDAstats": {
			"count": 29,
			"min": 1.9700000286102295,
			"max": 3.049999952316284,
			"avg": 2.4096551681387015,
			"sum": 69.87999987602234
		}
	}
}
```