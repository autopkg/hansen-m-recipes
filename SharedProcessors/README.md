These shared processors are for use in AutoPkg recipies. 

## Processors for Windows Software

### BESRelevanceProvider.py
- uses the BigFix QnA tool to parse files for version info
- Prereq: Run `autopkg install QnA`

### HachoirMetaDataProvider.py
- uses the Hachoir MetaData python library to get version information from EXE files
- Prereq: run `pip install hachoir_core hachoir_metadata hachoir_parser`

### MSIVersionProvider.py
- uses the wine and lessmsi application and wine to get version information from MSI files. Depreciated 02/2020.

### MSIInfoVersionProvider.py
- uses the msitools and misinfo tool to get version information from MSI files https://wiki.gnome.org/msitools
- Prereq: run `brew install msitools`

### WinInstallerExtractor.py
- uses the 7zip library to extract files (EXEs) to get their contents for further processing, including parsing the resulting files for version information.
- Prereq: run `brew install p7zip`

### GoogleChromeWinVersioner.py
- uses 7zip (/usr/local/bin/7z) library to extract Google Chrome MSI and regex to pull the current version from the SummaryInformation file.
- Prereq: run `brew install p7zip`
