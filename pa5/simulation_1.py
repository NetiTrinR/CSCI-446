'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network_1 as network
import link_1 as link
import threading
from time import sleep
import sys

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
	object_L = [] #keeps track of objects, so we can kill their threads

	#create network hosts
	h1 = network.Host(1)
	object_L.append(h1)
	h2 = network.Host(2)
	object_L.append(h2)


	#create routers and routing tables for connected clients (subnets)
	# router_a_rt_tbl_D = {1: {0: 1}, 2: {1: 1}, 3: {2:2}} # packet to host 1 through interface 0 for cost 1
	router_a_rt_tbl_D = {1: {0: 1}} #packet to host 1 through interface 0 for cost of 1
	router_a = network.Router(name='A',
							  intf_cost_L=[1,1],
							  intf_capacity_L =[500,500],
							  rt_tbl_D = router_a_rt_tbl_D,
							  max_queue_size=router_queue_size)
	object_L.append(router_a)

	# router_b_rt_tbl_D = {3: {1: 1}, 1:{0:1}} # packet to host 2 through interface 1 for cost 3
	router_b_rt_tbl_D = {2: {1: 3}}
	router_b = network.Router(name='B',
							  intf_cost_L=[1,3],
							  intf_capacity_L = [500,100],
							  rt_tbl_D = router_b_rt_tbl_D,
							  max_queue_size=router_queue_size)
	object_L.append(router_b)

	# # router_c_rt_tbl_D = {3: {1: 1}} # packet to host 1 through interface 0 for cost 1
	# router_c_rt_tbl_D = {1:{0:4},2:{0:4},3:{1:2}}
	# router_c = network.Router(name='C',
	# 						  intf_cost_L=[3,1],
	# 						  rt_tbl_D = router_c_rt_tbl_D,
	# 						  max_queue_size=router_queue_size)
	# object_L.append(router_c)

	# # router_d_rt_tbl_D = {1: {0: 4}, 3: {2: 1}} # packet to host 1 through interface 0 for cost 1
	# router_d_rt_tbl_D = {1:{0:7,1:5},2:{0:7,1:5},3:{2:1}}
	# router_d = network.Router(name='D',
	# 						  intf_cost_L=[1,1,1],
	# 						  rt_tbl_D = router_d_rt_tbl_D,
	# 						  max_queue_size=router_queue_size)
	# object_L.append(router_d)

	#create a Link Layer to keep track of links between network nodes
	link_layer = link.LinkLayer()
	object_L.append(link_layer)

	#add all the links
	link_layer.add_link(link.Link(h1, 0, router_a, 0))
	# link_layer.add_link(link.Link(h2, 0, router_a, 1))
	link_layer.add_link(link.Link(router_a, 1, router_b, 0))
	link_layer.add_link(link.Link(router_b, 1, h2, 0))
	# link_layer.add_link(link.Link(router_b, 1, router_d, 0))
	# link_layer.add_link(link.Link(router_c, 1, router_d, 1))
	# link_layer.add_link(link.Link(router_d, 2, h3, 0))


	#start all the objects
	thread_L = []
	for obj in object_L:
		thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

	for t in thread_L:
		t.start()

	# we cant update the routing tables because if we do so the routers
	# will always forward the data packets though the minimum cost path

	#send out routing information from router A to router B interface 0
	# router_a.send_routes(1)

	#create some send events
	for i in range(5):
		priority = i%2
		print(priority)
		h1.udt_send(2, 'Sample h1 data %d' % i, priority)
		# h3.udt_send(1, 'Sample h3 to h1 data %d' % i)
	#give the network sufficient time to transfer all packets before quitting
	sleep(simulation_time)

	#print the final routing tables
	for obj in object_L:
		if str(type(obj)) == "<class 'network.Router'>":
			obj.print_routes()

	#join all threads
	for o in object_L:
		o.stop = True
	for t in thread_L:
		t.join()

	print("All simulation threads joined")



# writes to host periodically
