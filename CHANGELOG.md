# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.2] - 2025-02-28
### Fixed
- pandera version updated to v0.22.1

## [2.7.1] - 2025-02-28
### Fixed
- pandera version fixed to v0.17.2

## [2.7.0] - 2024-12-17
### Changed
- default annotations font size

### Fixed
- chart height option at display options

## [2.6.0] - 2024-12-04
### Added
- error message if upload validation fails

## [2.5.1] - 2024-12-03
### Changed
- removed MODEX source for uploads

### Fixed
- CSV upload

## [2.5.0] - 2024-12-03
### Added
- databus source to import SEDOS results from databus
- option to filter all groups in groups, input_groups or output_groups

### Fixed
- filter None values in input/output groups in case of none-sankey graphs

## [2.4.0] - 2024-10-18
### Changed
- UI design by bmlancien

## [2.3.0] - 2024-10-11
### Added
- abbreviations in nav bar
- error message if chart/table creation fails

### Changed
- implemented tabs to separate chart and data table
- streamlined plot options
- do not filter None values in input/output groups

### Fixed
- x/y axis titles

## [2.2.0] - 2024-08-28
### Added
- sankey colors from user input and/or predefined color mapping
- units to sankey

## [2.1.1] - 2024-06-28
### Fixed
- error due to numpy version >=2.0.0

## [2.1.0] - 2024-06-28
### Added
- display options are used when plotting bar and line charts

## [2.0.0] - 2024-06-28
### Changed
- parameters are stored using ID instead of full query

### Added
- input and output groups in data model_

## [1.1.0] - 2024-06-06
### Changed
- searchable multi select dropdowns for dashboard filters

## [1.0.0] - 2024-05-16
### Added
- sankey charts
- datatables support for dashboard table

### Changed
- output format (including support for groups column containing lists)
- combine table and chart creation button

## [0.4.1] - 2024-03-05
### Added
- version bumping

## [0.4.0] - Labels & Colors - 2024-03-04
### Changed
- implementation of colors and labels

## [0.3.1] - HTMX - 2024-01-22
### Added
- django-htmx to dependencies

## [0.3.0] - First Deploy - 2024-01-19
### Added
- index view
- scenario selection view
- upload view for scenario data uploads
- models for scenario data and sources
- MODEX source
- downloading of MODEX scenario data
- storing downloaded data into DB
- preprocessing (filtering, aggregating and unit conversion) of scalar data
