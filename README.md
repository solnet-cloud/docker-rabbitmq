# docker-rabbitmq

	<b>This build is still under development</b>

RabbitMQ is open source message broker software (sometimes called message-oriented middleware) that implements the Advanced Message Queuing Protocol (AMQP). The RabbitMQ server is written in the Erlang programming language and is built on the Open Telecom Platform framework for clustering and failover.

More details can be found at the RabbitMQ <a href="http://www.rabbitmq.com">website</a>. 

This Docker builds on top of a Ubuntu image to provide a working RabbitMQ image which can be used to broker messages between nodes in a cluster.

You will provide the replication IP address for this node in the cluster and for other member(s) of the cluster. It is recommended that you use restart on-failure.

	docker run -d --restart=on-failure solnetcloud/rabbitmq:latest 172.20.20.1 172.20.20.2 172.20.20.3


