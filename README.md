# TradingPractice
Simple chart rendering app with ability to load a data file bid and/or ask file and allow trading with manual chart scrolling

Software needed to run it:

python
pygame


How to use it:

Create a folder called data and put 1 or 2 datafiles in there
If you have bid/ask data make sure the ASK file is first and the bid second (rename if they aren't)
If you only have 1 file then that's fine, the program will simply have no spread cost

The data file(s) must be of the following format:
Time 	Ask	Bid	AskVolume	BidVolume
eg data:
2020.01.01,22:02:56.165,1.32516,1.32462,0.74,0.74

Remove the file header if it has one, it must be a raw data file


About the app:

This is a simple app, I thew it together in a short period of time
It only runs manually with arrow keys and it simply draws the next bar
If you want it to process Tick data and then convert that to 1min,5min,1hr,4hr,1Day timeframe data and have it draw every tick 
then it's not much more work to upgrade it. If you want that functionality, go for it.

The purpose of the app is to practice manual trade execution on a 5min timeframe to practice already existing skills until they are trained to be used in realtime.
I haven't come across a tool that does this to the level I want and I also wanted more control over my testing process.
The code records data for FADE TRADES and TREND TRADES which can help you calculate stats on which trades are working best for you

This code isn't perfect and this is by no means a complete project.
You may adapt this code and do what you wish with it.
