# import pandas as pd
# from schemalock import lock, check
# df = pd.DataFrame({'customer_id':[1,2,3],'email':['a@x.com','b@x.com','c@x.com']})
# lock(df, name='demo')
# print(check(df, name='demo'))


# import pandas as pd
# from schemalock import lock, check, SchemaDriftError

# df = pd.DataFrame({'customer_id':[1,2,3], 'email':['a@x.com','b@x.com','c@x.com']})
# # (assumes lock(df, name='demo') was already run — reuses the existing lock file)

# dropped = df.drop(columns=['email'])
# try:
#     check(dropped, name='demo')
# except SchemaDriftError as e:
#     print(e)


import pandas as pd
from schemalock import lock, check, SchemaDriftError

df = pd.DataFrame({'customer_id':[1,2,3], 'email':['a@x.com','b@x.com','c@x.com']})
# (assumes lock(df, name='demo') already exists)

retyped = df.copy()
retyped['customer_id'] = retyped['customer_id'].astype(str)   # int -> string

try:
    check(retyped, name='demo')
except SchemaDriftError as e:
    print(e)