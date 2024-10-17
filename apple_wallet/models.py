from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator

from apple_wallet.settings import Settings, get_settings


class FieldType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BACK = "back"
    HEADER = "header"
    AUXILIARY = "auxiliary"


class PassStyle(str, Enum):
    GENERIC = "generic"
    BOARDING_PASS = "boardingPass"
    COUPON = "coupon"
    EVENT_TICKET = "eventTicket"
    STORE_CARD = "storeCard"


class PassFieldContent(BaseModel):
    attributedValue: Optional[str] = None
    changeMessage: Optional[str] = None
    currencyCode: Optional[str] = None
    dataDetectorTypes: Optional[str] = None
    dateStyle: Optional[str] = None
    ignoresTimeZone: Optional[bool] = False
    isRelative: Optional[bool] = False
    key: str
    label: Optional[str] = None
    numberStyle: Optional[str] = None
    textAlignment: Optional[str] = None
    timeStyle: Optional[str] = None
    value: str
    row: Optional[int] = None


class HeaderField(PassFieldContent):
    pass


class PrimaryField(PassFieldContent):
    pass


class SecondaryField(PassFieldContent):
    pass


class AuxiliaryField(PassFieldContent):
    pass


class BackField(PassFieldContent):
    pass


class BarcodeFormat(str, Enum):
    PKBarcodeFormatQR = "PKBarcodeFormatQR"
    PKBarcodeFormatPDF417 = "PKBarcodeFormatPDF417"
    PKBarcodeFormatAztec = "PKBarcodeFormatAztec"
    PKBarcodeFormatCode128 = "PKBarcodeFormatCode128"


class PassFields(BaseModel):
    auxiliaryFields: Optional[list[AuxiliaryField]] = None
    backFields: Optional[list[BackField]] = None
    headerFields: Optional[list[HeaderField]] = None
    primaryFields: Optional[list[PrimaryField]] = None
    secondaryFields: Optional[list[SecondaryField]] = None


class Barcode(BaseModel):
    altText: Optional[str] = None
    message: str
    format: BarcodeFormat
    messageEncoding: str


class UserInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    _template: Optional[str] = None


class Pass(BaseModel):
    """An object that represents a pass"""

    appLaunchURL: Annotated[
        AnyHttpUrl,
        Field(
            default=None,
            description="The URL to be used to launch the app when the pass is added to the wallet",
        ),
    ]
    associatedStoreIdentifiers: Optional[list[int]] = None
    authenticationToken: Optional[str] = None
    backgroundColor: Optional[str] = None
    barcodes: Optional[list[Barcode]] = None
    beacons: Optional[list[dict]] = None
    boardingPass: Optional[PassFields] = None
    coupon: Optional[dict] = None
    description: str
    eventTicket: Optional[PassFields] = None
    expirationDate: Optional[str] = None
    foregroundColor: Optional[str] = None
    formatVersion: int = 1
    generic: Optional[PassFields] = None
    groupingIdentifier: Optional[str] = None
    labelColor: Optional[str] = None
    logoText: Optional[str] = None
    locations: Optional[list[dict]] = None
    maxDistance: Optional[int] = None
    nfc: Optional[dict] = None
    organizationName: str
    passTypeIdentifier: str
    relevantDate: Optional[str] = None
    semantics: Optional[dict] = None
    serialNumber: str
    sharingProhibited: Optional[bool] = False
    storeCard: Optional[PassFields] = None
    suppressStripShine: Optional[bool] = True
    teamIdentifier: str
    userInfo: Optional[dict] = None
    voided: Optional[bool] = None
    webServiceURL: Optional[AnyHttpUrl] = None
    # Internal fields
    _style: Optional[str] = None

    @model_validator(mode="after")
    def validate_pass(self):
        # Identify which type of pass it is by checking which one of the attributes is not None
        self._style = next((p.value for p in PassStyle if getattr(self, p.value)), None)

        if not self._style:
            raise ValueError("Pass style not set")

        return self

    @property
    def style(self):
        return self._style

    @classmethod
    def from_template(
        cls, template: str, extra_data: dict = {}, settings: Settings = get_settings()
    ):
        # Load a pass template from a json file in the model directory
        json_file = Path(settings.template_path) / f"{template}.pass" / "pass.json"
        if not json_file.exists():
            raise FileNotFoundError(f"File {json_file} not found")
        with open(json_file, "r") as f:
            pass_dict: dict = json.load(f)
        # Augment the pass dictionary with extra data
        pass_dict.update(extra_data)
        # We store the template name in the userInfo field
        if pass_dict.get("userInfo"):
            pass_dict["userInfo"]["_template"] = template
        else:
            pass_dict["userInfo"] = {"_template": template}

        return cls(**pass_dict)

    def _get_field(self, key: str, field_type: FieldType) -> Optional[PassFieldContent]:
        field_map = {
            "primary": "primaryFields",
            "secondary": "secondaryFields",
            "back": "backFields",
            "header": "headerFields",
            "auxiliary": "auxiliaryFields",
        }

        field_attr = field_map.get(field_type)
        if not field_attr:
            return None

        pass_fields = getattr(self, self.style, None)
        if pass_fields:
            fields = getattr(pass_fields, field_attr, None)
            if fields:
                for field in fields:
                    if field.key == key:
                        return field
        return None

    def get_primary_field(self, key: str) -> Optional[PrimaryField]:
        return self._get_field(key, "primary")

    def get_secondary_field(self, key: str) -> Optional[SecondaryField]:
        return self._get_field(key, "secondary")

    def get_back_field(self, key: str) -> Optional[BackField]:
        return self._get_field(key, "back")

    def get_header_field(self, key: str) -> Optional[HeaderField]:
        return self._get_field(key, "header")

    def get_auxiliary_field(self, key: str) -> Optional[AuxiliaryField]:
        return self._get_field(key, "auxiliary")

    def _set_field(self, field_type: FieldType, field: PassFieldContent) -> None:
        field_map = {
            "primary": "primaryFields",
            "secondary": "secondaryFields",
            "back": "backFields",
            "header": "headerFields",
            "auxiliary": "auxiliaryFields",
        }

        field_attr = field_map.get(field_type)
        if not field_attr:
            raise ValueError(f"Invalid field type {field_type}")

        pass_fieldset = getattr(self, self.style, None)
        if not pass_fieldset:
            pass_fieldset = PassFields()
            setattr(self, self.style, pass_fieldset)
        fields = getattr(pass_fieldset, field_attr, None)
        if not fields:
            fields = []
            setattr(pass_fieldset, field_attr, fields)
        for i, f in enumerate(fields):
            if f.key == field.key:
                fields[i] = field
                return
        fields.append(field)

    def set_primary_field(self, field: PrimaryField) -> None:
        self._set_field("primary", field)

    def set_secondary_field(self, field: SecondaryField) -> None:
        self._set_field("secondary", field)

    def set_back_field(self, field: BackField) -> None:
        self._set_field("back", field)

    def set_header_field(self, field: HeaderField) -> None:
        self._set_field("header", field)

    def set_auxiliary_field(self, field: AuxiliaryField) -> None:
        self._set_field("auxiliary", field)
