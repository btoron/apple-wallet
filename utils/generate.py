#!python
import argparse
import shutil

from apple_wallet import PasskitService


def main(template: str):
    my_pass, passfile = PasskitService.get().generate_pass_from_template(
        template=template
    )
    assert passfile.exists()
    # Move passfile to a different location
    shutil.move(passfile, "tmp/pass.pkpass")


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a pass")
    # add an argument for the template name
    parser.add_argument(
        "--template",
        type=str,
        help="Name of the template to use",
        default="example",
    )
    args = parser.parse_args()
    # Call the main function including the template name
    main(template=args.template)
