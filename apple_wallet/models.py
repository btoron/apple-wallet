from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator

from .settings import Settings, get_settings


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
    boardingPass: Optional[dict] = None
    coupon: Optional[dict] = None
    description: str
    eventTicket: Optional[dict] = None
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
    storeCard: Optional[dict] = None
    suppressStripShine: Optional[bool] = True
    teamIdentifier: str
    userInfo: Optional[dict] = None
    voided: Optional[bool] = None
    webServiceURL: Optional[AnyHttpUrl] = None

    @model_validator(mode="after")
    def validate_pass(self):
        # Either generic, boardingPass, coupon, eventTicket, or storeCard must be present
        if not any(
            [
                self.generic,
                self.boardingPass,
                self.coupon,
                self.eventTicket,
                self.storeCard,
            ]
        ):
            raise ValueError(
                "Either generic, boardingPass, coupon, eventTicket, or storeCard must be present"
            )
        return self

    @classmethod
    def from_template(
        cls, model: str, extra_data: dict = {}, settings: Settings = get_settings()
    ):
        # Load a pass template from a json file in the model directory
        json_file = Path(settings.template_path) / f"{model}.pass" / "pass.json"
        if not json_file.exists():
            raise FileNotFoundError(f"File {json_file} not found")
        with open(json_file, "r") as f:
            pass_dict: dict = json.load(f)
        # Augment the pass dictionary with extra data
        pass_dict.update(extra_data)
        # We store the template name in the userInfo field
        if pass_dict.get("userInfo"):
            pass_dict["userInfo"]["_template"] = model
        else:
            pass_dict["userInfo"] = {"_template": model}

        return cls(**pass_dict)
