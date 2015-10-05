These shared processors are for use in AutoPkg recipies. 


## Processors for Windows Software

### HachoirMetaDataProvider.py
- uses the Hachoir MetaData python library to get version information from EXE files

### MSIVersionProvider.py
- uses the lessmsi application to get version information from MSI files

### WinInstallerExtractor.py
- uses the 7zip library to extract files (EXEs) to get their contents for further processing, including parsing the resulting files for version information. 
