# Release instructions 

> setup `pip install --upgrade pip build`

Using twine : https://twine.readthedocs.io/en/latest/ 

1. Clear `rm -r build dist *.egg-info`   if those dir exist.
2. Build :: `$  python -m build -s -w`   
3. Upload to **testpypi** ::  `$ twine upload -r testpypi dist/*`
4. Upload to **pypi** ::  `$ twine upload -r pypi dist/*`


### The `.pypirc` file

The rc file `~/.pypirc` should have something like this if not then create one
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username:__token__
password:<password_here>


[testpypi]
repository: https://test.pypi.org/legacy/
username:__token__
password:<password_here>
```

