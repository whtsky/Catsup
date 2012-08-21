#catsup

##License
Licensed under the MIT License.

##Install
```bash
git clone git://github.com/whtsky/catsup.git
cd catsup
pip install -r requirements.txt
cp config-sample.py config.py
vim config.py #Change it.
python catsup.py server --port=8888
```
Then go to http://localhost:8888 to take a look at your own catsup:)

##How to write
catsup uses Markdown to write posts.
Filename should like 2000-01-01-catsup.md(year-month-day-title.md)
Example:

	#Title
	- tags: tag1, tag2, tag3
	
	----
	
	Content
	```python
	print "hi,I'm coding."
	```
	
##Deploy a static blog
run`python catsup.py deploy`
And you can find your static blog in deploy/ .