import json

from pydantic_core import Url

from apple_wallet.models import Pass
from apple_wallet.settings import Settings


def test_model_pass_read_json(test_settings):
    # read a json file and create a Pass object
    with open("tests/data/example.pass/pass.json", "r") as f:
        pass_dict = json.load(f)
    assert pass_dict is not None
    my_pass = Pass(**pass_dict)
    assert my_pass.passTypeIdentifier == test_settings.passId


def test_model_pass_read_from_template(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId


def test_model_pass_read_from_template_with_extra_data(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example",
        settings=Settings(template_path="tests/data"),
        extra_data={"serialNumber": "123456"},
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    assert my_pass.serialNumber == "123456"


def test_model_inout(monkeypatch, test_settings):
    def compare(dict1, dict2, key):
        if isinstance(dict1[key], dict):
            for key2 in dict1[key].keys():
                compare(dict1[key], dict2[key], key2)
        elif isinstance(dict1[key], list):
            for i, item in enumerate(dict1[key]):
                compare(dict1[key], dict2[key], i)
        elif isinstance(dict1[key], str) and isinstance(dict2[key], Url):
            assert dict1[key] == str(dict2[key])
        else:
            assert dict1[key] == dict2[key]

    settings = Settings(template_path="tests/data")
    # Get content of a template
    my_pass_json = json.loads(
        (settings.get_template_path("example") / "pass.json").read_text()
    )
    # create a Pass object from a template
    my_pass = Pass.from_template("example", settings=settings)
    assert my_pass.passTypeIdentifier == test_settings.passId
    print(my_pass.model_dump_json(exclude_unset=True, indent=4))
    my_pass_2 = my_pass.model_dump(exclude_unset=True)
    for key in my_pass_json.keys():
        compare(my_pass_json, my_pass_2, key)
