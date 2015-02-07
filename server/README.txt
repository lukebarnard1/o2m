
Luke Barnard, 5th February 2015

The Server

This part of this package will enable the user to expose their data through a RESTful API. Security is going to remain the main theme - it has to be completely airtight and I have solutions to make this possible.

STEPS TO SHARE MY POSTS

1. There are some posts on my server that are unencrypted in a database.
2. In order to access these posts, my friends will need the key that decrypts them - the key that only I know: my private key.
	a. By giving this private key away, it isn't really private anymore... But this must be done SECURLY (not using the Internet).
	b. This key can decrypt my posts once the encrypted posts have reached the client.
3. The posts are encrypted using the public key, which everyone can know, and if they do, the only thing they can do is pretend to be me... So something else is sent with my posts - the private key! My friends already know it, so they can use it to authenticate my posts to prove I sent them. The private key itself must be encrypted along with the posts to make sure it isn't visible in transit to anyone who isn't my friend.
4. The posts are sent and arrive at the other side of the Internet. They are now decrypted using the private key, which is immediately used to check if the post really is from me... But what's the point of this if the decryption is proof that it's me. If someone else has my public key, they can't calculate the private key - that's the point. What if it's possible to go the other way?