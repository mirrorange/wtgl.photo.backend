from flask import Flask, request, make_response, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from user import User
from pic import Pic
from album import Album

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
app.debug = True


@app.errorhandler(500)
def handle_500_error(error):
    return make_response({"code": 500, "message": "未知错误"})


@app.errorhandler(404)
def handle_404_error(error):
    return make_response({"code": 404, "message": "找不到所请求的资源"})


@app.route("/api/error")
def error():
    raise SyntaxError


@app.route("/api/setup")
def setup():
    User().setup()
    Pic().setup()
    Album().setup()
    return make_response({"code": 0, "message": "OK"})


@app.route("/images/<uuid>", methods=['GET'])
def getImage(uuid):
    folder = app.config["UPLOAD_FOLDER"]
    pic = Pic().getPicMimetypeByUUID(uuid=uuid)
    if (pic["code"] != 0):
        return pic
    th = request.args.get('th', default=-1, type=int)
    if (th <= 0):
        return send_file(f"{folder}/{secure_filename(uuid)}", mimetype=pic["mimetype"])
    image = Image.open(f"{folder}/{secure_filename(uuid)}")
    image.thumbnail((th, th))
    output = BytesIO()
    image.save(fp=output, format="JPEG")
    output.seek(0)
    return send_file(output, mimetype="image/jpeg")


@app.route("/api/register", methods=['GET', "POST"])
def register():
    name = request.args.get('name', default="", type=str).strip()
    email = request.args.get('email', default="", type=str).strip()
    password = request.args.get('password', default="", type=str).strip()
    if (name == "" or email == "" or password == ""):
        return make_response({"code": 400, "message": "参数 name,email,password 不可为空"})
    user = User()
    res = user.register(name=name, email=email, password=password)
    user.close()
    return make_response(res)


@app.route("/api/userAction", methods=['GET', "POST"])
def userAction():
    token = request.args.get('token', default="", type=str).strip()
    if (token == ""):
        return make_response({"code": 400, "message": "参数 token 不可为空"})
    user = User()
    res = user.userAction(token=token)
    user.close()
    return make_response(res)


@app.route("/api/login", methods=['GET', "POST"])
def login():
    user_name = request.args.get('user_name', default="", type=str).strip()
    password = request.args.get('password', default="", type=str).strip()
    if (user_name == "" or password == ""):
        return make_response({"code": 400, "message": "参数 user_name,password 不可为空"})
    user = User()
    res = user.login(name=user_name, password=password)
    user.close()
    response = make_response(res)
    if (res["code"] == 0):
        response.set_cookie(key="access_token",
                            value=res["access_token"], max_age=86400)
    return response


@app.route("/api/logout", methods=['GET', "POST"])
def logout():
    res = make_response({"code": 0, "message": "OK"})
    res.delete_cookie("access_token")
    return res


@app.route("/api/getUserInf", methods=['GET', "POST"])
def getUserInf():
    user_name = request.args.get('user_name', default="", type=str).strip()
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    if (user_name == ""):
        return make_response({"code": 400, "message": "参数 user_name 不可为空"})
    user = User()
    res = user.getUserInf(name=user_name, token=access_token)
    user.close()
    return make_response(res)


@app.route("/api/getUserList", methods=['GET', "POST"])
def getUserList():
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    user = User()
    res = user.getUserList(token=access_token)
    user.close()
    return make_response(res)


@app.route("/api/setGroup", methods=['GET', "POST"])
def setGroup():
    user_name = request.args.get('user_name', default="", type=str).strip()
    group = request.args.get('group', default=-1, type=int)
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    if (user_name == "" or group == -1):
        return make_response({"code": 400, "message": "参数 user_name,group 不可为空"})
    user = User()
    res = user.setGruop(name=user_name, group=group, token=access_token)
    user.close()
    return make_response(res)


@app.route("/api/changePassword", methods=['GET', "POST"])
def changePassword():
    user_name = request.args.get('user_name', default="", type=str).strip()
    new_password = request.args.get(
        'new_password', default="", type=str).strip()
    old_password = request.args.get(
        'old_password', default="", type=str).strip()
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    if (user_name == "" or new_password == ""):
        return make_response({"code": 400, "message": "参数 user_name,new_password 不可为空"})
    user = User()
    res = user.changePassword(name=user_name, new_password=new_password,
                              old_password=old_password, token=access_token)
    user.close()
    return make_response(res)


@app.route("/api/getPicInf", methods=['GET', "POST"])
def getPicInf():
    picid = request.args.get('picid', default=-1, type=int)
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    pic = Pic()
    res = pic.getPicInf(token=access_token, picid=picid)
    pic.close()
    return make_response(res)


@app.route("/api/uploadPic", methods=["POST"])
def uploadPic():
    title = request.args.get('title', default="", type=str).strip()
    by = request.args.get('by', default="", type=str).strip()
    category = request.args.get('category', default="", type=str).strip()
    tag = request.args.get('tag', default="", type=str).strip()
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    if (title == "" or by == "" or category == "" or tag == ""):
        return make_response({"code": 400, "message": "参数 title,by,category,tag 不可为空"})
    if 'data' not in request.files or request.files['data'].filename.rsplit(".", 1)[1].lower() not in app.config["ALLOWED_EXTENSIONS"]:
        return make_response({"code": 400, "message": "未发送文件或文件格式不支持"})
    file = request.files['data']
    pic = Pic()
    res = pic.uploadPic(token=access_token, title=title,
                        by=by, category=category, tag=tag, file=file)
    pic.close()
    return make_response(res)


@app.route("/api/searchPic", methods=['GET', "POST"])
def searchPic():
    title = request.args.get('title', default="", type=str).strip()
    by = request.args.get('by', default="", type=str).strip()
    category = request.args.get('category', default="", type=str).strip()
    tag = request.args.get('tag', default="", type=str).strip()
    user = request.args.get('user', default="", type=str).strip()
    sort = request.args.get('sort', default=0, type=int)
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    pic = Pic()
    res = pic.searchPic(sort=sort, limit=limit, offset=offset,
                        title=title, category=category, tag=tag, by=by, user=user)
    pic.close()
    return make_response(res)


@app.route("/api/changePicInf", methods=['GET', "POST"])
def changePicInf():
    picid = request.args.get('picid', default=-1, type=int)
    title = request.args.get('title', default="", type=str).strip()
    by = request.args.get('by', default="", type=str).strip()
    category = request.args.get('category', default="", type=str).strip()
    tag = request.args.get('tag', default="", type=str).strip()
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    pic = Pic()
    res = pic.changePicInf(token=access_token, picid=picid,
                           title=title, by=by, category=category, tag=tag)
    pic.close()
    return make_response(res)


@app.route("/api/getAlbum", methods=['GET', "POST"])
def getAlbum():
    albid = request.args.get('albid', default=-1, type=int)
    if (albid == -1):
        return make_response({"code": 400, "message": "参数 albid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.getAlbum(token=access_token, albid=albid)
    album.close()
    return make_response(res)


@app.route("/api/createAlbum", methods=['GET', "POST"])
def createAlbum():
    title = request.args.get('title', default="", type=str).strip()
    cover = request.args.get('cover', default=-1, type=int)
    private = request.args.get('private', default=True, type=bool)
    description = request.args.get('description', default="", type=str).strip()
    if (title == ""):
        return make_response({"code": 400, "message": "参数 title 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.createAlbum(token=access_token, title=title, cover=cover,
                            primary=False, private=private, description=description)
    album.close()
    return make_response(res)


@app.route("/api/removeAlbum", methods=['GET', "POST"])
def removeAlbum():
    albid = request.args.get('albid', default=-1, type=int)
    if (albid == -1):
        return make_response({"code": 400, "message": "参数 albid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.removeAlbum(token=access_token, albid=albid)
    album.close()
    return make_response(res)


@app.route("/api/setAlbumCover", methods=['GET', "POST"])
def setAlbumCover():
    albid = request.args.get('albid', default=-1, type=int)
    picid = request.args.get('picid', default=-1, type=int)
    if (albid == -1 or picid == -1):
        return make_response({"code": 400, "message": "参数 albid,picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.setAlbumCover(token=access_token, albid=albid, picid=picid)
    album.close()
    return make_response(res)


@app.route("/api/addToAlbum", methods=['GET', "POST"])
def addToAlbum():
    albid = request.args.get('albid', default=-1, type=int)
    picid = request.args.get('picid', default=-1, type=int)
    if (albid == -1 or picid == -1):
        return make_response({"code": 400, "message": "参数 albid,picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.addToAlbum(token=access_token, albid=albid, picid=picid)
    album.close()
    return make_response(res)


@app.route("/api/removeFromAlbum", methods=['GET', "POST"])
def removeFromAlbum():
    albid = request.args.get('albid', default=-1, type=int)
    picid = request.args.get('picid', default=-1, type=int)
    if (albid == -1 or picid == -1):
        return make_response({"code": 400, "message": "参数 albid,picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    album = Album()
    res = album.removeFromAlbum(token=access_token, albid=albid, picid=picid)
    album.close()
    return make_response(res)


@app.route("/api/addFav", methods=['GET', "POST"])
def addFav():
    picid = request.args.get('picid', default=-1, type=int)
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    user = User().checkUser(access_token)
    if (user["code"] != 0):
        return user
    album = Album()
    albid = album.getPrimaryAlbumId(user_name=user["name"])
    res = album.addToAlbum(token=access_token, albid=albid, picid=picid)
    album.close()
    return make_response(res)


@app.route("/api/removeFav", methods=['GET', "POST"])
def removeFav():
    picid = request.args.get('picid', default=-1, type=int)
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    user = User().checkUser(access_token)
    if (user["code"] != 0):
        return user
    album = Album()
    albid = album.getPrimaryAlbumId(user_name=user["name"])
    res = album.removeFromAlbum(token=access_token, albid=albid, picid=picid)
    album.close()
    return make_response(res)


@app.route("/api/getFav", methods=['GET', "POST"])
def getFav():
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    user = User().checkUser(access_token)
    if (user["code"] != 0):
        return user
    album = Album()
    albid = album.getPrimaryAlbumId(user_name=user["name"])
    res = album.getAlbum(token=access_token, albid=albid)
    album.close()
    return make_response(res)


@app.route("/api/getSubmissions", methods=['GET', "POST"])
def getSubmissions():
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    status = request.args.get("status", default=0, type=int)
    pic = Pic()
    res = pic.getSubmissions(token=access_token, status=status)
    pic.close()
    return make_response(res)


@app.route("/api/acceptSubmission", methods=['GET', "POST"])
def acceptSubmission():
    picid = request.args.get('picid', default=-1, type=int)
    tips = request.args.get('tips', default="", type=str).strip()
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    pic = Pic()
    res = pic.handleSubmission(
        token=access_token, picid=picid, accept=True, tips=tips)
    pic.close()
    return make_response(res)


@app.route("/api/rejectSubmission", methods=['GET', "POST"])
def rejectSubmission():
    picid = request.args.get('picid', default=-1, type=int)
    tips = request.args.get('tips', default="", type=str).strip()
    if (picid == -1):
        return make_response({"code": 400, "message": "参数 picid 不可为空"})
    access_token = request.args.get('access_token', default="", type=str).strip(
    ) or request.cookies.get("access_token", default="", type=str).strip()
    pic = Pic()
    res = pic.handleSubmission(
        token=access_token, picid=picid, accept=False, tips=tips)
    pic.close()
    return make_response(res)
