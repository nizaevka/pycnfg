# Contribution guide

## Issues

[GitHub issues](https://github.com/nizaevka/pycnfg/issues) for bug reports and feature requests.

#### Step-by-step guide

##### New feature

1. Make an issue with your feature description;
2. We shall discuss the design and its implementation details;
3. Once we agree that the plan looks good, go ahead and implement it.


##### Bugfix

1. Goto [GitHub issues](https://github.com/nizaevka/pycnfg/issues);
2. Pick an issue and comment on the task that you want to work on this feature;
3. If you need more context on a specific issue, please ask, and we will discuss the details.


Once you finish implementing a feature or bug-fix, please send a Pull Request.

If you are not familiar with creating a Pull Request, here are some guides:
- http://stackoverflow.com/questions/14680711/how-to-do-a-github-pull-request
- https://help.github.com/articles/creating-a-pull-request/


##### Contribution best practices

0. Install pre-commit hook:
```
pip install pre-commit
```
1. Break your work into small, single-purpose updates if possible.
It's much harder to merge in a large change with a lot of disjoint features.
2. Submit the update as a GitHub pull request against the `master` branch.
3. Make sure that you provide docstrings for all your new methods and classes
4. Make sure that your code passes the unit tests.
5. Add new unit tests for your code.


## Documentation

Project uses [Numpy style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html)
for formatting docstrings. 
Length of line inside docstrings block must be limited to 79 characters.

#### Check that you have written working docs
```bash
make html
```

The command requires `Sphinx` and some sphinx-specific libraries.