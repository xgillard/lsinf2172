# 
# Docker container for the Databases (LSINF2172) exercises grading on INGInious.
# Basically, this container bundles:
# - INGInious base (centos)
# - Python3 + the `lsinf2172` module (installed from PyPI)
# - Java8 and Scala
# - Rel (the relational database that implements Tutorial D as an instance of the relational algebra)
# - sqlite3 (to evaluate the SQL based exercises)
#
# Author: X. Gillard
# Date  : Jan. 30, 2017
#

# Extend the `java8scala` container that comes already fledged with java8
# (python3 is also insalled by default)

FROM  ingi/inginious-c-java8scala
LABEL org.inginious.grading.name="databases"


# sqlite3 is installed by default on centos. This line is only present to make
# things explicit and emphasize on the fact that it is indeed required.
# RUN yum install -y sqlite

# Add the lsinf2172 library that bundle REL already
RUN pip3.5 install lsinf2172-inginious-utils==1.0rc11


