# Part 4: Blog (WIP NEEDS WRITEUP)
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
### Imports
`from datetime import datetime`

### Model
```
```

## Form
### Imports
```
from flask_ckeditor import CKEditorField
```

### Form
```
```

## Views
### Imports
```
import os
import datetime
from flask import current_app, send_from directory, request, abort
from flask_ckeditor import upload_success, upload_fail
from scaffold.models import BlogPost
from scaffold.core.forms import BlogPostForm
```

### Blog
```
```

### Create
```
```

### Read
```
```

### Update
```
```

### Delete
```
```

### Publish
```
```

### File uploads
```
```

## Templates
### base.html
#### end of head
```
{{ckeditor.load_code_theme()}}
```
### blog link
```
<li><a href="{{url_for('core.blog')}}">Blog</a></li>
```

### blog/blog.html
### blog/blog_admin.html
### blog/create_post.html
### blog/read_post.html

## create `uploads` directory next to templates / etc
