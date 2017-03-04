##Introduction
This project is an implementation of a basic blog, using the Google App Engine framework.  Functionality includes:

+ front page to display posts
+ individual pages to display single posts and their comments
+ sign-up page to register new users
+ login page to login existing users
+ ability for logged in users to logout
+ registered users can create, edit, and delete blog posts
+ registered users can like, or comment on other users' posts (but not their own)
+ registered users can edit their comments

##Files
The following files should be included:

+ app.yaml
+ blog.py
+ all .html files in the /templates folder (8)
+ all .css files in the /static folder (3)
+ all .py files in the /models folder (4 + __init__)
+ all .py files in the /handlers folder (13 + __init__)


##Running and Viewing the App
In order to run the blog, you must have the following installed:

* python2.7
* google app engine

To run the app on your local machine using the google app engine's shell, you can run the command
> ```
> dev_appserver.py [PATHNAME]
> ```

where [PATHNAME] is the path to the app.yaml file.

Alternatively, if you have a Google Cloud account, you can have Google's appcloud host the app.  After registering a domain, you can run the command
> ```
> gcloud app deploy
> ```
from the app.yaml's directory

**IMPORTANT!**
In order for links in the .html pages to correctly render, it is necessary to set the variable 'url' in /handlers/hanlder.py (line 25)

by default it is set to


> ```
> url = 'http://localhost:8080'
> ```

If you are not deploying it locally, you must change it to the url you are deploying it to.  Example:


> ```
> url = 'http://seths-udacity-project.appspot.com'
> ```