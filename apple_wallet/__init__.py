import hashlib
import json
import shutil
import tempfile
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7

from .models import Pass
from .settings import Settings, get_settings


class PasskitService:
    def create_pass_info(self, template: str, extra_data: dict = {}) -> Pass:
        my_pass = Pass.from_template(
            template=template, extra_data=extra_data, settings=self._settings
        )
        return my_pass

    def generate_pass_from_info(self, pass_info: Pass) -> Path:
        # Create a temporary directory to store the pass
        temp_dir = Path(tempfile.mkdtemp())
        # Copy the template files to the temporary directory
        if not pass_info.userInfo or not pass_info.userInfo._template:
            raise ValueError(
                "The pass template must be specified in the userInfo field"
            )
        source = self._settings.get_template_path(pass_info.userInfo._template)
        target = Path(temp_dir) / "temp.pass"
        shutil.copytree(source, target)
        # Deploy the json data to the temporary directory
        (Path(target) / "pass.json").write_text(
            pass_info.model_dump_json(indent=4, exclude_unset=True)
        )
        # Create the manifest
        manifest = self._create_manifest(target)
        # Sign and create signature and manifest files
        self._sign_manifest(manifest=manifest, pass_path=target)
        self._create_zipfile(target)

        return Path(target).parent / "pass.pkpass"

    def generate_pass_from_template(
        self, template: str, extra_data: dict = {}
    ) -> Tuple[Pass, Path]:
        # Generate structure from the template
        my_pass = Pass.from_template(
            model=template, extra_data=extra_data, settings=self._settings
        )

        # Create a temporary directory to store the pass
        temp_dir = Path(tempfile.mkdtemp())
        # Copy the template files to the temporary directory
        source = self._settings.get_template_path(template)
        target = Path(temp_dir) / "temp.pass"
        shutil.copytree(source, target)
        # Deploy the json data to the temporary directory
        (Path(target) / "pass.json").write_text(
            my_pass.model_dump_json(indent=4, exclude_unset=True)
        )
        # TODO : Filter files to copy
        # Create the manifest
        manifest = self._create_manifest(target)
        # Sign and create signature and manifest files
        self._sign_manifest(manifest=manifest, pass_path=target)
        self._create_zipfile(target)

        return my_pass, Path(target).parent / "pass.pkpass"

    def _create_manifest(self, pass_path: Path) -> str:
        manifest = {}
        for root, dir, files in pass_path.walk():
            for file in files:
                absolute_path = Path(root) / file
                hash = hashlib.sha1(absolute_path.read_bytes()).hexdigest()
                manifest[absolute_path.relative_to(pass_path).as_posix()] = hash
        Path(pass_path, "manifest.json").write_text(json.dumps(manifest))
        return json.dumps(manifest)

    def _sign_manifest(self, manifest: str, pass_path: Path):
        signature_path = Path(pass_path, "signature")
        certificate = x509.load_pem_x509_certificate(
            Path(self._settings.certificate_path, "signerCert.pem").read_bytes()
        )
        private_key = serialization.load_pem_private_key(
            Path(self._settings.certificate_path, "signerKey.pem").read_bytes(),
            password=None,
        )
        wwdr_certificate = x509.load_pem_x509_certificate(
            Path(self._settings.certificate_path, "wwdr.pem").read_bytes()
        )
        options = [pkcs7.PKCS7Options.DetachedSignature]
        signature = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(manifest.encode("UTF-8"))
            .add_signer(certificate, private_key, hashes.SHA256())
            .add_certificate(wwdr_certificate)
            .sign(serialization.Encoding.DER, options)
        )
        signature_path.write_bytes(signature)
        return signature_path

    def _create_zipfile(self, pass_path: Path):
        pass_zip = zipfile.ZipFile(Path(pass_path).parent / "pass.pkpass", "w")
        for root, dir, files in pass_path.walk():
            for file in files:
                absolute_path = Path(root) / file
                pass_zip.write(absolute_path, absolute_path.relative_to(pass_path))
        pass_zip.close()
        return pass_zip

    def __init__(self, settings: Settings = get_settings()):
        self._settings = settings

    @classmethod
    def get(cls, settings: Settings = get_settings()):
        return PasskitService(settings=settings)
