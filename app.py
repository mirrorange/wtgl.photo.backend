from flask import Flask,request,make_response
from user import User

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
app.debug=True

@app.route("/api/register", methods=['GET', "POST"])
def register():
    name = request.args.get('name',default="",type=str).strip()
    email = request.args.get('email',default="",type=str).strip()
    password = request.args.get('password',default="",type=str).strip()
    if(name == "" or email == "" or password == ""):
        return make_response({"code":400,"message":"参数 name,email,password 不可为空"})
    try:
        user = User()
        res = user.register(name=name,email=email,password=password)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})

@app.route("/api/userAction", methods=['GET', "POST"])
def userAction():
    token = request.args.get('token',default="",type=str).strip()
    if(token == ""):
        return make_response({"code":400,"message":"参数 token 不可为空"})
    try:
        user = User()
        res = user.userAction(token=token)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})

@app.route("/api/login", methods=['GET', "POST"])
def login():
    user_name = request.args.get('user_name',default="",type=str).strip()
    password = request.args.get('password',default="",type=str).strip()
    if(user_name == "" or password == ""):
        return make_response({"code":400,"message":"参数 user_name,password 不可为空"})
    try:
        user = User()
        res = user.login(name=user_name,password=password)
        user.close()
        response = make_response(res)
        if(res["code"] == 0):
            response.set_cookie(key="access_token",value=res["access_token"],max_age=86400)
        return response
    except:
        return make_response({"code":-1,"message":"未知错误"})

@app.route("/api/logout", methods=['GET', "POST"])
def logout():
    res = make_response({"code":0,"message":"成功"})
    res.delete_cookie("access_token")
    return res

@app.route("/api/getUserInf", methods=['GET', "POST"])
def getUserInf():
    user_name = request.args.get('user_name',default="",type=str).strip()
    access_token = request.args.get('access_token',default="",type=str).strip()
    if(access_token == ""):
        access_token = request.cookies.get("access_token",default="",type=str).strip()
    if(access_token == ""):
        return make_response({"code":401,"message":"请先登录"})
    if(user_name == ""):
        return make_response({"code":400,"message":"参数 user_name 不可为空"})
    try:
        user = User()
        res = user.getUserInf(name=user_name,token=access_token)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})

@app.route("/api/getUserList", methods=['GET', "POST"])
def getUserList():
    access_token = request.args.get('access_token',default="",type=str).strip()
    if(access_token == ""):
        access_token = request.cookies.get("access_token",default="",type=str).strip()
    if(access_token == ""):
        return make_response({"code":401,"message":"请先登录"})
    try:
        user = User()
        res = user.getUserList(token=access_token)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})


@app.route("/api/setGroup", methods=['GET', "POST"])
def setGroup():
    user_name = request.args.get('user_name',default="",type=str).strip()
    group = request.args.get('group',default=-1,type=int)
    access_token = request.args.get('access_token',default="",type=str).strip()
    if(access_token == ""):
        access_token = request.cookies.get("access_token",default="",type=str).strip()
    if(access_token == ""):
        return make_response({"code":401,"message":"请先登录"})
    if(user_name == "" or group == -1):
        return make_response({"code":400,"message":"参数 user_name,group 不可为空"})
    try:
        user = User()
        res = user.setGruop(name=user_name,group=group,token=access_token)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})

@app.route("/api/changePassword", methods=['GET', "POST"])
def changePassword():
    user_name = request.args.get('user_name',default="",type=str).strip()
    new_password = request.args.get('new_password',default="",type=str).strip()
    old_password = request.args.get('old_password',default="",type=str).strip()
    access_token = request.args.get('access_token',default="",type=str).strip()
    if(access_token == ""):
        access_token = request.cookies.get("access_token",default="",type=str).strip()
    if(user_name == "" or new_password == ""):
        return make_response({"code":400,"message":"参数 user_name,new_password 不可为空"})
    try:
        user = User()
        res = user.changePassword(name=user_name,new_password=new_password,old_password=old_password,token=access_token)
        user.close()
        return make_response(res)
    except:
        return make_response({"code":-1,"message":"未知错误"})