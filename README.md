# PA1 - Fanyi Tang UNI:ft2582
This is a UDP-based chatapp and following command will guide you how to run the app.

1. To build the server use:
python3 chatapp.py -s 4000

2. To build the client end:
python3 chatapp.py -c x localhost 4000 13100

3. Server function:

a. receive register msg and send ack
b. receive deregister msg and send ack
c. receive create_group msg and send ack
d. receive list_groups msg and send ack
e. receive join_group msg and send ack
f. receive groupchat msg and send ack
g. receive list_members msg and send ack
h. receive leave_group msg and send ack

4. Client function:
There two modes in client end:

a. normal mode and the command sample is here:
1. send client_name msg -> send private msg to other clien
2. create_group <group_name> -> create group chat
3. list_groups -> look at the group lists
4. join_group <group_name> -> join_group

b. group mode:
1. send_group msg -> send group message
2. list_members -> look at the members in group
3. leave_group -> leave group
