import json

dic = {}
jsonString = json.dumps(dic)
jsonFile = open("testList.json", "w")
jsonFile.write(jsonString)
jsonFile.close()




