Feature: The Promotion service back-end
    As a Promotion site Manager
    I need a RESTful catalog service
    So that I can keep track of all promotions.

Background:
    Given the following promotions
        | id |      title       | description  | promo_code | promo_type      | promo_value | start_date | created_date | duration | active |
        | 1  | nike promotion   | promo desc 1 | 10001      | AMOUNT_DISCOUNT | 20%         | 2024-10-22 | 2024-10-05   | 14 days  | true   |
        | 2  | adidas promotion | promo desc 2 | 10002      | BUY_ONE_GET_ONE | 1           | 2024-11-05 | 2024-11-04   | 7 days   | false  |

Scenario: Create a Promotion
    When I visit the "Home Page"
    And I set the "title" to "New Year Sale"
    And I set the "description" to "Huge discount"
    And I set the "promo_code" to "10001"
    And I select "AMOUNT_DISCOUNT" in the "promo_type" dropdown
    And I set the "promo_value" to "50%"
    And I set the "start_date" to "01-01-2025"
    And I set the "created_date" to "12-25-2024"
    And I set the "duration" to "30 days"
    And I select "True" in the "active" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "title" field should be empty
    And the "description" field should be empty
    When I paste the "id" field
    # Read a Promotion
    And I press the "Retrieve" button        
    Then I should see the message "Success"
    And I should see "New Year Sale" in the "title" field
    And I should see "Huge discount" in the "description" field
    And I should see "10001" in the "promo_code" field
    And I should see "AMOUNT_DISCOUNT" in the "promo_type" dropdown
    And I should see "50%" in the "promo_value" field
    And I should see "30 days" in the "duration" field
    And I should see "True" in the "active" dropdown

Scenario: Update a Promotion
    When I visit the "Home Page"
    And I set the "title" to "nike promotion"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "nike promotion" in the "title" field
    And I should see "promo desc 1" in the "description" field
    When I change "title" to "Holiday Discount"
    And I change "description" to "Special year-end offer"
    And I change "promo_value" to "25%"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    # Read a Promotion
    And I press the "Retrieve" button     
    Then I should see the message "Success"
    And I should see "Holiday Discount" in the "title" field
    And I should see "Special year-end offer" in the "description" field
    And I should see "25%" in the "promo_value" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Holiday Discount" in the results
    And I should not see "nike promotion" in the results

    
# Mimic action route
Scenario: Toggle Active for a Promotion
    When I visit the "Home Page"
    And I set the "title" to "nike promotion"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "nike promotion" in the "title" field
    And I should see "promo desc 1" in the "description" field
    # Change active to true, was false 
    When I select "True" in the "active" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button     
    Then I should see the message "Success"
    And I should see "True" in the "active" dropdown
    # Change active to false, was changed to true
    When I select "False" in the "active" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "False" in the "active" dropdown

Scenario: Delete a Promotion
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "nike promotion" in the "title" field
    And I should see "promo desc 1" in the "description" field
    # Delete that promotion
    When I press the "Delete" button
    Then I should see the message "Promotion has been Deleted!"
    When I set the "id" to "1"
    And I press the "Retrieve" button
    Then I should see the message "was not found"

Scenario: List all Promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "nike promotion" in the results
    And I should see "adidas promotion" in the results
    And I should not see "puma promotion" in the results

Scenario: Query a Promotion
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "title" to "nike promotion"
    And I set the "description" to "promo desc 1"
    And I set the "promo_code" to "10001"
    And I select "AMOUNT_DISCOUNT" in the "promo_type" dropdown
    And I set the "start_date" to "10-22-2024"
    And I set the "created_date" to "10-05-2024"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should see "20%" in the "promo_value" field
