# 梧桐图库后端API

## 图库操作

### 获取图片信息

- 获取图片的基本信息及Url

#### 调用地址

api/getPicInf (GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picid|true|int|图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|title|string|标题|
|category|string|分类|
|tag|array\<string\>|标签|
|url|string|图片Url|
|user|string|投稿用户|
|by|string|作者|
|creation_time|string|创建时间|
|view|int|访问人数|
|fav|int|收藏人数|

### 查找图片

- 按标题、分类、标签、用户或作者查找图片

#### 调用地址

api/searchPic (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|sort|flase|int|结果排序 0:按更新时间 1:按图片收藏人数|
|limit|false|int|最大返回结果数目，默认为20|
|offset|false|int|从第几条数据开始查询|
|title|flase|string|图片标题|
|category|flase|string|分类|
|tag|false|string|标签|
|user|false|string|投稿用户|
|by|false|string|作者|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|list|array|返回数据|

##### 返回字段 "list" 子项

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|picid|int|图片ID|
|title|string|标题|
|category|string|分类|
|tag|array\<string\>|标签|
|url|string|图片Url|
|user|string|投稿用户|
|by|string|作者|
|creation_time|string|创建时间|
|view|int|访问人数|
|fav|int|收藏人数|

### 修改图片信息

- 修改图片标题、作者、分类、标签等信息（权限：上传者或管理员）

#### 调用地址

api/changePicInf (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picid|true|int|图片ID|
|title|flase|string|标题|
|by|false|string|作者|
|category|false|string|分类|
|tag|false|string|标签|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

## 图片集操作

### 获取图片集

- 获取图片集的名称、封面以及内容

#### 调用地址

api/getAlbum (GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|albid|true|int|图片集ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|title|string|图片集标题|
|cover|int|封面图片ID|
|cover_url|string|封面图片Url|
|user|string|图片集创建者|
|list|array\<int\>|返回图片集 picid 列表|

### 创建图片集

- 创建一个图片集 （权限：普通用户）

#### 调用地址

api/createAlbum (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|title|true|string|图片集标题|
|cover|true|int|封面图片ID|
|description|false|string|图片集描述|
|private|false|bool|是否设为私有|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|albid|int|图片集ID|

### 删除图片集

- 删除一个图片集 （权限：创建者或管理员）

#### 调用地址

api/removeAlbum (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|albid|true|int|图片集ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 设置图片集封面

- 设置一个图片集的封面 （权限：创建者）

#### 调用地址

api/setAlbumCover (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|albid|true|int|图片集ID|
|cover|true|int|封面图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 加入图片集

- 将图片加入图片集 （权限：创建者）

#### 调用地址

api/addToAlbum (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|albid|true|int|图片集ID|
|picid|true|int|图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 从图片集删除

- 将图片从图片集删除 （权限：创建者）

#### 调用地址

api/removeFromAlbum (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|albid|true|int|图片集ID|
|picid|true|int|图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

## 用户操作

### 登录

- 以一个用户身份登录

#### 调用地址

api/login (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|user_name|true|string|用户名|
|password|true|string|密码|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|access_token|string|用户访问令牌(有效期一天)|

### 登出

- 登出用户

#### 调用地址

api/logout (GET)

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 获取用户信息

- 缺省 user 字段，获取登录用户信息 （权限：普通用户）
- 填入 user 字段，获取任意用户信息（权限：系统管理员）

#### 调用地址

api/getUserInf (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|user_name|flase|string|用户名|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|user_name|string|用户名|
|email|string|邮箱|
|group|string|用户组|

### 注册

- 注册一个账户

#### 调用地址

api/register (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|user_name|true|string|用户名|
|password|true|string|密码|
|email|true|string|邮箱|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 获取用户列表

- 获取全部用户列表 （权限：系统管理员）

#### 调用地址

api/getUserList (GET)

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|list|array|返回结果|

##### 返回字段 "list" 子项

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|user_name|string|用户ID|
|email|string|邮箱|
|group|int|用户组|

### 设置用户组

- 为一个账户设置用户组 （权限：系统管理员）

#### 调用地址

api/setGroup (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|user_name|true|string|用户名|
|group|true|int|用户权限 0:普通用户 1:图库管理员 2:系统管理员|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 修改密码

- 验证旧密码修改密码 （权限：普通用户）
- 缺省旧密码设置密码 （权限：系统管理员）

#### 调用地址

api/changePassword (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|user_name|true|string|用户名|
|old_password|flase|string|旧密码|
|new_password|true|string|新密码|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

## 收藏

### 收藏图片

- 收藏一张图片 （权限：普通用户）

#### 调用地址

api/addFav (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picid|true|int|图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

### 取消收藏图片

- 取消收藏一张图片 （权限：普通用户）

#### 调用地址

api/removeFav (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picid|true|int|图片ID|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

## 投稿与管理

### 投稿图片

- 投稿一张图片并等待管理员审核（权限：普通用户）

#### 调用地址

api/uploadPic (POST)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|title|true|string|标题|
|by|true|string|作者|
|category|true|string|分类|
|tag|true|string|标签|
|data|true|bytes|图片数据|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|picid|int|图片ID|

### 获取未通过审核投稿列表

- 获取所有投稿 （权限：管理员）
- 获取自己的投稿 （权限：普通用户）

#### 调用地址

api/getSubmissions (GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|status|false|int|指定投稿状态，默认为 0:待审核|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|
|list|array|返回数据|

##### 返回字段 "list" 子项

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|picid|int|图片ID|
|title|string|标题|
|category|string|分类|
|tag|array\<string\>|标签|
|url|string|图片Url|
|user|string|投稿用户|
|by|string|作者|
|creation_time|string|创建时间|
|status|int|投稿状态 0:待审核 1:已通过 2:已拒绝|
|tips|string|管理员信息|

### 通过投稿

- 通过指定投稿 （权限：管理员）

#### 调用地址
api/acceptSubmission (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picids|true|int|图片ID|
|tips|false|int|管理员信息|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|flase|string|提示信息|

### 拒绝投稿

- 拒绝指定投稿 （权限：管理员）

####  调用地址
api/rejectSubmission (POST/GET)

#### 参数

|字段|必选|类型|说明|
|----|----|----|----|
|picid|true|int|图片ID|
|tips|flase|string|管理员信息|

#### 返回

|返回值字段|字段类型|字段说明|
|----------|--------|--------|
|code|int|返回代码|
|message|string|提示信息|

## 返回代码

|代码|说明|
|-----|-----|
|0|成功|
|100|用户不存在|
|101|需要登录|
|102|Token无效|
|103|用户权限不足|
|104|用户名或密码错误|
|105|用户名已存在|
|106|邮箱已存在|
|400|参数错误|
|403|拒绝访问|
|404|资源不存在|
|500|服务器内部错误|
|503|请求过快|
