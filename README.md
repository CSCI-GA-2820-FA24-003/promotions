# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-FA24-003/promotions/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA24-003/promotions/actions)

## API Usage
local depolyment: http://localhost:8080/
1. Read a promotion  
Method: `GET`  
Endpont: `/promotions/{promotion_id}`  
Response:  
```json
{
    "active": true,
    "created_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "description": "test d",
    "duration": "15 days, 0:00:00",
    "id": 2,
    "promo_code": 11000,
    "promo_type": "AMOUNT_DISCOUNT",
    "promo_value": "test v",
    "start_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "title": "test2"
}
```
2. Create a promotion   
Method: `POST`  
Endpont: `/promotions`  
Response:  
```json
{
    "active": true,
    "created_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "description": "test d",
    "duration": "15 days, 0:00:00",
    "id": 2,
    "promo_code": 11000,
    "promo_type": "AMOUNT_DISCOUNT",
    "promo_value": "test v",
    "start_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "title": "test2"
}
```
3. Find all promotions  
Method: `GET`  
Endpont: `/promotions`  
Response:  
```json
    {
        "active": true,
        "created_date": "Tue, 08 Oct 2024 00:00:00 GMT",
        "description": "test d",
        "duration": "15 days, 0:00:00",
        "id": 1,
        "promo_code": 11000,
        "promo_type": "AMOUNT_DISCOUNT",
        "promo_value": "test v",
        "start_date": "Tue, 08 Oct 2024 00:00:00 GMT",
        "title": "test"
    },
    {
        "active": true,
        "created_date": "Tue, 08 Oct 2024 00:00:00 GMT",
        "description": "test d",
        "duration": "15 days, 0:00:00",
        "id": 2,
        "promo_code": 11000,
        "promo_type": "AMOUNT_DISCOUNT",
        "promo_value": "test v",
        "start_date": "Tue, 08 Oct 2024 00:00:00 GMT",
        "title": "test2"
    }

```

4. Update all promotions  
Method: `PUT`  
  Endpont:`/promotions/<int:promotion_id> `  
  Response:
  ```json
     {     
    "active": true,
    "created_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "description": "test d",
    "duration": "15 days, 0:00:00",
    "id": 1,
    "promo_code": 11000,
    "promo_type": "AMOUNT_DISCOUNT",
    "promo_value": "test v",
    "start_date": "Tue, 08 Oct 2024 00:00:00 GMT",
    "title": "new_test"
}
```


5. Delete promotions  
Method: `DELETE`  
  Endpont:`/promotions/<int:promotion_id>`  
  Response: HTTP_204_NO_CONTENT



## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
