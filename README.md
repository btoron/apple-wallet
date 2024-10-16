# Apple Wallet

A very simple library to generate Passes for Apple Wallet

Model-based (hello pydantic)

### Configuration

All the configuration comes through environment vars (see `pydantic-settings`, but can be overwritten):

- **APPLE_WALLET_TEMPLATE_PATH**: Path to the templates. Every template is a folder called `<TEMPLATE>.pass` that follows the structure defined in [3]. Defaults to `./templates`

- **APPLE_WALLET_CERTIFICATE_PATH**: Path to the folder containing certificates and keys. Defaults to `./certificates`. Three certificates are needed:
  - Key
  - CSR
  - WWDR

### Tests

202409: Tested for iOS 17 and 18

### Acknowledgments

This library is heavily based on the examples and code provided in:

[1] https://github.com/twopointone/applepassgenerator (Worked fine but I am addicted to Pydantic)

[2] https://github.com/alexandercerutti/passkit-generator (Excellent ideas that I try to replicate in Python)

### More about Apple Pass ###
[3] Reference: Human Interface: https://developer.apple.com/design/human-interface-guidelines/wallet

[4] Reference: PassKit: https://developer.apple.com/wallet/

[5] Reference: PassKit Package Format Reference: https://developer.apple.com/library/archive/documentation/UserExperience/Reference/PassKit_Bundle/Chapters/Introduction.html