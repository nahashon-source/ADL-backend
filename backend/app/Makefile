.PHONY: run stop restart

run:
	uvicorn backend.app.main:app --reload --port=8080

stop:
	@fuser -k 8080/tcp || true

restart: stop run


# make run     # start server
# make stop    # stop server
# make restart # restart cleanly
