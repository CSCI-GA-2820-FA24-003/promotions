Feature: The shopcarts service back-end
    As a Promotion site Manager
    I need a RESTful catalog service
    So that I can keep track of all promotions.
    Background:
        Given the following promotions
            | id |      title       | description  | promo_code | promo_type      | promo_value | start_date | created_date | duration | active |
            | 1  | nike promotion   | promo desc 1 | 10001      | AMOUNT_DISCOUNT | 20%         | 2024-10-22 | 2024-10-05   | 14 days  | true   |
            | 2  | adidas promotion | promo desc 2 | 10002      | BUY_ONE_GET_ONE | 1           | 2024-11-05 | 2024-11-04   | 7 days   | false  |
    Scenario: Background test