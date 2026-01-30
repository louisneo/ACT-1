from django.shortcuts import render

def home(requests):
    return render(requests, 'home.html', {})

def addUser(requests):
    return render(requests, 'addUser.html', {})
