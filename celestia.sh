# a hacky script that automatically restarts the bot on crash
:() {
	(
		python3 celestia.py
		sleep 5
		:
	)
};:
