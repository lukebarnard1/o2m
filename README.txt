
Luke Barnard, Tuesday 3rd February 2015

One to Many - The Distributed Social Network

INTRODUCTION
One to Many is an idea that I have to create completely decentralized social network. The main features that One to Many defines are:
	- All data created by a user resides ONLY on their computer and links between user data are exactly that - links.
	- Data is served out of users' own computers in an encrypted format that can only be decrypted with a key that they posses, which can be given to their friends
	- Each user has a web interface hosted locally on their computer which acts as the user interface for controlling their data and reading other users' data

ARCHITECTURE

Package
	- Server: Serves your posts, comments, anything that you want your friends to see
		- Serve posts and comments to other people
		- Allow people to comment on your posts by leaving links to comments on their system
	- Client: Read, write, edit and delete your posts whilst being able to comment on other peoples' posts
		- Loads other people's posts through known addresses. If you know someone's address and their key, you can see their posts and the comment links on their computer. Links are then followed but this can only happen if they can be decrypted - so you have to be friends if you want to see their comments. So keys are needed to decrypt data AND links

Server:
The server will be a web server based on the DJango library. A very simple RESTful API will be used so that users can GET,PUT,UPDATE and DELETE their own posts and comments locally but also PUT and DELETE their comments.

OWNER 				SERVER 		FRIENDS
	GET post->		|	<- PUT comment link
	DELETE post->		|	<- DELETE comment link
	UPDATE post->		|
	PUT post->		|
				|
	DELETE comment->	|
	UPDATE comment->	|
	PUT comment->		|

All data will be transmitted in an encrypted JSON format. For example, if a user requests my posts, they are free to have the data and if they have associated my web server (IP address) with a key to decrypt the data, then they can also interpret the data and follow any comment links with recognized addresses attached to them.

Data will be stored in a database locally on the user's own computer: they can do whatever they want with it, it's theirs!

Client:
The client will be a web client that requests data from the friends requested. Friends will be stored locally as a (name, address, key) tuple so that their data can be labeled, networked and decrypted. The first page will be your own profile that you can add posts to.