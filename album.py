import config
from user import User
from pic import Pic
import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()


class Albums(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True)
    title = Column(String(64))
    cover = Column(Integer)
    user = Column(String(32))
    primary = Column(Boolean)
    private = Column(Boolean)
    description = Column(String(1024))
    pics = Column(String(1024))

    def __init__(self, title, cover, user, primary, private, description):
        self.title = title
        self.cover = cover
        self.user = user
        self.primary = primary
        self.private = private
        self.description = description
        self.pics = "[]"


class Album():

    def __init__(self):
        self.sql = sqlalchemy.create_engine(config.SQL_URL)
        self.sql.connect()
        self.session = sessionmaker(self.sql)()

    def setup(self):
        Base.metadata.create_all(self.sql)

    def close(self):
        self.session.commit()
        self.session.close()

    def getPrimaryAlbumId(self, user_name: str):
        """
        通过用户名获取收藏图片集ID

        参数:
          name - 用户名
        """
        if (User().userExist(name=user_name)):
            alb = self.session.query(Albums).filter_by(
                user=user_name).filter_by(primary=True).first()
            if (alb):
                return alb.id
            else:
                alb = Albums(title=f"{user_name} 的收藏", user=user_name, cover=-1,
                             primary=True, private=True, description=f"{user_name} 的收藏")
                self.session.add(alb)
                self.session.commit()
                return alb.id
        else:
            return -1

    def getAlbum(self, token: str, albid: int):
        """
        获取图片集信息

        参数:
          token - AccessToken
          albid - 图片集ID
        """
        alb = self.session.query(Albums).filter_by(id=albid).first()
        if (not alb):
            return {"code": 404, "message": "图片集不存在"}
        if (alb.private):
            user = User().checkUser(token=token)
            if (user["code"] != 0):
                return user
            if (user["name"] != alb.user):
                return {"code": 403, "message": "拒绝访问：图片集为私有"}
        return {"code": 0, "message": "OK", "title": alb.title, "cover": alb.cover, "user": alb.user, "list": json.loads(alb.pics)}

    def createAlbum(self, token: str, title: str, cover: int, primary: bool, private: bool, description: str):
        """
        创建图片集

        参数:
          token - AccessToken
          title - 图片集标题
          primary - 是否为收藏图片集
          private - 是否为私有图片集
          description - 图片集描述
        """
        user = User().checkUser(token)
        if (user["code"] != 0):
            return user
        alb = Albums(
            title=title, cover=cover, user=user["name"], primary=primary, private=private, description=description)
        self.session.add(alb)
        self.session.commit()
        return {"code": 0, "message": "OK", "albid": alb.id}

    def removeAlbum(self, token: str, albid: int):
        """
        删除图片集

        参数:
          token - AccessToken
          albid - 图片集ID
        """
        user = User().checkUser(token=token)
        if (user["code"] != 0):
            return user
        alb = self.session.query(Albums).filter_by(id=albid)
        if (not alb.first()):
            return {"code": 404, "message": "图片集不存在"}
        if (user["name"] != alb.first().user and user["group"] < 1):
            return {"code": 103, "message": "权限不足"}
        alb.delete()
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def setAlbumCover(self, token: str, albid: int, picid: int):
        """
        设置图片集封面

        参数:
          token - AccessToken
          albid - 图片集ID
          picid - 图片ID
        """
        user = User().checkUser(token=token)
        if (user["code"] != 0):
            return user
        alb = self.session.query(Albums).filter_by(id=albid)
        if (not alb.first()):
            return {"code": 404, "message": "图片集不存在"}
        if (user["name"] != alb.first().user and user["group"] < 1):
            return {"code": 103, "message": "权限不足"}
        if (not Pic().picExist(picid=picid)):
            return {"code": 404, "message": "图片不存在"}
        alb.update({Albums.cover: picid})
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def addToAlbum(self, token: str, albid: int, picid: int):
        """
        加入图片集

        参数:
          token - AccessToken
          albid - 图片集ID
          picid - 图片ID
        """
        user = User().checkUser(token=token)
        if (user["code"] != 0):
            return user
        alb = self.session.query(Albums).filter_by(id=albid)
        if (not alb.first()):
            return {"code": 404, "message": "图片集不存在"}
        if (user["name"] != alb.first().user and user["group"] < 1):
            return {"code": 103, "message": "权限不足"}
        if (not Pic().picExist(picid=picid)):
            return {"code": 404, "message": "图片不存在"}
        pics = json.loads(alb.first().pics)
        if (picid not in pics):
            pics.append(picid)
            if (alb.first().primary):
                Pic().picFav(picid=picid, addOrRemove=True)
        alb.update({Albums.pics: json.dumps(pics)})
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def removeFromAlbum(self, token: str, albid: int, picid: int):
        """
        从图片集删除

        参数:
          token - AccessToken
          albid - 图片集ID
          picid - 图片ID
        """
        user = User().checkUser(token=token)
        if (user["code"] != 0):
            return user
        alb = self.session.query(Albums).filter_by(id=albid)
        if (not alb.first()):
            return {"code": 404, "message": "图片集不存在"}
        if (user["name"] != alb.first().user and user["group"] < 1):
            return {"code": 103, "message": "权限不足"}
        if (not Pic().picExist(picid=picid)):
            return {"code": 404, "message": "图片不存在"}
        pics = json.loads(alb.first().pics)
        if (picid in pics):
            pics.remove(picid)
            if (alb.first().primary):
                Pic().picFav(picid=picid, addOrRemove=False)
        alb.update({Albums.pics: json.dumps(pics)})
        self.session.commit()
        return {"code": 0, "message": "OK"}
