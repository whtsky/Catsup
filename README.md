#catsup

##Install
```bash
git clone git://github.com/whtsky/catsup.git
cd catsup
pip install -r requirements.txt
cp config-sample.py config.py
vim config.py #Change it.
python catsup-server.py
```
Then go to http://localhost:8888 to take a look at your own catsup:)

##How to write
catsup uses Markdown to write posts.
Example:

	#Title
	- date: 2012-7-6
	
	----
	
	Content
	```python
	print "hi,I'm coding."
	```
	
##Deploy a static blog
run`python catsup-static.py`
And you can find your static blog in deploy/ .