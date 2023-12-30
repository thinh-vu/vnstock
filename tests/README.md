# 1. Vnstock Unit Testing

This document is an annex of the Vnstock Contributing Guidelines.

It provides the necessary information to build, run and maintain Unit Tests for Vnstock.

## 2. Run `unit tests`

In this section we will explain everything you need to run the `unit tests` on the `Vnstock` project.

## 2.1. How to install tests dependencies?

To run the tests you will need first to install the [`pytest` package](https://docs.pytest.org/en/7.1.x/index.html). For example, using poetry as dependencies manager, you run this command:

```bash
poetry add pytest
```

### 2.2. How to run `tests`:

#### By `module`

You can run tests on a specific module by specifying the path of this module, as follows:

```bash
pytest tests/test_some_module.py
```

#### By test `name`

You can run tests by their name with the argument `-k`. Read more about this argument [here](https://docs.pytest.org/en/7.1.x/example/markers.html#using-k-expr-to-select-tests-based-on-their-name)

```bash
pytest tests/test_some_module.py -k test_function_name
```

## 2.3. How to skip tests

### Skipping a specific test

You can use the decorator `@pytest.mark.skip` as below:

```python
import pytest

@pytest.mark.skip
def test_some_function(mocker):
    pass

@pytest.mark.skip(reason="This time with a comment")
def test_another_function(mocker):
    pass
```

### Skipping the entire test module

```python
import pytest

pytest.skip(msg="Some optional comment.", allow_module_level=True)

def test_some_function(mocker):
    pass
```

## 3. How to build `unit tests`

When you contribute a new feature to the Vnstock project, it's important that tests are added for this particular feature.

All the `unit tests` should be insides the `tests` folder. There should be at most one `test module` for each `module` of the `Vnstock` project.

Each `test module` should follow the same naming pattern of the `module` that it is `testing`. For instance,

- in order to test the following module `vnstock/funds.py`
- a `test module` should be added here: `tests/test_funds.py`