"""
    The reference implementation of the SPEAR ranking algorithm in Python.

    The purpose of this implementation is to make the inner workings of
    the algorithm easy to understand and not to distract or confuse
    the reader with highly optimized code.

    The SPEAR algorithm takes a list of user activities on resources
    as input, and returns ranked lists of users by expertise scores
    and resources by quality scores, respectively.

    You can also use this library to simulate the HITS algorithm of
    Jon Kleinberg. Simply supply a credit score function C(x) = 1 to
    the SPEAR algorithm (see documentation of Spear.run()).

    More information about the SPEAR algorithm is available at:
    * http://www.spear-algorithm.org/
    * "Telling Experts from Spammers: Expertise Ranking in Folksonomies"
      Michael G. Noll, Ching-man Au Yeung, et al.
      SIGIR 09: Proceedings of 32nd International ACM SIGIR Conference
      on Research and Development in Information Retrieval, Boston, USA,
      July 2009, pp. 612-619, ISBN 978-1-60558-483-6

    The code is licensed to you under version 2 of the GNU General Public
    License.

"""
__author__ = "Michael G. Noll"
__copyright__ = "(c) 2009-2010 Michael G. Noll and Ching-man Au Yeung"
__description__ = "The reference implementation of the SPEAR ranking algorithm."
__email__ = "michael[AT]quuxlabs[DOT]com"
__license__ = "GPLv2"
__maintainer__ = "Michael G. Noll"
__status__ = "Development"
__url__ = "http://www.quuxlabs.com/"
__version__ = "1.0"

import datetime
import sys
import unittest

try:
    from scipy import sparse
    """
    Note: The following program makes use of the sparse matrix module in SciPy
          In general, a lil_matrix is created first as it provides more convenient indexing.
          The matrix will then be converted into a csr_matrix for faster computation of multiplications.
    """
    import numpy
except:
    print "ERROR: could not import SciPy or NumPy Python module"
    print ""
    print "You can download SciPy and NumPy at"
    print "http://www.scipy.org/Download"
    print
    raise


class Spear(object):

    def __init__(self, activities):
        """
            Initialize the SPEAR algorithm with input activities.

        @param A: List of (timestamp, user, resource) tuples.
            A (timestamp, user, resource) tuple represents that <user>
            'acted on' <resource> on date/time <timestamp>.

            Example:
            [
                (datetime.datetime(2010,7,1,9,0,0), "alice", "http://www.quuxlabs.com/"),
                (datetime.datetime(2010,8,1,12,45,0), "bob", "http://www.quuxlabs.com/"),
            ]
        @param type: list

        """
        self.activities = activities
        # Sort activity data by timestamp (oldest first).
        self.activities.sort()
        
        # Extract users and resources for later use.
        self._users = set()
        self._resources = set()
        for timestamp, user, resource in activities:
            self._users.add(user)
            self._resources.add(resource)

        # Assign IDs to users and resources.
        #
        # This is needed because scipy requires numerical values
        # for addressing cells in matrices.
        self._user2id = {}
        self._id2user = {}
        for id, user in enumerate(self.users):
            self._user2id[user] = id
            self._id2user[id] = user
        self._resource2id = {}
        self._id2resource = {}
        for id, resource in enumerate(self.resources):
            self._resource2id[resource] = id
            self._id2resource[id] = resource        
    
    def get_users(self):
        return self._users
    users = property(fget=get_users,
                     doc="Returns the set of users found in activities")
    
    def get_resources(self):
        return self._resources
    resources = property(fget=get_resources,
                         doc="Returns the set of resources found in activities")
    
    def _get_userid(self, user):
        return self._user2id[user]

    def _get_user(self, userid):
        return self._id2user[userid]
    
    def _get_resourceid(self, resource):
        return self._resource2id[resource]

    def _get_resource(self, resourceid):
        return self._id2resource[resourceid]

    def _populate(self, A):
        """
        Populates the adjacency matrix A for use with the discoverer-follower scheme.
    
        @param A: Empty adjacency matrix A (a numpy matrix), which maps users
            to resources.
        @param type: list
        
        @return: Populated adjacency matrix A (a numpy matrix).
    
        """
    
        # Calculate the number of actions per resource.
        #
        # In social bookmarking scenarios, for example, the number of actions
        # of a resource would be its number of bookmarks.
        num_actions = {}
        for timestamp, user, resource in self.activities:
            num_actions[resource] = num_actions.get(resource, 0) + 1
    
        # Number of users found so far who have acted on a resource.
        current_num_users = {}
    
        # Score to be assigned to the next user.
        #
        # The first user will receive a score equals to number of total actions + 1,
        # and the last user will receive a score of 1.
        #
        current_score = {}

        prev_timestamp_of_docs = {}
    
        # Each matrix cell stores the "action position" of user i
        # with regard to resource j.
        #
        # If there are 10 users with the follow timestamps (smaller
        # int values = earlier timestamps) for a resource j:
        #
        #     1, 1, 1, 2, 3, 3, 4, 4, 5, 6
        #
        # then their scores in the respective A[i,j] will be:
        #
        #     10, 10, 10, 7, 6, 6, 4, 4, 2, 1
        #
        for timestamp, user, resource in self.activities:
            # raise an error if timestamp is None because this
            # means there is an error in the input data which
            # we want to know about
            #
            assert timestamp is not None
            
            current_num_users.setdefault(resource, 0)
            if timestamp == prev_timestamp_of_docs.get(resource):
                A[self._get_userid(user),self._get_resourceid(resource)] = current_score[resource]
            else:
                current_score[resource] = num_actions[resource] - current_num_users[resource]
                A[self._get_userid(user),self._get_resourceid(resource)] = current_score[resource]
                prev_timestamp_of_docs[resource] = timestamp
            current_num_users[resource] += 1 
    
        return A

    def _apply_credit_scores(self, A, C):
        """
        Applies credit scores to the adjacency matrix A.
    
        @param A: Populated adjacency matrix A (a numpy matrix), which maps users to resources.
        @param type: list
        
        @param C: Credit score function C().
            See the documentation of C at Spear.run().
        @param type: A function that takes a numeric argument and returns a float 
        
        @return: Adjacency matrix A (a numpy matrix), with credit scores applied.
    
        """
        for i in xrange(len(A.data)):
            if A.data[i]:
                for j in xrange(len(A.data[i])):
                    A.data[i][j] = C(A.data[i][j])

        return A

    def run(self, iterations=250, C=lambda score: pow(score, 0.5), verbose=True):
        """
        Runs the SPEAR algorithm to find the Top users (experts) and resources.
    
        @param iterations: Number of iterations for the algorithm.
            Default: 250
        @param type: int
    
        @param C: Credit score function C().
            Default: the root function, i.e. C(x) = x^0.5
            
            The default value of C is the parameter used in the SPEAR
            publication "Telling Experts from Spammers" from SIGIR 2009.

            If you want to simulate HITS, supply the function C(x) = 1,
            for example through C=lambda x: 1.
            
            Please note that the credit score function will ALWAYS
            return a value of 0 (zero) for the input values of 0 (zero),
            regardless of the function passed for the parameter C.
            In other words, it is fixed that C(0) == 0.
        @param type: a function that takes a numeric argument and returns a float 

        @param verbose: If True (default), print some status information
            to STDOUT during computation.
        @param type: bool
    
        @return: A tuple of lists (expertise_results, quality_results), which
            contains ranked lists of (expertise_score, user) and (quality_score, resource)
            tuples, respectively. The lists are ranked, i.e. the best items are listed first.
    
        """
        # A: user-resource matrix (adjacency matrix)
        A = sparse.lil_matrix( (len(self.users), len(self.resources)) )
        
        if verbose:
            print "Step 1) Populating adjacency matrix A"
        A = self._populate(A)

        if verbose:
            print "Step 2) Applying credit score function C() to A"
        A = self._apply_credit_scores(A, C)

        A = A.tocsr()
    
        # E: expertise vector for users
        #
        # For the record, setting E to [1, 1, ..., 1] is not really needed
        # as E will be overwritten in the very first iteration step (E = Q x A^T).
        #
        E = numpy.ones(len(self.users))
    
        # Q: quality vector for resources
        #
        Q = numpy.ones(len(self.resources))
    
        # Update expertise and quality iteratively = mutual reinforcement
        #
        if verbose:
            print "Step 3) Mutual reinforcement using %d iterations ***this might take some time***" % (iterations)
        for i in xrange(iterations):
            # E is the y_p weight vector in the original HITS algorithm;
            # the next line is HITS' "O" operation, which is based on the
            # "out-degree" of Web pages; in our case, "out-degree" is not
            # computed by counting the number of pages qs to which a given
            # page p links to, but rather the number of resources qs a given
            # user p has 'acted on'
            #       HITS:
            #           p -> {q1, q2, q3, ...}
            #       SPEAR:
            #           user -> {resource1, resource2, resource3, ...}
            E = Q * A.T

            # Q is the x_p weight vector in the original HITS algorithm;
            # the next line is HITS' "I" operation, which is based on the
            # "in-degree" of web pages; in our case, "in-degree" is not
            # computed by counting the number of pages qs linking to a
            # given page p, but the number of users qs who 'acted on' a
            # given resource p
            #       HITS:
            #           p <- {q1, q2, q3, ...}
            #       SPEAR:
            #           resource <- {user1, user2, user3, ...}
            Q = E * A
    
            # normalization
            E = E / E.sum()
            Q = Q / Q.sum()

        if verbose:
            print "Step 4) Sorting vectors E and Q by expertise and quality scores, respectively"
        expertise_results = [ (expertise_score, self._get_user(userid)) for userid, expertise_score in enumerate(E) ]
        expertise_results.sort()
        expertise_results.reverse()
        quality_results = [ (quality_score, self._get_resource(resourceid)) for resourceid, quality_score in enumerate(Q) ]
        quality_results.sort()
        quality_results.reverse()
    
        return expertise_results, quality_results


class SpearTester(unittest.TestCase):

    def testSpearOnSampleData(self):
        
        USERS = ["Steve Jobs", "Bill Gates", "Sergey Brin", "Larry Page"]
        RESOURCES = ["D1", "D2", "D3"]
        EXPERTISE_RESULTS = [
            (0.42154381, USERS[0]),
            (0.32808641, USERS[1]),
            (0.21227046, USERS[2]),
            (0.03809933, USERS[3]),
        ]
        QUALITY_RESULTS = [
            (0.52695009, RESOURCES[1]),
            (0.34629657, RESOURCES[0]),
            (0.12675334, RESOURCES[2]),
        ]
        activities = []
        activities.append((datetime.datetime(2010,7,1,9,0,0), USERS[0], RESOURCES[0]))
        activities.append((datetime.datetime(2010,7,2,9,0,0), USERS[1], RESOURCES[0]))
        activities.append((datetime.datetime(2010,6,1,9,0,0), USERS[0], RESOURCES[1]))
        activities.append((datetime.datetime(2010,6,1,10,0,0), USERS[1], RESOURCES[1]))
        activities.append((datetime.datetime(2010,6,2,11,0,0), USERS[2], RESOURCES[1]))
        activities.append((datetime.datetime(2010,6,10,12,0,0), USERS[2], RESOURCES[2]))
        activities.append((datetime.datetime(2010,6,14,12,0,0), USERS[3], RESOURCES[2]))

        spear = Spear(activities)
        expertise_results, quality_results = spear.run(verbose=False)

        # check expertise results
        for index, (expertise_score, user) in enumerate(expertise_results):
            ref_expertise_score, ref_user = EXPERTISE_RESULTS[index]
            self.assertAlmostEqual(expertise_score, ref_expertise_score, places=7)
            self.assertEqual(user, ref_user)

        # check quality results
        for index, (quality_score, resource) in enumerate(quality_results):
            ref_quality_score, ref_resource = QUALITY_RESULTS[index]
            self.assertAlmostEqual(quality_score, ref_quality_score, places=7)
            self.assertEqual(resource, ref_resource)
        

if __name__ == "__main__":
    unittest.main()
