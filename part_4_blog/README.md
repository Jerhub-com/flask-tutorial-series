# Jerhub Flask Tutorial Series
**Author:** Jeremy Ecker

**Link:** [Jerhub Flask Tutorial Series](https://jerhub.com/tutorials/home)
--

# Part 4: Blog
In this section, we will discuss adding blogging capabilities to the
application. We will integrate a WYSIWYG (What You See Is What You Get) editor,
and add a new model, views, and templates to demonstrate its use.

We will move slightly more quickly in this section since concepts such as
template / view creation have been addressed in previous sections, but we will
take some time to discuss specific details of integrating CKEditor with the
app. As always, official documentation is useful:

[flask-ckeditor docs](https://flask-ckeditor.readthedocs.io/en/latest/)

## New dependencies
Add to `requirements.txt`:

`Flask-CKEditor`

## Init
Add to `__init__.py`:
### Imports
`from flask_ckeditor import CKEditor`

### Configuration
Add between database setup and CSRF:
```
app.config['CKEDITOR_FILE_UPLOADER'] = 'blog_posts.upload'
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
app.config['CKEDITOR_ENABLE_CSRF'] = True
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
ckeditor = CKEditor(app)
```

## Model
For the model we are going to need several columns, namely:

- user - string of the username
- date - datetime of publication
- title - string of the title
- content - text of the post content
- published - boolean of whether the post is published or not

Go ahead and open up `models.py` and add a new class called `BlogPost`, which
inherits from `db.Model`. Define those columns, and make an `__init__` method
for the caller to set them on instantiation. If you get stuck, reference the
provided code.

## Form
In `core/forms.py`, add a new form named `BlogPostForm`. Within it, add three
fields:

- title
- content
- submit

The only new field will be content, which will be a `CKEditorField`, so you will
need a new import:

`from flask_ckeditor import CKEditorField`

The field should look like:

`content = CKEditorField('Text', validators=[DataRequired()])`

We won't be using a ReCaptcha field for this form, because we are going to
require that the user be logged in and an admin in order to access it.

## Views
This is where the meat of this section lies, because we are going to be adding
a bunch of new views. At a minimum, we should make a way for the user to have
CRUD (Create, Read, Update, Delete) capabilities for blog posts, as well as
pages to list them. In addition, we'll make use of file uploads so they can add
pictures to the posts.

In `core/views.py`, add the new imports we will need:
```
import os
import datetime
from flask import current_app, send_from directory, request, abort
from flask_ckeditor import upload_success, upload_fail
from scaffold.models import BlogPost
from scaffold.core.forms import BlogPostForm
```

### Blog - Listing posts
We'll want two views for this, one which will list only published posts and be
accessible to all visitors, and a second which will list all posts and be
accessible only to admin users.

The first view will be routed to `/blog`, and it needs to query the database and
pass the list of published posts to the template. The second will do the same
thing, but it will be routed to `/blog/admin`, and have the `@login_required`
decorator.

**Hints**: Here are sqlalchemy queries you could use:

Get all posts:

`posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date.desc())).scalars()`

Get only published posts:

`posts = db.session.execute(db.select(BlogPost).filter_by(published=True).order_by(BlogPost.date.desc())).scalars()`


### Create
Now, listing posts is great, but it doesn't do us much good if we can't create
them in the first place. This view should again have the `@login_required`
decorator, and should first check that the user is an admin. If not, it should
abort with a 403 forbidden error.

Next, instantiate a `BlogPostForm`, and check the `validate_on_submit()`. Recall
that in the model, we made the user column a string representing the username.
So we'll need to get the username from the user id of current_user, for example:

`user = db.session.execute(db.select(User).filter_by(id=current_user.id)).scalar()`

We'll also want a `date = datetime.datetime.now()` for the date column.

Armed with those, try to make the whole view function, and refer to the provided
code if stuck.

### Read
For reading a post, we aren't going to know in advance which post the user is
requesting to read, so we'll want to provide some way to select it dynamically.
Luckily, we can use the post id for this. In the route decorator, you can do it
like this: `@core.route('/<int:post_id>')` and then pass `post_id` into the
function. That way if the user tries to visit `/23`, the post with id=23 will
be displayed.

Next, craft a sql query to get the post with that id, and pass it into the
template. If the post doesn't exist, you should abort with a 404 error.

One thing to note: we said earlier that we should only allow published posts to
be visible for anyone, but that we want all posts to be visible for admins. We
can accomplish this in the same view by wrapping the return statement into an if
statement:
```
if blog_post.published or current_user.admin:
    return render_template('blog/read_post.html', post=blog_post)
```

### Update
This one is just a little more complicated, because we don't just want to give
the user the BlogPostForm like we did in `create_post()`, we also want to make
sure that the existing post content is displayed to the user when the form
loads. For clarity, we'll go ahead and give you this function for free:
```
@core.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """
    Allow admin to edit a blog post.
    """
    if not current_user.admin:
        abort(403)

    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()

    form = BlogPostForm()

    if form.validate_on_submit():
        blog_post.title=form.title.data
        blog_post.content=form.content.data
        db.session.commit()

        return redirect(url_for('core.read_post', post_id=blog_post.id))
    
    # Pre-populate the form with current data
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.content.data = blog_post.content

    return render_template('blog/create_post.html', form=form)
```

### Delete
This is a bit simpler than the previous one - all we need to do is use the
`session.delete` on the blog post. So locate the post by id as we showed before,
and call `db.session.delete(blog_post)`.

### Publish
To publish a post, we'll want to set the `published` flag to True. But, what if
we made a mistake and want to un-publish a post, such as if we published it by
accident and it wasn't quite done yet? Our strategy to handle this should be,
rather than just setting the flag to True, we'll check its existing value and
set it to the opposite, and worry about conveying that information to the user
from the template. While we're at it, we'll update the publication date to the
current date. Here is what the function should look like once it's done:
```
@core.route('/<int:post_id>/publish', methods=['GET', 'POST'])
@login_required
def publish_post(post_id):
    """
    Toggle a blog post's published flag.
    """
    if not current_user.admin:
        abort(403)

    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()
    
    blog_post.published = False if blog_post.published else True
    blog_post.date = datetime.datetime.utcnow()

    db.session.commit()

    return redirect(url_for('core.read_post', post_id=post_id))
```

### File uploads
For file uploads, we patterned our solution almost exactly after that listed in
the [flask-ckeditor docs](https://flask-ckeditor.readthedocs.io/en/latest/plugins.html#image-upload), so if you haven't had a chance yet, head on over there and
take a look, and see if you can get it working on your own. Take a look at our
provided solution if you run into issues.

## Templates
In addition to a slight modification to `base.html`, there will be several new
templates required:

- blog.html
- blog_admin.html
- create_post.html
- read_post.html

Since our templates folder is started to look a bit cluttered by now, it is a
good time to make a new directory within templates, and use it to house the
blog-related stuff. Let's call it `blog` (we are quite creative here at Jerhub).

First, in `base.html`, you'll want to add this line to the end of the `<head>`
section: `{{ckeditor.load_code_theme()}}`.

Next, add some logic in the navbar unordered list to determine which blog link
to display. If the current user is an admin, we want to link them to the
blog_admin route, but if not, we want to send them to the regular blog. Let's
employ a little Jinja2 mojo for this:
```
{% if current_user.admin %}
    <li>
        <a class="nav-link" href={{url_for('core.blog_admin')}}>Blog</a>
    </li>
{% else %}
    <li>
        <a class="nav-link" href={{url_for('core.blog')}}>Blog</a>
    </li>
{% endif %}
```

The last task now is to discuss the remaining templates, which will live in the
new `templates/blog` directory. First of all, let's tackle `blog.html` and
`blog_admin.html`. These will be very, very similar with only slight changes.
The main difference is that whereas in the public blog we will simply display
a list of posts, in the admin blog we must also add buttons for accessing our
CRUD views' functionality.

Recall in the views that we pass `posts` to the templates? Well, we can iterate
over those in a jinja `for` loop to display them all as individual cards, as in
this complete `blog.html` template:
```
{% extends 'base.html' %}
{% block content %}
    <div class="flex-container">
        <div>
            <h1>Blog</h1>
        </div>
    </div>

    <div class="flex-container">
        {% for post in posts %}
            <div class="card">
                <div>
                    <h2>{{post.title}}</h2>
                    <p>Written by {{post.user}} on {{post.date.strftime('%B %d, %Y')}}</p>
                    <button><a href="{{url_for('core.read_post', post_id=post.id)}}">Read</a></button>
                </div>
            </div>
        {% endfor %}
    </div>
{% endblock %}
```
So now that we understand the basic loop, go ahead and try to implement
`blog_admin.html` by yourself. Remember that is exactly the same as above, but
you are adding buttons for Create, Read, Update, and Delete, which link to the
urls for their respective views.

Not too bad, right? Now on to the last two views: `blog/create_post.html` and
`blog/read_post.html`.

For `create_post.html`, just make a new form to gather the fields we need to
populate:
```
{% extends 'base.html' %}
{% block content %}
    <div class="flex-container">
        <div class="card">
            <form method="POST">
                {{form.hidden_tag()}}
                {{form.title.label}}<br>
                {{form.title}}<br><br>
                {{form.content.label}}<br>
                {{form.content}}<br><br>
                {{form.submit()}}
            </form>
            {{ckeditor.load()}}
            {{ckeditor.config(name='content')}}
        </div>
    </div>
{% endblock %}
```
Remember, we don't need any `edit_post.html`, because we are going to re-use
this one and just have the title and content fields pre-populated by the view.

The `read_post.html` template is going to be slightly more complicated, but not
too bad. Basically, we are going to use Jinja to detect if the current user is
an admin, and if so, provide buttons at the bottom of the post to update,
delete, or publish. For publishing, we are also going to need to check whether
the post is currently published or not, and label the button accordingly.
Remember, the `publish_post` view is going to be linked from both buttons, it is
only the button label which is different, because same view is acting as a
toggle for the published boolean flag. The tricky part is that we will need to
specify that we are using the `POST` method for the delete and publish actions.
This one is slightly tricky, so I'll provide the full example below.

`read_post.html`:
```
{% extends 'base.html' %}
{% block content %}
    <div class="flex-container">
        <div class="card">
            <div>
                <h1>{{post.title}}</h1>
                    <p>Written by {{post.user}} on {{post.date.strftime('%B %d, %Y')}}</p><hr>
                {{post.content|safe}}

                {% if current_user.admin %}
                    <div>
                        <button><a href="{{url_for('core.update_post', post_id=post.id)}}">Edit</a></button>

                        <form action="{{url_for('core.delete_post', post_id=post.id)}}" method="POST">
                            <input type="hidden" name="csrf_token" value="{{csrf_token()}}"/>
                            <input type="submit" value="Delete">
                        </form>

                        {% if not post.published %}
                            <form action="{{url_for('core.publish_post', post_id=post.id)}}" method="POST">
                                <input type="hidden" name="csrf_token" value="{{csrf_token()}}"/>
                                <input type="submit" value="Publish">
                            </form>
                        {% else %}
                            <form action="{{url_for('core.publish_post', post_id=post.id)}}" method="POST">
                                <input type="hidden" name="csrf_token" value="{{csrf_token()}}"/>
                                <input type="submit" value="Un-Publish">
                            </form>
                        {% endif %}
                        
                    </div>
                {% endif %}

            </div>
        </div>
    </div>
{% endblock %}
```

## Sanitize Form Data
The [Flask-CKEditor docs](https://flask-ckeditor.readthedocs.io/en/latest/basic.html#clean-the-data) suggest to use a built-in method called 'cleanify' to
sanitize the HTML data prior to working with it, which is a great suggestion.
The issue with their method though, is that it makes use of a now depricated
package called 'bleach' behind the scenes. It is a good idea to try to keep your
application dependencies up to date, and when one goes the way of the Dodo, it
is time to start looking for alternative solutions.

Enter NH3 (Ammonia). [NH3 docs](https://nh3.readthedocs.io/en/latest/)

This is a good thing to do not only where we expect to find html in a form
submission, but also where we don't expect it but malicious users might try to
do some tomfoolery with our forms.

First, `import nh3`. Next, in `core/views.py` let's adjust the `create_post` and `update_post` functions to make use of NH3. In `create_post,` after the checks
for `if validate_on_submit()`, change the BlogPost instantiation to look like
this:
```
blog_post = BlogPost(user=user.username,
                     date=datetime.datetime.now(),
                     title=nh3.clean(form.title.data),
                     content=nh3.clean(form.content.data),
                     published=False)
```

Then in `update_post`, revise it similarly:
```
if form.validate_on_submit():
        blog_post.title = nh3.clean(form.title.data)
        blog_post.content=nh3.clean(form.content.data)
        db.session.commit()
```

Next, let's check the `login` and `contact` views to see if we need to pour any
ammonia on those too. For the login form, observe the types of the fields we
defined in `core.forms.py`:
```
email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=64)])
password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
```
In the [wtforms docs](https://wtforms.readthedocs.io/en/2.3.x/fields/), we can
see that the PasswordField is basically a StringField, so we can do a clean on
both email and password in `core.views.py` `login` view.

Similarly, do the same process for the `contact` view. Examine your form field
types and clean the ones that need cleaning: email, name, and message fields in
this case. If you get stuck, refer to our provided files.

## Conclusion
And that's it! My sincere congratulations to you for completing part 4 of the
Jerhub Flask Tutorial Series. I hope you were able to take away some good info,
and most importantly, I hope you had fun! See you next time~
