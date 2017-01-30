'''
The :mod:`lsinf2172.dbms` module provides context managers that facilitate the
writing of DBMS related INGInious tests.

Concreteley, it provides:

+ :class:`Rel` that encapsulates the interaction with the Rel DBMS
+ :class:`SQL` that encapsulates the interaction with the chosen SQL DBMS
  (here SQLite)


.. note::
    The `SQL` context is certainly not the most efficient way to interact with
    the chosen DBMS but at least, it provides the same interface as the one of
    `Rel`.

Author: X. Gillard
Date  : Jan. 26, 2017
'''

import shutil
import os
import os.path
from subprocess import Popen, PIPE

class DBMSContext:

    def __init__(self, database, proc_home='.', run_student=True):
        '''
        Creates a new instance of the Rel context manager

        :param database:    the relative path of the database to use when running the
                            tests. Pay attention though, this path can be rooted
                            in `student`. Hence, you should *NEVER EVER* reference a
                            database that resides in a parent directory.
        :param proc_home:   the (relative or absolute) path to the folder where the
                            process is going to be executed
        :param run_student: a flag indicating whether or not you want the subprocess
                            to be spawned and executed inside a new container
                            (in a student context in inginious parlance).
        '''
        self._database    = database
        self._proc_home   = os.path.abspath(proc_home)
        self._process     = None
        self._result      = None
        self._run_student = run_student

    def __enter__(self):
        '''
        Initializes the context.
        That is to say, starts a subprocess and waits for user input
        '''
        self.__ensure_runtime_resources()
        cmd_pattern     = "run_student {}" if self._run_student else "{}"
        self._process   = Popen(
                            cmd_pattern.format(self.command()),
                            cwd=self.home(),
                            stdin=PIPE,
                            stdout=PIPE,
                            shell=True)

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        '''
        Finalizes the context:
        Makes sure the result is set and the underlying process closed.
        '''
        if self._process is not None:
            self._result  = self.result()
            self._process.terminate()
            self._process = None
        return False

    def __set_result(self):
        '''
        Makes sure that the `result()` is able to yield a decent value and
        ignores everything related to the database closure.
        '''
        self._process.stdin.close()
        self._result = str(self._process.stdout.read(), 'utf-8')

    def __ensure_runtime_resources(self):
        '''
        This command makes sure that the runtime will be able to access all the
        resources it needs. In particular, this means that this function ensures
        that all the resources (database + potential dbms engine) required to run
        a student script will be made available to that script.
        '''
        if self._run_student:
            # When the database is pre-existent, is obviously needed !
            if os.path.exists(self._database):
                target_location = "./student/{}".format(self._database)
                
                # but it probably needs to be wiped off if already present in the student folder
                if os.path.exists(target_location):
                    rm_anything = shutil.rmtree if os.path.isdir(target_location) else os.remove
                    rm_anything(target_location)
                    
                self.__copy_resource(self._database, target_location)

            # copy additional resources if need be
            for res_name, res_path in self.runtime_requires().items():
                destination = "./student/{}".format(res_name)
                if not os.path.exists(destination):
                    shutil.copytree(res_path, destination)

    def __copy_resource(self, resource, dest):
        '''
        Copies any resource (be it a file or directory) to the desired location
        :param resource: path of the resource (what) that needs to be copied
        :param dest:     path of the location where to copy it
        '''
        copy_anything = shutil.copytree if os.path.isdir(resource) else shutil.copy2
        copy_anything(resource, dest)

    def execute(self, statement):
        '''
        Executes one statement on the running database.

        :param statement: the Rel statement to execute.
        '''
        if self._result:
            raise ValueError("You can't keep executing statements after collecting the result")
        self._process.stdin.write( bytes(statement+'\n', 'utf-8') )

    def result(self):
        '''
        :return: The combined output of all the commands that have been
                 `execute`d().
        '''
        if not self._result:
            self.__set_result()

        return self._result
        
    def database(self):
        '''
        :retrun: the database location
        '''
        base_path = ('./student/{}' if self._run_student else '{}')
        relative  = base_path.format(self._database)
        return os.path.abspath(relative)

    def home(self):
        '''
        :return: the subprocess' home directory
        '''
        return self._proc_home

    def command(self):
        '''
        :return: the command to be executed to spawn the DBMS subprocess so as
                 to allow interaction.

        .. warning::
            This method *must* be overridden by the subclasses.

        .. note::
            The subclass implementations are encouraged to use the following
            methods :

            + database()
            + home()
        '''
        pass

    def runtime_requires(self):
        '''
        :return: a dict {res_name : path } of paths to the resources that
                 are required at runtime in order to correctly run the DBMS
                 and its queries/statements
        '''
        return {}


class Rel(DBMSContext):
    '''
    This class implements an easy to use wrapper around the RelDBMS whichone is
    going to greatly help us writing maintainable / understandable tests for the
    INGInious-based student exercises.

    .. example::
        #
        # Assuming `self` is a Nose test instance (thus having assertEqual()),
        # one can write the following snippet to test the content of the
        # sys.Catalog
        #
        with Rel('./db1') as db:
            db.execute('sys.Catalog')

            self.assertEqual(db.result(), '... something very long ...')
    '''

    def __init__(self, database, run_student=True):
        '''
        Creates a new instance of the Rel context manager

        :param database:    the relative path of the database to use when running the
                            tests. Pay attention though, this path can be rooted
                            in `student`. Hence, you should *NEVER EVER* reference a
                            database that resides in a parent directory.
        :param run_student: a flag indicating whether or not you want the subprocess
                            to be spawned and executed inside a new container
                            (in a student context in inginious parlance).
        '''
        home_base = "./student" if run_student else os.path.dirname(os.path.abspath(__file__))
        rel_home  = os.path.join(home_base, 'resources/Rel-standalone')

        super().__init__(database, rel_home, run_student)

        # This is RelDBMS specific: we only want to keep the relevant payload
        # that resides between the begin and end marks
        self.__begin = '\nOk.\n'
        self.__end   = 'Closing database in'

    def runtime_requires(self):
        '''
        Declares that the Rel environment needs to have access to the `Rel-standalone`
        folder and its content
        '''
        return {'resources': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')}

    def command(self):
        cmd_pattern = "java -classpath {home} -jar RelDBMS.jar -f{db}"
        return cmd_pattern.format(home=self.home(), db=self.database())

    def __crop_irrelevant(self, x):
        _start = x.find(self.__begin) + len(self.__begin)
        _end   = x.find(self.__end)
        return x[_start:_end]

    def result(self):
        '''
        Overrides the default behavior to keep relevant payload only
        '''
        if not self._result:
            self._result = self.__crop_irrelevant(super().result())
        return self._result


class SQL(DBMSContext):
    '''
    This class implements an easy to use wrapper around SQLite3 whichone is
    going to greatly help us writing maintainable / understandable tests for the
    INGInious-based student exercises (even though it isn't the most efficient
    way to interact with SQLite3).

    .. example::
        #
        # Assuming `self` is a Nose test instance (thus having assertEqual()),
        # one can write the following snippet to test the content of the
        # sys.Catalog
        #
        with SQL('./db1.db') as db:
            db.execute('select * from people;')

            self.assertEqual(db.result(), '... something very long ...')
    '''

    def __init__(self, database, run_student=True):
        '''
        Creates a new instance of the SQL context manager

        :param database:    the relative path of the database to use when running the
                            tests. Pay attention though, this path can be rooted
                            in `student`. Hence, you should *NEVER EVER* reference a
                            database that resides in a parent directory.
        :param run_student: a flag indicating whether or not you want the subprocess
                            to be spawned and executed inside a new container
                            (in a student context in inginious parlance).
        '''
        super().__init__(database, '.', run_student)

    def command(self):
        return "sqlite3 {}".format(self.database())
