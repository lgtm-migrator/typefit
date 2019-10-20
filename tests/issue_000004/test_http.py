from typing import Any, Dict, List, NamedTuple, Optional, Text, Union

import httpx
import httpx.models as hm
from pytest import fixture
from typefit import api

HttpArg = Union[Text, List[Text]]
HttpArgs = Dict[Text, HttpArg]
HttpHeaders = Dict[Text, Text]


class HttpGet(NamedTuple):
    args: HttpArgs
    headers: HttpHeaders
    origin: Text
    url: Text


class HttpCookies(NamedTuple):
    cookies: Dict[Text, Text]


class HttpAuth(NamedTuple):
    authenticated: bool
    user: Text


@fixture(name="bin_url")
def make_bin_url():
    return "https://httpbin.org/"


def test_get_simple(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("get?value={value}")
        def get(self, value: int) -> HttpGet:
            pass

    get = Bin().get(42)
    assert isinstance(get, HttpGet)
    assert get.args["value"] == "42"


def test_get_parametric(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get(lambda value: f"get?value={value}")
        def get(self, value: int) -> HttpGet:
            pass

    get = Bin().get(42)
    assert get.args["value"] == "42"


def test_get_headers_static(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        def headers(self) -> Optional[hm.HeaderTypes]:
            return {"Foo": "Bar", "Answer": "nope"}

        @api.get("get", headers={"Answer": "42"})
        def get(self) -> HttpGet:
            pass

    get = Bin().get()
    assert get.headers["Foo"] == "Bar"
    assert get.headers["Answer"] == "42"


def test_get_headers_parametric(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("get", headers=lambda value: {"Answer": f"{value}"})
        def get(self, value: int) -> HttpGet:
            pass

    get = Bin().get(42)
    assert get.headers["Answer"] == "42"


def test_get_hint(bin_url):
    called = set()

    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("get", hint="foo")
        def get(self) -> HttpGet:
            pass

        def raise_errors(self, resp: httpx.Response, hint: Any) -> None:
            called.add("raise_errors")
            assert hint == "foo"
            return super().raise_errors(resp, hint)

        def decode(self, resp: httpx.Response, hint: Any) -> Any:
            called.add("decode")
            assert hint == "foo"
            return super().decode(resp, hint)

        def extract(self, data: Any, hint: Any) -> Any:
            called.add("extract")
            assert hint == "foo"
            return super().extract(data, hint)

    Bin().get()
    assert called == {"raise_errors", "decode", "extract"}


def test_get_params_static(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("get", params={"value": "42"})
        def get(self) -> HttpGet:
            pass

    get = Bin().get()
    assert get.args["value"] == "42"


def test_get_params_parametric(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("get", params=lambda value: {"value": value})
        def get(self, value: int) -> HttpGet:
            pass

    get = Bin().get(42)
    assert get.args["value"] == "42"


def test_get_cookies_static(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        def cookies(self) -> Optional[hm.CookieTypes]:
            return {"answer": "nope", "foo": "bar"}

        @api.get("cookies", cookies={"answer": "42"})
        def test_cookies(self) -> HttpCookies:
            pass

    cookies = Bin().test_cookies()
    assert cookies.cookies["answer"] == "42"
    assert cookies.cookies["foo"] == "bar"


def test_get_cookies_parametric(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get("cookies", cookies=lambda answer: {"answer": answer})
        def test_cookies(self, answer: Text) -> HttpCookies:
            pass

    cookies = Bin().test_cookies("42")
    assert cookies.cookies["answer"] == "42"


def test_get_auth_static(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        def auth(self) -> Optional[hm.AuthTypes]:
            return "foo", "bar"

        @api.get("basic-auth/{user}/{password}")
        def test_auth(self, user: Text, password: Text) -> HttpAuth:
            pass

    auth = Bin().test_auth("foo", "bar")
    assert auth.authenticated
    assert auth.user == "foo"


def test_get_auth_parametric(bin_url):
    class Bin(api.SyncClient):
        BASE_URL = bin_url

        @api.get(
            "basic-auth/{user}/{password}", auth=lambda user, password: (user, password)
        )
        def test_auth(self, user: Text, password: Text) -> HttpAuth:
            pass

    auth = Bin().test_auth("foo", "bar")
    assert auth.authenticated
    assert auth.user == "foo"
