# a hacky script that automatically restarts the bot on crash
:() {
	(
		./celestia.py
		sleep 5
		:
	)
};:
