import json

from pydantic_core import Url

from apple_wallet.models import Pass, PrimaryField
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
    assert my_pass.style is not None


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


def test_model_get_primary_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    primary_field = my_pass.get_primary_field("student")
    assert primary_field is not None
    assert primary_field.value == "Laura MARTIN"
    assert primary_field.label == "Student"


def test_model_get_secondary_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    secondary_field = my_pass.get_secondary_field("loc")
    assert secondary_field is not None
    assert secondary_field.label == "LOCATION"
    assert secondary_field.value == "Aguamarina Elementary"


def test_model_get_back_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    back_field = my_pass.get_back_field("date")
    assert back_field is not None
    assert back_field.label == "Pickup Date"
    assert back_field.value == "2021-09-01"


def test_model_get_auxiliary_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    auxiliary_field = my_pass.get_auxiliary_field("extra")
    assert auxiliary_field is not None
    assert auxiliary_field.label == "Additional Info"
    assert auxiliary_field.value == "HONDA, RED, GLSH91"


def test_model_get_header_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    header_field = my_pass.get_header_field("allergy")
    assert header_field is not None
    assert header_field.label == "Allergies"
    assert header_field.value == "Peanuts"


def test_model_update_primary_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    primary_field = my_pass.get_primary_field("student")
    assert primary_field is not None
    assert primary_field.value == "Laura MARTIN"
    assert primary_field.label == "Student"
    primary_field.value = "Laura Martin"
    new_field = my_pass.get_primary_field("student")
    assert new_field is not None
    assert new_field.value == "Laura Martin"


def test_model_add_primary_field(monkeypatch, test_settings):
    # create a Pass object from a template
    my_pass = Pass.from_template(
        "example", settings=Settings(template_path="tests/data")
    )
    assert my_pass.passTypeIdentifier == test_settings.passId
    primary_field = PrimaryField(key="new", value="new value", label="New Label")
    my_pass.set_primary_field(primary_field)
    new_field = my_pass.get_primary_field("new")
    assert new_field is not None
    assert new_field.value == "new value"
