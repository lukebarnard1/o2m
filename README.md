
O2M – One to Many, The Distributed Social Network
==========================================================
[![Build Status](https://travis-ci.org/lukebarnard1/o2m.svg?branch=master)](https://travis-ci.org/lukebarnard1/o2m)

Introduction
============

I for one am tired of using free systems that are funded by my own
contribution to this world. My connections with other people are fuelling the
accuracy of advertisement agencies and quite frankly, there’s nothing more
annoying.

The fact of the matter is that when data is all in one place and we’ve
willingly ticked the “I Agree to These Terms and Conditions” box, we’ve also
allowed for third parties to become involved.

But the Internet is better than this. There is no need for a centralized
website and database where everyone stores their entire lives. To me, this
simply creates unnecessary copies of everything you’ve ever thought or done
and puts it in the hands of those who want to make money from it. There are
ways to socialize without a central authority. The data in question should be
transmitted from sender to receiver and then it’s gone. It should be stored
for as long as is technically required. It should also only be stored for as
long as is absolutely necessary.

This should be the case for social networking. Everyone has a computer, which
is capable of becoming a web server. After all, a web server is just another
program running on a computer, preferably one connected to the Internet. The
program responds to requests from incoming connections and returns data given
that the requestor has proven that they can be trusted (the same level of
trust that you would assign to a friend, perhaps). Also, they must prove that
they really are that person to prevent anyone pretending to be anyone else.
This is the foundation of the social network I’m about to describe.

The Fundamentals
================

Data
----

The data in question is social data. Data you would like to share with your
friends. This data is stored on your own personal computer. This way, you can
delete it whenever you like. You can also edit it whenever you like. The data
can only be accessed when your computer is connected to the Internet (or at
least to the requestor’s computer via a network). Implementations of this
network may implement caching for speed increases, but the temporary files
will only be stored on your friends’ computers (this may make ‘deleting’ a
file quite difficult, but once data can be accessed, it can be copied anyway,
regardless of caching).

Network Protocol - HTTP
-----------------------

In the spirit of not reinventing the wheel, it would be most appropriate to
use the web as the foundation for this social network. The HTTP protocol comes
with security and authentication features that will be most important to
create a secure implementation of the network. Data will be exposed through a
web interface that can be accessed only by friends.

GUI
---

The graphical user interface of this system can be anything, but for an easy
transition between today’s social networks and the one I propose here, a
browser-based interface would be appropriate.

Linking
-------

This is another key part of the social network. In any social network, others
who wish to share their opinions respond to initial “posts” with “comments”.
Here, there is no necessary distinction, but how does one link a “comment” to
a “post” if they’re on different machines? No problem, use a link. Links have
already revolutionized the way we communicate data with the rest of the world,
so why not use them here.

There is a hierarchy or tree structure that spans the Internet, connecting
friends and their data together into one social network. Each user has their
own tree consisting of nodes. Each node has a piece of content, which can be
reached by URL (constructed from the IP of the friend who left it) and
children. The content could be literally any data of any format but in fact,
it should be reachable via a URL. This means that parts of trees from
networked computers can be downloaded at high speed, followed by the
potentially large files linked to at each node. It also means that
authentication to access actual content can be done separately. For a more
familiar feeling, the tree need not be fetched but maybe the same nodes in
order of time or only the nodes of which descend from a specified node in a
tree (such as the root node).

If I make a post on my local machine, and a friend comments on it, then their
comment is linked to from my machine. That way, I have control of the link and
they have control of the data. This is how social networks should be. If
someone then comments on their comment, the same thing happens because posts
and comments are ultimately pieces of text stored on their creators’ machines,
reachable via URLs. But because I was the original poster, all of the links
are stored on my machine.

Naturally, friends are the only ones who can create links and they reserve the
authority to change or delete the link so long as it’s theirs.

Friends
-------

Friends are people you trust. People are either not your friend or they are.
This binary nature of the term “friend” can be extended to the binary nature
of being able to login to a web server. You either can or you can’t. If
someone would like to see my posts, then they must have “registered” their
friendship with me. This means that I have a record of them in my database and
a way to make sure that it really is them requesting data. A simple password
and username system would suffice here, but any level of authentication is
possible.

Security 
=========

Obviously, all data should be absolutely secure from any third parties wishing
to listen in. Solutions to this already exist and they really do work, so long
as you can trust the person you’re communicating with not to give away their
private keys. This may not be truly the case with every website you’ve ever
visited but it is certainly true with your friends. So the real problem with
security is trust and this problem is solved when you trust whom you
communicate with. It makes sense really, when you think about it.

Functional Requirements
=======================

I first define a data dictionary explaining each of the objects in this social
network. The server you expose to your friends will also need a defined set of
functionalities so that implementations can agree on how to communicate.

Data Dictionary
---------------

 Name | Description
 -----|--------------
 Tree | There is one of these stored on each user’s computer. It is a structure that begins with a root Node and each Node belongs to a parent except the root.
 Node | One node has a Friend that created it (this could be the owner of the tree) and an identifier to identify the Content on the Friend’s machine. A node also has a creation time.
 Content | This can be downloaded at a URL once a unique identifier is known. At the URL can be any data and when downloaded, it will come with a Content-Type header, which will allow it to be rendered accordingly.
 Friend | Each Friend object contains an IP address, port number and a name. This is just a minimum. If authentication is required, perhaps a password for accessing this Friend’s server is also needed.

Protocol
--------

 Method | URL | Action | Authority 
 -------|-----|--------|----------
 GET | /posts | Return a JSON tree containing the Nodes on this server. | Friends
 GET | /timeline | Return a JSON array of Nodes and their children that are descendants of the root, sorted by time created. |Friends
 POST | /posts | Add a Node to the root Node of the Tree. | Owner
 POST | /node/somenode | Add a Node to the Node identified by “somenode”. The user who creates this Node should have already created content on their machine for this Node to link to. | Friends
 GET | /content/somecontent | Get the Content represented by the identifier “somecontent”. | Friends
 POST | /content/somecontent | Add a piece of Content to the collection of Contents stored on this machine with the identifier “somecontent”. | Owner
