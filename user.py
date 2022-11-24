import config
import jwt
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    email = Column(String(64), unique=True)
    group = Column(Integer)
    password = Column(String(64))

    def __init__(self, name, email, group, password):
        self.name = name
        self.email = email
        self.group = group
        self.password = password


class User():

    def __init__(self):
        self.sql = sqlalchemy.create_engine(config.SQL_URL)
        self.sql.connect()
        self.session = sessionmaker(self.sql)()

    def setup(self):
        Base.metadata.create_all(self.sql)

    def close(self):
        self.session.commit()
        self.session.close()

    def sendMail(self, to: str, msg: MIMEMultipart):
        """
        发送邮件

        参数:
          to - 发送到邮件地址
          msg - 邮件内容
        """
        smtp = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
        smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
        msg['From'] = config.SMTP_USER
        msg['To'] = to
        smtp.sendmail(config.SMTP_USER, to, msg.as_bytes())

    def userExist(self, name: str):
        """
        验证用户是否存在

        参数:
          name - 用户名
        """
        if (self.session.query(Users).filter_by(name=name).first()):
            return True
        else:
            return False

    def emailExist(self, email: str):
        """
        验证邮箱是否已注册

        参数:
          email - 邮箱
        """
        if (self.session.query(Users).filter_by(email=email).first()):
            return True
        else:
            return False

    def checkUser(self, token: str):
        """
        验证登录是否有效

        参数:
          token - AccessToken
        """
        if (token == ""):
            return {"code": 101, "message": "请先登录"}
        try:
            obj = jwt.decode(token, key=config.SECRET_KEY,
                             algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {"code": 102, "message": "登录状态已过期"}
        except:
            return {"code": 102, "message": "登录Token无效"}

        if (obj["type"] != "access_token"):
            return {"code": 102, "message": "登录Token无效"}

        user = self.session.query(Users).filter_by(name=obj["name"]).first()
        if (user):
            if (user.group == obj["group"]):
                return {"code": 0, "name": user.name, "group": user.group}
            else:
                return {"code": 102, "message": "登录状态已过期"}
        else:
            return {"code": 100, "message": "用户不存在"}

    def login(self, name: str, password: str):
        """
        用户登录

        参数:
          name - 用户名
          password - 密码
        """
        user = self.session.query(Users).filter_by(name=name).first()
        if (user and user.password == password):
            payload = {"exp": int(time.time(
            )) + 86400, "type": "access_token", "name": user.name, "group": user.group}
            token = jwt.encode(payload=payload, key=config.SECRET_KEY)
            return {"code": 0, "message": "OK", "access_token": token}
        else:
            return {"code": 104, "message": "用户名或密码错误"}

    def getUserInf(self, name: str, token: str):
        """
        获取用户信息

        参数:
          name - 用户名
          token - AccessToken
        """
        user = self.checkUser(token)
        if (user["code"] != 0):
            return user
        if (user["group"] < 2 and user["name"] != name):
            return {"code": 103, "message": "权限不足"}
        if (not self.userExist(name)):
            return {"code": 100, "message": "用户不存在"}
        u = self.session.query(Users).filter_by(name=name).first()
        return {"code": 0, "message": "OK", "user_name": u.name, "email": u.email, "group": u.group}

    def getUserList(self, token: str):
        """
        获取用户列表

        参数:
          token - AccessToken
        """
        user = self.checkUser(token)
        if (user["code"] != 0):
            return user
        if (user["group"] < 2):
            return {"code": 103, "message": "权限不足"}
        users = self.session.query(Users).all()
        userarr = []
        for u in users:
            userarr.append(
                {"user_name": u.name, "email": u.email, "group": u.group})
        return {"code": 0, "message": "OK", "list": userarr}

    def changePassword(self, name: str, new_password: str, old_password: str = "", token: str = ""):
        """
        修改用户密码，若缺省 old_password 则必须为系统管理员权限

        参数:
          name - 用户名
          new_password - 新密码
          old_password - 旧密码
          token - AccessToken
        """
        if (not self.userExist(name)):
            return {"code": 100, "message": "用户不存在"}
        u = self.session.query(Users).filter_by(name=name)
        if (old_password != ""):
            if (u.first().password != old_password):
                return {"code": 104, "message": "用户名或密码错误"}
        elif (token != ""):
            user = self.checkUser(token)
            if (user["code"] != 0):
                return user
            if (user["group"] < 2):
                return {"code": 103, "message": "权限不足"}
        else:
            return {"code": 400, "message": "必须具有 old_password 或 access_token 之一"}
        u.update({Users.password: new_password})
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def setGruop(self, name: str, group: int, token: str):
        """
        设置用户的用户组，需要管理员权限

        参数:
          name - 用户名
          group - 用户组
          token - AccessToken
        """
        user = self.checkUser(token)
        if (user["code"] != 0):
            return user
        if (user["group"] < 2):
            return {"code": 103, "message": "权限不足"}
        if (not self.userExist(name)):
            return {"code": 100, "message": "用户不存在"}
        self.session.query(Users).filter_by(
            name=name).update({Users.group: group})
        self.session.commit()
        return {"code": 0, "message": "OK"}

    def register(self, name: str, email: str, password: str):
        """
        注册账号，将发送验证邮件到注册邮箱。

        参数:
          name - 用户名
          email - 用户组
          token - AccessToken
        """
        if (self.userExist(name)):
            return {"code": 105, "message": "用户名已存在"}
        if (self.emailExist(email)):
            return {"code": 106, "message": "邮箱已存在"}
        payload = {"exp": int(time.time()) + 86400, "type": "register",
                   "name": name, "email": email, "password": password}
        token = jwt.encode(payload=payload, key=config.SECRET_KEY)
        confirmUrl = f"{config.URL_BASE}/api/userAction?token={token}"
        msg = MIMEMultipart()
        msg['Subject'] = Header('【梧桐故里】注册新用户验证', 'utf-8').encode()
        msg.attach(MIMEText(
            f'您正在注册梧桐故里账号，请点击<a href=\"{confirmUrl}\">此处</a>验证邮箱', 'html', 'utf-8'))
        self.sendMail(email, msg)
        return {"code": 0, "message": "已发送验证邮件"}

    def userAction(self, token: str):
        """
        执行已通过的用户操作

        参数:
          token - 操作Token
        """
        try:
            obj = jwt.decode(token, key=config.SECRET_KEY,
                             algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {"code": 102, "message": "请求已过期"}
        except:
            return {"code": 102, "message": "操作Token无效"}

        if (obj["type"] == "register"):
            if (self.userExist(obj["name"])):
                return {"code": 105, "message": "用户已存在"}
            if (self.emailExist(obj["email"])):
                return {"code": 106, "message": "邮箱已存在"}
            user = Users(name=obj["name"], email=obj["email"],
                         group=0, password=obj["password"])
            self.session.add(user)
            self.session.commit()
            return {"code": 0, "message": "OK"}

        if (obj["type"] == "setpassword"):
            if (not self.userExist(obj["name"])):
                return {"code": 100, "message": "用户不存在"}
            self.session.query(Users).filter_by(name=obj["name"]).update(
                {Users.password: obj["password"]})
            self.session.commit()
            return {"code": 0, "message": "OK"}
