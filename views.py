from django.http import HttpResponse
from django.shortcuts import render, redirect
from pprint import pprint
import json

with open("json_data.json", 'r', encoding="utf-8") as json_file:
    json_data = json.loads(json_file.read() )

with open("json_logins.json", 'r', encoding="utf-8") as json_file1:
    json_logins = json.loads(json_file1.read() )

def index(request):
    data = {}
    data["organizations"] = json_data["Organizations"]

    return render(request, "index.html", data)

def article(request, id):
    data = {}
    data["found"] = True
    data["people"] = json_data["People"]

    for i in range(len(json_data["Organizations"])):
        for j in range(len(json_data["Organizations"][i]["IntelectualProperties"])):

            if json_data["Organizations"][i]["IntelectualProperties"][j]["ID"] == id:
                data["article"] = json_data["Organizations"][i]["IntelectualProperties"][j]

                return render(request, "article.html", data)

    data["found"] = False
    return render(request, "article.html", data)

def author(request, id):
    data = {}
    data["found"] = True
    for i in range(len(json_data["People"])):
        if json_data["People"][i]["ID"] == id:
            data["author"] = json_data["People"][i]

            return render(request, "author.html", data)
    data["found"] = False
    return render(request, "author.html", data)

def login(request):
    if request.method == 'POST':
        req = request.POST

        login = req['login']
        password = req['password']

        for k in json_logins["data"]:
            if k['login'] == login and k['password'] == password:
                request.session['type'] = k['type']
                request.session['name'] = k['login']
                return redirect('/')

        return render(request, "login.html", {"error": "Неправильно введенный логин или пароль"})

    return render(request, "login.html")

def register(request):
    if request.method == 'POST':
        req = request.POST

        login = req['login']
        password = req['password']

        for k in json_logins["data"]:
            if k['login'] == login:
                return render(request, "login.html", {"error": "Пользователь с таким логином существует"})

        json_logins['data'] += [{'FullName': FullName, 'Post': Post, 'login': login, 'password': password, 'type': 'user'}]

        with open("json_logins.json", 'w', encoding="utf-8") as json_file1:
            json.dump(json_logins, json_file1)

        request.session['type'] = 'user'
        request.session['name'] = login

        return redirect('/')

    return render(request, "register.html")

def exit(request):
    del request.session['name']
    del request.session['type']

    return redirect('/')

def admin(request):
    if not "type" in request.session:
        return redirect('/')

    if request.session["type"] == "admin":
        data = {}
        data["users"] = json_logins['data']

        if request.method == "POST":
            req = request.POST
            login = req["login"]

            if "edit" in req:
                type  = req.get('type', None)

                for ind in range(len(json_logins['data'])):
                    if json_logins['data'][ind]['login'] == login:
                        json_logins['data'][ind]['type'] = type
                        break
            elif "delete" in req:
                for ind in range(len(json_logins['data'])):
                    if json_logins['data'][ind]['login'] == login:
                        del json_logins['data'][ind]
                        break

            with open("json_logins.json", 'w', encoding="utf-8") as json_file1:
                json.dump(json_logins, json_file1)

        return render(request, "admin.html", data)

    return redirect('/')



def addProperty(request, id):
    if not "type" in request.session:
        return redirect('/')

    if request.session["type"] == "admin" or request.session["type"] == "manager":
        data = {}

        if request.method == "POST":
            req = request.POST

            new_author_id = json_data["People"][-1]["ID"] + 1

            FullName = req["FullName"]
            Birthday = req["Birthday"]
            Post = req["Post"]
            Description = req["Description"]

            json_data["People"].append(
                {
                    "ID": new_author_id,
                    "FullName": FullName,
                    "Birthday": Birthday,
                    "Post": Post,
                    "Description": Description
                }
            )

            new_prop_id = 1
            for org in json_data["Organizations"]:
                new_prop_id += len(org["IntelectualProperties"])

            Name = req["Name"]
            Date = req["Date"]
            Briefly = req["Briefly"]
            Description = req["Description"]

            json_data["Organizations"][id-1]["IntelectualProperties"].append(
                {
                    "ID": new_prop_id,
                    "Name": Name,
                    "Date": Date,
                    "Authors": [new_author_id],
                    "Briefly": Briefly,
                    "Description": Description,
                }
            )

            with open("json_data.json", 'w', encoding="utf-8") as json_file:
                json.dump(json_data, json_file, ensure_ascii = False)

        return render(request, "addProperty.html", data)

    return redirect('/')



def addOrganization(request):
    if not "type" in request.session:
        return redirect('/')

    if request.session["type"] == "admin" or request.session["type"] == "manager":
        data = {}
        if request.method == "POST":
            req = request.POST

            ID = json_data["Organizations"][-1]["ID"] + 1
            Name = req["Name"]
            StartDate = req["StartDate"]
            Description = req["Description"]
            City = req["City"]
            Street = req["Street"]
            FirstName = req["FirstName"]
            SecondName = req["SecondName"]
            MiddleName = req["MiddleName"]
            Birthday = req["Birthday"]

            json_data["Organizations"].append(
                {
                    "ID": ID,
                    "Name": Name,
                    "StartDate": StartDate,
                    "Description": Description,
                    "Location":
                    {
                        "City": City,
                        "Street": Street,
                    },
                    "Head":
                    {
                        "FirstName": FirstName,
                        "SecondName": SecondName,
                        "MiddleName": MiddleName,
                        "Birthday": Birthday,
                    },
                    "IntelectualProperties":
                    [

                    ]
                }
            )

            with open("json_data.json", 'w', encoding="utf-8") as json_file:
                json.dump(json_data, json_file, ensure_ascii = False)

        return render(request, "addOrganization.html", data)

    return redirect('/')


def deleteProperty(request,id):
    if not "type" in request.session:
        return redirect('/')

    if request.session["type"] == 'admin' or request.session["type"] == 'manager':
        for ind in range(len(json_data['Organizations'])):
            for ind2 in range(len(json_data['Organizations'][ind]['IntelectualProperties'])):
                if json_data['Organizations'][ind]['IntelectualProperties'][ind2]['ID'] == id:
                    del json_data['Organizations'][ind]['IntelectualProperties'][ind2]
                    break

        with open("json_data.json", 'w', encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii = False)

        return redirect('/')

    return redirect('/')



def deleteOrganization(request, id):
    if not "type" in request.session:
        return redirect('/')
        
    if request.session["type"] == "admin" or request.session["type"] == "manager":
        for ind in range(len(json_data['Organizations'])):
            if json_data['Organizations'][ind]['ID'] == id:
                del json_data['Organizations'][ind]
                break

        with open("json_data.json", 'w', encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii = False)

        return redirect('/')

    return redirect('/')
