#!/usr/bin/python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Config, Pages
from CTFd import create_app
from random import randint

import datetime
import random
import hashlib
import os
import sys
import json

CPC = 5 #challenges per category
UNSOLVED = "We need to recover the flag from this challenge! If you find it, submit with the format RC3FLAG[put the flag you found here]"
SOLVED = "This challenge was solved before by someone else! If you are sure you found the key and it is wrong, let an admin know so we can fix it."

try:
    os.remove("CTFd/ctfd.db")
except: pass
app = create_app()

categories = os.listdir("static/categories")

with app.app_context():
    db = app.db
    solves = ""
    print "GENERATING CHALLENGES"
    try:
        with open("solves.txt") as f:
            solves = f.readlines()
    except: pass
    for cat in categories:
        path = os.path.join("static/categories", cat)
        allchals = os.listdir(path)
        try:
            chals = random.sample(os.listdir(path), CPC)
        except:
            chals = allchals

        keys = []
        for l in solves:
            j = json.loads(l.rstrip())
            if j['category'] == cat:
                keys.append(j)
        for chal in chals:
            name = chal[:-4]
            dbchal = Challenges(name, UNSOLVED, random.randint(1, 1000),cat)
            db.session.add(dbchal)
            db.session.commit()
            db.session.add(Files(dbchal.id, os.path.join(path, chal)))
            setwildkey = True
            for key in keys:
                if name == key['name']:
                    setwildkey = False
                    db.session.add(Keys(dbchal.id, key['key'], 0))
                    dbchal.description = SOLVED
                    db.session.add(dbchal)
                    break
            if setwildkey:
                db.session.add(Keys(dbchal.id, "RC3FLAG\[.*\]", 1))

    print "GENERATING INITITAL CONFIG"
    buser = Teams("admin" , "admin@rc3.club", "admin")
    buser.admin = True
    db.session.add(buser)
    db.session.add(Teams("rc3" , "rc3@rc3.club", "rc3"))
    ctf_name = Config('ctf_name', "RC3RandCTF")
    page = Pages('index', '<div class="row"><h1>Welcome to RC3 RandCTF, the randomly generated CTF board based on shell-storm.org\'s CTF repo and CTFd!</h1></div>')
    max_tries = Config("max_tries", 0)
    start = Config('start', None)
    end = Config('end', None)
    view_challenges_unregistered = Config('view_challenges_unregistered', False)
    prevent_registration = Config('prevent_registration', True)
    setup = Config('setup', True)
    db.session.add(ctf_name)
    db.session.add(page)
    db.session.add(max_tries)
    db.session.add(start)
    db.session.add(end)
    db.session.add(view_challenges_unregistered)
    db.session.add(prevent_registration)
    db.session.add(setup)
    db.session.commit()
    app.setup = False
    db.session.close()
    print "DONE. Log in with admin:admin and let others log in with rc3:rc3"
