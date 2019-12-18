from redis import Redis
import json
import pandas as pd


redis = Redis()

items = redis.lrange('newhouseprice:items', 0, -1)


tf_zz_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])
tf_gy_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])

gx_zz_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])
gx_gy_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])

sy_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])
zz_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])
ds_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])
bs_dataform = pd.DataFrame(columns=['name', 'type', 'price', 'location', 'area'])

for item in items:
    data = json.loads(item)
    if data['type'] == '商业类':
        sy_dataform = sy_dataform.append(data, ignore_index=True)
        if data['location'].startswith('天府新区'):
            tf_gy_dataform = tf_gy_dataform.append(data, ignore_index=True)
        elif data['location'].startswith('高新'):
            gx_gy_dataform = gx_gy_dataform.append(data, ignore_index=True)
    elif data['type'] == '住宅':
        zz_dataform = zz_dataform.append(data, ignore_index=True)
        if data['location'].startswith('天府新区'):
            tf_zz_dataform = tf_zz_dataform.append(data, ignore_index=True)
        elif data['location'].startswith('高新'):
            gx_zz_dataform = gx_zz_dataform.append(data, ignore_index=True)
    elif data['type'] == '底商':
        ds_dataform = ds_dataform.append(data, ignore_index=True)
    elif data['type'] == '别墅':
        bs_dataform = bs_dataform.append(data, ignore_index=True)

with pd.ExcelWriter('房价信息.xlsx') as writer:
    sy_dataform.to_excel(writer, sheet_name='商业类')
    zz_dataform.to_excel(writer, sheet_name='住宅类')
    ds_dataform.to_excel(writer, sheet_name='底商类')
    bs_dataform.to_excel(writer, sheet_name='别墅类')

with pd.ExcelWriter('区域房价.xlsx') as writer:
    tf_zz_dataform.to_excel(writer, sheet_name='天府新区住宅')
    tf_gy_dataform.to_excel(writer, sheet_name='天府新区公寓')
    gx_zz_dataform.to_excel(writer, sheet_name='高新区住宅')
    gx_gy_dataform.to_excel(writer, sheet_name='高新区公寓')




