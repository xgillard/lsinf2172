from lsinf2172.dbms import SQL

'''
This module contains a simple enough example that shows how one interacts with Rel
using a simple python script. This should be the skeleton of the test harness developed
to evaluate students submissions.
'''

with SQL('../sqlite/databases/1.db', run_student=False) as db:
    db.execute('select * from people;')

    print(db.result())
