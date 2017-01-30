#! /usr/bin/python3

'''
This module provide the basis classes for the 'puzzle' tasks

Author: X. Gillard
Date  : Jan. 26, 2017
'''

from lsinf2172.dbms      import SQL
from difflib             import ndiff
from textwrap            import indent

from inginious.input     import get_input
from inginious.feedback  import set_problem_result,  \
                                set_problem_feedback,\
                                set_global_result,\
                                set_global_feedback,\
                                set_grade
                                
class Puzzle:
    '''
    This class provides the basic evaluation harness to provide feedback and
    grade a 'puzzle'-like submission.
    
    .. note:: 
    
        In order to actually be usable, this class should be completed with an
        implementation of the `get_student_output()` method.
    '''
    def __init__(self, questions, databases):
        self._questions = questions
        self._databases = databases

    def get_student_output(self, question, db):
        '''
        :return: the student output for `question` when evaluated on `db`
        '''
        pass

    def get_expected_output(self, question, db):
        '''
        :return: the expected (prof) output for `question` when evaluated on `db`
        '''
        with open('questions/{qid}/output-db{db}'.format(qid=question, db=db)) as f:
            return sorted( f.read().splitlines() )

    def diff_expected_vs_student(self, question, db):
        '''
        Compares the expected result vs the student's and returns a delta (list of
        strings) containing only the differences between the two results.

        Items present in the student's result which are not present in the prof's
        are prefixed with a '+'. Similarly, items present in the prof's result and
        absent from the student's are prefixed with a '-'.

        .. note::
            As opposed to a regular diff, the lines that are common to both results
            are filtered out.
        '''
        expect = self.get_expected_output(question, db)
        student= self.get_student_output( question, db)

        # compute a diff of the files
        diffs  = ndiff(expect, student)
        # filter out the common subsequences
        diffs = filter(lambda x: not x.startswith(' '), diffs)

        return list(diffs)
        
    def to_rst(self, lines):
        '''
        This function takes a set of lines and formats them so as to produce a valid
        rst snippet
        '''
        _rst = '\n{}\n'.format('\n'.join(lines))
        
        # Level 1 should already be ok
        # Level 2
        _rst = indent(_rst, " "*4, lambda x: x.startswith("+") or x.startswith('-'))
        
        return _rst

    def evaluate_submission(self, question, db):
        '''
        This function evaluates the student's submission for `question` on `db`.
        It returns a tuple (<result>, <feedback-msg>) containing relevant information
        that can later be combined into a more sensible message (if many questions
        need to be agregated).

        :return: a tuple (<result>, <feedback-msg>)
        '''
        differences= self.diff_expected_vs_student(question, db)

        message    = None
        status     = None

        if len(differences) == 0:
            status  = 'success'
            message = "* Your query returns the correct result on DB-{}!".format(db)
        else:
            status  = 'failed'

            missing = list(filter(lambda x: x.startswith('-'), differences))
            extra   = list(filter(lambda x: x.startswith('+'), differences))
            
            message = '* Your query returns a wrong result on DB-{}.\n'.format(db)

            if extra:
                message += '    * Here are some incorrectly reported tuples: \n\n{}\n\n'\
                            .format('\n'.join(extra[:3]))
            if missing:
                message += '    * Here are some tuples missing from your result: \n\n{}\n\n'\
                            .format('\n'.join(missing[:3]))

        return (status, message)


    def main(self):
        '''
        This is the script main entry point: it evaluates a student's submission
        for all the questions and all databaeses and automatically provides a
        feedback and a grade for it.
        '''
        # Note: we might want to weight some question differently than other
        task_grade = 0.0

        for question in self._questions:
            problem_id = "question{}".format(question)
            evaluation = [ self.evaluate_submission(question, db) for db in self._databases ]

            feedback   = self.to_rst([ x[1] for x in evaluation ])
            nb_success = list(map(lambda x: x[0], evaluation)).count('success')
            pb_grade   = 100.0 * nb_success / len(evaluation)

            set_problem_result('success' if pb_grade == 100.0 else 'failed', problem_id)
            set_problem_feedback(feedback, problem_id)

            task_grade += pb_grade

        # Grade the whole task
        task_grade = ( task_grade / len(self._questions) )
        set_grade( task_grade )
        
        if task_grade == 100.0: 
            set_global_result('success')
            set_global_feedback('You successfully completed this task')
        else:
            set_global_result('failed')
            set_global_feedback('Keep trying to improve your solution')

