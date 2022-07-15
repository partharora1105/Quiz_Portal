import json
import os
ascii_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__, static_folder="static")


@app.route('/quiz/admin',methods = ['POST', 'GET'])
def openAdmin():
    readFile = open("static/data/testList.json" , "r")
    testList = json.loads(readFile.read())
    readFile.close()
    return render_template("admin.html", testDict = testList)

@app.route('/quiz/admin/delete',methods = ['POST', 'GET'])
def deleteAdmin():
    readFile = open("static/data/testList.json" , "r")
    testList = json.loads(readFile.read())
    readFile.close()
    deleteTestName = request.form["delete"]
    for filePath in testList[deleteTestName]:
        os.remove(filePath)
    del testList[deleteTestName]
    newFile = open("static/data/testList.json" , "w")
    newFile.write(json.dumps(testList))
    newFile.close()
    return render_template("admin.html", testDict = testList)


@app.route("/quiz/question-paper/step1", methods = ["POST" , "GET"])
def openNewTest():
    return render_template ("questionMaker.html" , val = True)

@app.route("/quiz/question-paper/step2", methods = ["POST" , "GET"])
def step1():
    mcqList = []
    try:
        num =int(request.form["num"])
    except:
         return render_template ("questionMaker.html" , val = True, message = "Number of questions can't be empty")
    opts = request.form["opts"]
    if opts == "":
        opts = "0"
        
    optList = []
    for item in opts.split(","):
        newItem = item.strip()
        try:
            if "-" in newItem:
                temp = item.split("-")
                small = int(temp[0])
                big = int(temp[1])
                for i in range(small , big +1):
                    optList.append(i)
            else:
                optList.append(int(newItem))
        except:
            return render_template ("questionMaker.html" , val = True, message = "Error: Make sure Text or Image Based Questions are integers seperated with only commas and hyphens")
    if max(optList) > num:
         return render_template ("questionMaker.html" , val = True, message = "Error: Please ensure that index of Text/Image question isnt greater than total number of questions")

    for i in range(1, num+1):
        if i not in optList:
            mcqList.append(i)
    optList.sort()
    mcqList.sort()
    return render_template ("questionMaker.html" , val = False , name = request.form["testName"], time = request.form["time"], num = num, opts = opts, mcqList = mcqList)

@app.route("/quiz/question-paper/complete", methods = ["POST" , "GET"])
def complete():
    testName = request.form["testName"]
    readFile = open("static/data/testList.json", "r") 
    testList= json.loads(readFile.read())
    readFile.close()
    if testName in testList.keys():
        testName= testName + "(new)"
        
    testList[testName] = []
    questionPaper= request.files["qp"]
    if questionPaper.filename != '':
        paperName = "static/data/" + testName + ".pdf"
        questionPaper.save(paperName)
    
        testList[testName].append(paperName)
    else:
        return render_template ("questionMaker.html" , val = True, message = "Error: Invalid File")
    mcqDict = {}
    num = int(request.form["num"])
    for i in range(1, num+1):
        try:
            numberOfOptions = int(request.form[str(i) + "options"])
            alphabets = []
            for j in range(0, int(numberOfOptions)):
                alphabets.append(ascii_upper[j])
            correctOptions = request.form[str(i) + "correct"].upper().split(",")
            mcqDict[i] = {"numberOfOptions": numberOfOptions, "alphabets": alphabets, "correctOptions(s)": correctOptions, "msq" : len(correctOptions) > 1}
        except KeyError:
            continue
    testDic = {"questionPaper": {"testName": testName,"paperPath": paperName , "time": int(request.form["time"]), "numberOfQuestions": int(num) , "mcqs": mcqDict} , "studentResponses": {}}
    jsonPath = "static/data/"+testName + ".json"
    dataFile = open(jsonPath, "w")
    testList[testName].append(jsonPath)
    dataFile.write(json.dumps(testDic))
    dataFile.close()
    listFile = open("static/data/testList.json", "w")
    listFile.write(json.dumps(testList))
    listFile.close()
    test_url = url_for("testPage", link1 = testName)
    review_url = url_for("reviewPage", link2 = testName)
    attempt_url = url_for("attemptPage", link3 = testName)
    readFile = open("static/data/testList.json" , "r")
    testList = json.loads(readFile.read())
    readFile.close()
    return render_template("admin.html", testDict = testList)
   

@app.route("/quiz/<link1>", methods = ["POST" , "GET"])
def testPage(link1):
    testName = link1
    readFile = open("static/data/"+testName + ".json", "r")
    testData = json.loads(readFile.read())
    readFile.close()
    time = testData["questionPaper"]["time"]
    return render_template('start.html', testName = testName , time =time)

@app.route("/quiz/<link3>/singleAttempt", methods = ["POST" , "GET"])
def attemptPage(link3):
    testName = link3
    studentName = request.form["studentName"]
    readFile = open("static/data/"+testName + ".json", "r")
    testData = json.loads(readFile.read())
    readFile.close()
    questionPaper = testData["questionPaper"]
    time = int(questionPaper["time"]) * 60
    indexList = []
    for i in range(1, 1+ testData["questionPaper"]["numberOfQuestions"]):
        indexList.append(str(i))
    if studentName in testData["studentResponses"]:
        testData["studentResponses"][studentName + "2"] = {"result" : "Attempting", "wrong" : {}, "responses" : {}}
    else:
        testData["studentResponses"][studentName] = {"result" : "Attempting", "wrong" : {}, "responses" : {}}
    newFile = open("static/data/"+testName + ".json", "w")
    newFile.write(json.dumps(testData))
    newFile.close()
    return render_template('omr.html', studentName = studentName, questionPaper= questionPaper, indexList =  indexList, filePath = questionPaper['paperPath'][7:], time = time)

@app.route("/quiz/<link2>/review", methods = ["POST" , "GET"])
def reviewPage(link2):
    testName = link2
    readFile = open("static/data/"+testName + ".json", "r")
    testData = json.loads(readFile.read())
    readFile.close()
    req = testData["studentResponses"] 
    return render_template('review.html', studentData = req , testName = testName)

@app.route("/quiz/testSubmitted", methods = ["POST" , "GET"])
def gatherAnswers():
    testName = request.form["testName"]
    studentName = request.form["studentName"] 
    readFile = open("static/data/"+testName + ".json", "r")
    testData = json.loads(readFile.read())
    readFile.close()
    ansDict = {}
    total = 0
    totalCorrect = 0
    wrongDic = {}
    questionPaper = testData["questionPaper"]
    for index in range(1, 1+ questionPaper["numberOfQuestions"]):
        if str(index) in questionPaper["mcqs"] and bool(questionPaper["mcqs"][str(index)]["msq"]):
            try:
                attemptedMsqs = []
                for alphabet in questionPaper["mcqs"][str(index)]["alphabets"]:
                    try:
                        attemptedMsqs.append(request.form[str(index) + alphabet])
                    except:
                        continue
                attempted = sorted(attemptedMsqs)
            except:
                attempted = []
            correct = sorted(questionPaper["mcqs"][str(index)]["correctOptions(s)"])
            result = correct == attempted
            total += 1
            if result:
                totalCorrect +=1
            else:
                wrongDic[index] = attempted
            ansDict[index] = {"correctAns":  correct, "attemptedAns": attempted, "result": result }
        elif str(index) in questionPaper["mcqs"] and not bool(questionPaper["mcqs"][str(index)]["msq"]):
            correct = questionPaper["mcqs"][str(index)]["correctOptions(s)"]
            try:
                attempted = [request.form[str(index)]]
            except:
                attempted = []
            result =  correct == attempted
            total += 1
            if result:
                totalCorrect +=1
            else:
                wrongDic[index] = attempted
            ansDict[index] = {"correctAns": correct , "attemptedAns": attempted, "result": result}
        else:
            try:
                uploaded= request.files[str(index) + "file"]
                if uploaded.filename != '':
                    imagePath = "static/data/" + testName +"_"  + studentName +"_"  + str(index)
                    uploaded.save(imagePath)
                    readFile = open("static/data/testList.json", "r")
                    testList = json.loads(readFile.read())
                    readFile.close()
                    testList[testName].append(imagePath) 
                    newFile = open("static/data/testList.json", "w")
                    newFile.write(json.dumps(testList ))
                    newFile.close()
                else:
                    imagePath = "Not Uploaded"
            except:
                imagePath = "Not Uploaded"
            ansDict[index] ={"correctAns": "NA", "attemptedAns" : {"text": request.form[str(index) +"text"], "image": imagePath}, "result": "NA"}

    readFile = open("static/data/"+testName + ".json", "r")
    testData = json.loads(readFile.read())
    readFile.close()
    testData["studentResponses"][studentName] = {"result": str(totalCorrect) + "/" + str(total), "wrong": wrongDic,  "responses" : ansDict}
    newFile = open("static/data/"+testName + ".json", "w")
    newFile.write(json.dumps(testData))
    newFile.close()
    return redirect(url_for("testPage" , link1 = testName))


app.debug = True
app.run()

