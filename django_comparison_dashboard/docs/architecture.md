
# Upload

Upload of scenario data is done by following steps:
1. Select scenario from source (via `DataSource`)
2. Transform data into datamodel used by dashboard (via `DataAdapter`)
3. Validate (using frictionless) and store data in database (via `import` function in model `Scenario`)
