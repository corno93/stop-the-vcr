
<div align="center">

# stop-the-vcr

![python-package workflow](https://github.com/corno93/stop-the-vcr/actions/workflows/python-package.yml/badge.svg)
![something](https://img.shields.io/badge/python-3.8%7C3.9%7C3.10%7C3.11-blue)
</div>

---


A package that contains `VCR.py` custom [request matchers](https://vcrpy.readthedocs.io/en/latest/advanced.html#register-your-own-request-matcher) including:

- `body_structure` - raises an assertion if the actual request structure is different to the expected request structure stored in the cassette
- `body_types`- raises an assertion if the actual request field types are different to the expected request field types stored in the cassette
- `body_structure_and_types` - does both of the above

## Why
Using`VCR.py` in tests is awesome. However, problems arise when devs get lazy and don't
re-record cassettes after their API changes. This leaves us blind in knowing whether
the change to our API causes a change in response from the downstream service.

Yes, we could use the `body` [request matcher](https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching)
from `VCR.py` to detect different out going request bodies. However, since `body` strictly compares the entire actual and expected
request bodies and if your project is using factories to generate test data, `body` will always raise an assertion...



## Quick start

```bash
pip install stop-the-vcr
````

## Usage

```python
# tests/test_something.py
import vcr
from stop_the_vcr.matchers import body_structure_and_types

my_vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['uri', 'method', 'body_structure_and_types'],
)

my_vcr.register_matcher("body_structure_and_types", body_structure_and_types)

# Then continue using vcr as you would
with my_vcr.use_cassette('test.json'):
    # your http code here
    ...

```
