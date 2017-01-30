from lsinf2172.dbms import Rel

'''
This module contains a simple enough example that shows how one interacts with Rel
using a simple python script. This should be the skeleton of the test harness developed
to evaluate students submissions.
'''

with Rel('databases/courses', run_student=False) as db:
    # ************************************ RELVAR DECLARATION ********************************
    db.execute('''
        VAR courses BASE RELATION {
        	id   CHAR,
        	name CHAR
        } KEY { id};''')

    db.execute('''
        INSERT courses RELATION {
        	TUPLE {name 'Database',  id 'LINGI2172'},
        	TUPLE {name 'Compilers', id 'LINGI2131'},
        	TUPLE {name 'MCP2',      id 'LINGI2224'},
        	TUPLE {name 'Meth',      id 'LINGI2251'},
        	TUPLE {name 'Dist.Sys',  id 'LINGI2345'}
        };''')

    # ************************************ IMPURITIES     ************************************
    # This is of course an examble (BUT an useful one): it reminds us of
    # the way to execute impure statements (such as DISPLAYING a relation value)
    db.execute('''OUTPUT courses;''')

    print(db.result())
