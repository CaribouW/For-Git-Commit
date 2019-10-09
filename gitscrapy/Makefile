schema2sql:
	docker exec -i git-mysql mysqldump -uroot -pmysql gitcommit > framework.sql

sql2schema:
	docker exec -i git-mysql mysql -uroot -pmysql gitcommit < framework.sql

deploy:
    docker-compose up -d --build
