import shutil

from apple_wallet import PasskitService
from apple_wallet.settings import Settings


def test_service_generate_pass(test_settings):
    my_pass, passfile = PasskitService.get(
        settings=Settings(template_path="tests/data")
    ).generate_pass_from_template(template="example")
    assert my_pass.passTypeIdentifier == test_settings.passId
    assert passfile.exists()
    # Move passfile to a different location
    shutil.move(passfile, "tests/data/pass.pkpass")


def test_service_generate_modified_pass(test_settings):
    extra_data = {
        "generic": {
            "primaryFields": [
                {"key": "Student", "value": "Laura Martin", "label": "Student"}
            ],
            "secondaryFields": [
                {"key": "by", "value": "Amelia Bedelia", "label": "Pickup By"},
                {"key": "extra", "value": "HONDA, RED, GLSH91"},
            ],
            "backFields": [
                {"key": "date", "value": "2021-09-01", "label": "Pickup Date"},
                {"key": "time", "value": "10:00", "label": "Pickup Time"},
                {
                    "key": "createPass",
                    "attributedValue": "<a href='https://example.net'>Create Pass</a>",
                    "label": "Create Pass",
                    "value": "",
                },
            ],
        }
    }
    my_pass, passfile = PasskitService.get(
        settings=Settings(template_path="tests/data")
    ).generate_pass_from_template("example", extra_data=extra_data)
    assert my_pass.passTypeIdentifier == test_settings.passId
    assert passfile.exists()
    # Move passfile to a different location
    shutil.move(passfile, "tests/data/pass.pkpass")


def test_generate_pass_from_info(test_settings):
    pass_info = PasskitService.get(
        settings=Settings(template_path="tests/data")
    ).create_pass_info("example")
    assert pass_info is not None
    assert pass_info.passTypeIdentifier == test_settings.passId
    passfile = PasskitService.get(
        settings=Settings(template_path="tests/data")
    ).generate_pass_from_info(pass_info)
    assert passfile.exists()
    shutil.move(passfile, "tests/data/pass.pkpass")
