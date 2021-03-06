# encoding=utf-8

from app import app
from flask import render_template, request, jsonify
# from models import Message
from datetime import datetime
import requests
from src.query_api import *
import json

# Helper func:
def load_property(fname):
    f = open(fname)
    prop_dict = {}
    for line in f.xreadlines():
        pid, pname = line.decode("utf8").strip().split("\t")
        prop_dict[pname] = pid
    f.close()
    return prop_dict
pfname = "../properties.txt"
prop_dict = load_property(pfname)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nlq")
def nlq():
    return render_template("nlq.html")

@app.route("/nlq_ask", methods=["POST"])
# Note: prompt is the specific error message to display in final answer.
def nlq_ask():
    args = request.form.get("args")
    args = json.loads(args)
    prompt = ""
    answer = ""
    item = args.get("item", "")
    prop = args.get("property", "")
    if not item:
        prompt = "We cannot locate the entity in your query!"

    # get eid of the item according to its name or alias.
    eid = find_entityid(item)
    if not eid:  
        eid = find_aliasid(item)
    if not eid: 
        prompt = "We do not find any entity with name or alias of %s!" % item
    if eid:
        # if no property detected, we consider it as to find a description 
        if not prop:
            answer = find_description(eid)
            if not answer: 
                prompt = "We consider your query as to find the definition of %s, \
                    but we cannot find its definition!" % item
        else:
            pid = prop_dict[prop]   # get pid according to dict.
            # find the value in claim triple, the prompt maybe error msg or ""
            # Note if the value is a eid, convert to its label.
            answer = find_claim_value(eid, pid)
            if not answer:
                prompt = "We consider your query as to find the missing value \
                in triple (%s, %s, ?), but we cannot find the value!" % (item, prop)


    # answer = "Just a test"
    status = "success"
    if prompt:
        status = "fail"
    return jsonify(status=status, data=answer, prompt=prompt)


@app.route("/find_entity", methods=["POST"])
def first_query():
    ename = request.form.get("sent")
    data = []
    # data = find_entity(ename)
    data = [
        ["Q100", "Boston", "HAHA"],
        ["P2", "HAH", "HAHA"],
    ]
    prompt = ""
    if len(data) == 0:
        prompt = "We do not find entities with this name!"
    status = "success"
    if prompt:
        status = "fail"
    return jsonify(status=status, data=data, prompt=prompt)

@app.route("/secondary_query", methods=["POST"])
def secondary_query():
    eid = request.form.get("eid")
    qtype = request.form.get("qtype")
    data = []
    prompt = ""
    prompts = [
        "We do not find its subclass or instance relation!",
        "We do not find statements about it!",
        "We do not find entities co-occurred with it!",
    ]
    if not qtype:
        prompt = "Please choose a option first!"
        return jsonify(status="fail", data=data, prompt=prompt)
        
    qtype = int(qtype)
    if qtype == 1:
        data = find_tree(eid)
    elif qtype == 2:
        data = find_cooccur(eid)
    elif qtype == 3:    
        data = find_statements(eid)

    if len(data) == 0:
        prompt = prompts[qtype-1]
    status = "success"
    if prompt:
        status = "fail"
    return jsonify(status=status, data=data, prompt=prompt)

@app.route("/addDict", methods=["POST"])
def add_dict():
    dic = json.loads(request.form.get("dict"))
    print dic
    # status = rule.add_dict(dic)
    status = True
    return jsonify(status=status)