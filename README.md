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

### Post properties
catsup supports some post properties. Write them before "---" and start with "- ".
Example:

    - category: A Category
    - date: 2012-12-24
    - tags: tag1, tag2
    - comment: no

The `category` property defines the category of the post, but it's not used yet.
The `date` property can overwrite the date from the filename。
The `tags` property defines the tags of the post.
The `comment` property defines whether the post can be commented or not.

### Post excerpt
You can use `<--more-->` to define an excerpt of a post. Any content before that will be used as excerpt of the post. And you can choose to display excerpt rather than full content on your homepage.

##Deploy a static blog
run`python catsup.py deploy`
And you can find your static blog in deploy/ .