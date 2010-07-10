SPEAR
=====

The reference implementation of the SPEAR ranking algorithm in Python.

Features
--------

The purpose of this implementation is to make the inner workings of the SPEAR algorithm easy to understand and not to distract or confuse the reader with highly optimized code.

The SPEAR algorithm takes a list of user activities on resources as input, and returns ranked lists of users by expertise scores and resources by quality scores, respectively.

Using SPEAR to simulate the HITS algorithm
------------------------------------------

You can also use this library to simulate the HITS algorithm of Jon Kleinberg. Simply supply a credit score function C(x) = 1 to the SPEAR algorithm (see documentation of Spear.run()).

Installation
------------

You can now download and install SPEAR from Python Package Index (aka Python Cheese Shop) via setuptools/easy_install. Just run

    $ easy_install Spear

After installation, a simple import deliciousapi in your Python scripts will do the trick.

An alternative installation method is downloading the code straight from the git repository.

Updates
-------

If you used setuptools/easy_install for installation, you can update Spear via

    $ easy_install -U Spear

Alternatively, if you downladed the code from the git repository, simply pull the latest changes.

Usage
-----

The algorithm requires a list of user activities on resources as input. More specifically, it requires a list of (timestamp, user, resource) tuples.

    >>> import spear
    >>> activities = [
    ... (datetime.datetime(2010,7,1,9,0,0), "alice", "http://www.quuxlabs.com/"),
    ... (datetime.datetime(2010,8,1,12,45,0), "bob", "http://www.quuxlabs.com/"),
    ... ]
    >>> spear_algorithm = spear.Spear(activities)
    >>> expertise_results, quality_results = spear_algorithm.run()

Get the top user and his expertise score:

    >>> expertise_score, user = expertise_results[0]
    >>> print "%s => %.4f" % (user, expertise_score)
    alice => 0.5858

Get the top resource and its quality score:

    >>> quality_score, resource = quality_results[0]
    >>> print "%s => %.4f" % (resource, quality_score)
    http://www.quuxlabs.com/ => 1.0000

More information
----------------

You can find more information about the SPEAR algorithm at:

* [http://www.spear-algorithm.org/](http://www.spear-algorithm.org/)
* [Telling Experts from Spammers: Expertise Ranking in Folksonomies](http://portal.acm.org/citation.cfm?id=1571941.1572046)  
  Michael G. Noll, Ching-man Au Yeung, et al.  
  SIGIR 09: Proceedings of 32nd International ACM SIGIR Conference
  on Research and Development in Information Retrieval, Boston, USA,
  July 2009, pp. 612-619, ISBN 978-1-60558-483-6

License
-------

The code is licensed to you under version 2 of the GNU General Public License.

Copyright
---------

Copyright 2009-2010 Michael G. Noll <http://www.michael-noll.com/>, Ching-man Au Yeung <http://www.albertauyeung.com/>

