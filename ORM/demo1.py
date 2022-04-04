# 导入:
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()

user = Table('user', metadata,
             Column('id', Integer, primary_key=True),
             Column('name', String(20)),
             )

color = Table('color', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(20)),
              )
engine = create_engine("mysql+pymysql://root:123@127.0.0.1:3306/test", max_overflow=5)

metadata.create_all(engine)

# 初始化数据库连接:
# engine = create_engine('mysql+pymysql://root:123@localhost:3306/test')
# # 创建DBSession类型:
# DBSession = sessionmaker(bind=engine)