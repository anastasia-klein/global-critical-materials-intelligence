# Microsoft schema references

This folder vendors only the transitive schema closure required by the authored PBIP/PBIR files and the official report-theme schema 2.159, enabling offline CI. Files retain their Microsoft MIT notices in the two included licence files. `manifest.json` records fingerprints and the source schema tree SHA.

Official sources:
- https://github.com/microsoft/json-schemas/tree/main/fabric
- https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema

Schema validation verifies the serialized structure; it does not execute Power BI, Power Query, DAX or visual rendering.
