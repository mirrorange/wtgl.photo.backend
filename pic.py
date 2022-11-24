import config
from user import User
import time
import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid1
from werkzeug.datastructures import FileStorage
import json

Base = declarative_base()


class Pics(Base):
    __tablename__ = "pics"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), unique=True)
    mimetype = Column(String(32))
    title = Column(String(64))
    user = Column(String(32))
    by = Column(String(32))
    category = Column(String(32))
    tag = Column(String(128))
    creation_time = Column(Integer)
    view = Column(Integer)
    fav = Column(Integer)
    status = Column(Integer)
    tips = Column(String(128))

    def __init__(self, uuid, title, user, by, category, tag, mimetype, status=0):
        self.uuid = uuid
        self.mimetype = mimetype
        self.title = title
        self.user = user
        self.by = by
        self.category = category
        self.tag = tag
        self.creation_time = time.time()
        self.status
        self.view = 0
        self.fav = 0
        self.status = status
        self.tips = ""


class Pic():

    def __init__(self):
        self.sql = sqlalchemy.create_engine(config.SQL_URL)
        self.sql.connect()
        self.session = sessionmaker(self.sql)()

    def setup(self):
        Base.metadata.create_all(self.sql)

    def close(self):
        self.session.commit()
        self.session.close()

    def picExist(self, picid: int):
        """
        检查图片是否存在

        参数:
          picid - 图片ID
        """
        if (self.session.query(Pics).filter_by(id=picid).first()):
            return True
        else:
            return False

    def picView(self, picid: int):
        """
        统计图片访问量

        参数:
          picid - 图片ID
        """
        pic = self.session.query(Pics).filter_by(id=picid)
        view = pic.first().view
        pic.update({Pics.view: view+1})
        self.session.commit()

    def picFav(self, picid: int, addOrRemove: bool):
        """
        统计图片收藏量

        参数:
          picid - 图片ID
          addOrRemove - True: 收藏 +1  False: 收藏 -1
        """
        pic = self.session.query(Pics).filter_by(id=picid)
        fav = pic.first().fav
        if (addOrRemove):
            pic.update({Pics.fav: fav+1})
        else:
            pic.update({Pics.fav: fav-1})
        self.session.commit()

    def getPicMimetypeByUUID(self, uuid: str):
        """
        获取图片Mimetype

        参数:
          uuid - 图片UUID
        """
        pic = self.session.query(Pics).filter_by(uuid=uuid).first()
        if (pic):
            return {"code": 0, "message": "OK", "mimetype": pic.mimetype}
        else:
            return {"code": 404, "message": "图片不存在"}

    def getPicInf(self, token: str, picid: int):
        """
        获取图片信息

        参数:
          picid - 图片ID
        """
        pic = self.session.query(Pics).filter_by(id=picid).first()
        if (pic):
            if (pic.status != 1):
                if (token == ""):
                    return {"code": 101, "message": "请先登录"}
                user = User().checkUser(token=token)
                if (user["code"] != 0):
                    return user
                if (user["name"] != pic.user and user["group"] < 1):
                    return {"code": 403, "message": "拒绝访问：图片审核未通过"}
            self.picView(picid=picid)
            return {"code": 0, "message": "OK", "title": pic.title, "category": pic.category, "tag": json.loads(pic.tag), "url": f"{config.URL_BASE}/images/{pic.uuid}",
                    "user": pic.user, "by": pic.by, "creation_time": pic.creation_time, "view": pic.view, "fav": pic.fav, "status": pic.status}
        else:
            return {"code": 404, "message": "图片不存在"}

    def searchPic(self, sort: int = 0, limit: int = 20, offset: int = 0, title: str = "", category: str = "", tag: str = "", user: str = "", by: str = ""):
        """
        搜索图片

        参数:
          sort - 排序方式
          limit - 最大返回结果数目
          offset - 查询起始位置
          ... - 搜索项
        """
        pics = self.session.query(Pics)
        pics = pics.filter_by(status=1)
        if (category != ""):
            pics = pics.filter_by(category=category)
        if (user != ""):
            pics = pics.filter_by(user=user)
        if (by != ""):
            pics = pics.filter_by(by=by)
        if (tag != ""):
            tags = filter(lambda x: x.strip(), tag.split(","))
            for t in tags:
                pics = pics.filter(Pics.tag.like(f"%{t}%"))
        if (title != ""):
            pics = pics.filter(Pics.title.like(f"%{title}%"))
        if (sort == 0):
            pics = pics.order_by(Pics.creation_time.desc())
        elif (sort == 1):
            pics = pics.order_by(Pics.fav.desc())
        pics = pics.offset(offset).limit(limit)
        pics = pics.all()
        piclist = []
        for pic in pics:
            piclist.append({"title": pic.title, "category": pic.category, "tag": json.loads(pic.tag), "url": f"{config.URL_BASE}/images/{pic.uuid}",
                            "user": pic.user, "by": pic.by, "creation_time": pic.creation_time, "view": pic.view, "fav": pic.fav})
        return {"code": 0, "message": "OK", "list": piclist}

    def changePicInf(self, token: str, picid: int, title: str = "", by: str = "", category: str = "", tag: str = ""):
        """
        修改图片信息

        参数:
          token - AccessToken
          picid - 图片ID
          ... - 修改项
        """
        user = User().checkUser(token)
        if (user["code"] != 0):
            return user
        pic = self.session.query(Pics).filter_by(id=picid)
        if (user["group"] < 1 and pic.first().user != user["name"]):
            return {"code": 103, "message": "权限不足"}
        if (title != ""):
            pic.update({Pics.title: title})
        if (by != ""):
            pic.update({Pics.by: by})
        if (category != ""):
            pic.update({Pics.category: category})
        if (tag != ""):
            tags = json.dumps(
                list(filter(lambda x: x.strip(), tag.split(","))))
            pic.update({Pics.tag: tags})
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def uploadPic(self, token: str, title: str, by: str, category: str, tag: str, file: FileStorage):
        """
        上传图片

        参数:
          token - AccessToken
          title - 图片标题
          by - 图片作者
          category - 图片分类
          tag - 图片标签
          file - 图片文件
        """
        user = User().checkUser(token)
        if (user["code"] != 0):
            return user
        uuid = uuid1()
        tags = json.dumps(list(filter(lambda x: x.strip(), tag.split(","))))
        pic = Pics(uuid=uuid, title=title,
                   user=user["name"], by=by, category=category, tag=tags, mimetype=file.mimetype)
        self.session.add(pic)
        self.session.commit()
        file.save(f"{config.UPLOAD_FOLDER}/{uuid}")
        return {"code": 0, "message": "OK", "picid": pic.id}

    def getSubmissions(self, token: str, status: int = 0):
        """
        获取所有投稿 （管理员）
        获取自己的投稿 （普通用户）

        参数:
          token - AccessToken
          status - 投稿状态 0:待审核 1:审核通过 2:审核不通过
        """
        user = User().checkUser(token)
        if (user["code"] != 0):
            return user
        pics = self.session.query(Pics).filter(Pics.status == status)
        if (user["group"] < 1):
            pics = pics.filter_by(user=user["name"])
        piclist = []
        for pic in pics:
            piclist.append({"picid": pic.id, "title": pic.title, "category": pic.category, "tag": json.loads(
                pic.tag), "url": f"{config.URL_BASE}/images/{pic.uuid}", "user": pic.user, "by": pic.by, "creation_time": pic.creation_time, "status": pic.status, "tips": pic.tips})
        return {"code": 0, "message": "OK", "list": piclist}

    def handleSubmission(self, token: str, picid: int, accept: bool, tips: str = ""):
        """
        处理待审核的投稿

        参数:
          token - AccessToken
          tips - 管理员提示信息
          status - 投稿状态 0:待审核 1:审核通过 2:审核不通过
        """
        user = User().checkUser(token)
        if (user["code"] != 0):
            return user
        if (user["group"] < 1):
            return {"code": 103, "message": "权限不足"}
        pic = self.session.query(Pics).filter_by(id=picid)
        if (accept):
            pic.update({Pics.status: 1, Pics.tips: tips})
        else:
            pic.update({Pics.status: 2, Pics.tips: tips})
        self.session.commit()
        return {"code": 0, "message": "OK"}
