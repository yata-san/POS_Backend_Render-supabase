import platform
print("platform", platform.uname())

from sqlalchemy.orm import sessionmaker
import json

from db_control.connect_supabase import engine

def myselect(mymodel, key_value, key_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(mymodel).filter(getattr(mymodel, key_name) == key_value)
    try:
        with session.begin():
            result = query.all()
        result_dict_list = []
        for obj in result:
            result_dict = {col: getattr(obj, col) for col in obj.__table__.columns.keys()}
            result_dict_list.append(result_dict)
        result_json = json.dumps(result_dict_list, ensure_ascii=False)
    except Exception as e:
        print("取得に失敗しました:", e)
        result_json = None
    session.close()
    return result_json
