Selenium Test Steps:

Step 1: Initialize WebDriver and Navigate to the Website

	Create a new Python script (e.g., "amazon_automation.py").
	Import the necessary Selenium modules.
	Initialize a WebDriver instance (e.g. Chrome WebDriver).
	Navigate to the URL of the Amazon website (e.g., "https://www.amazon.com").

Step 2: Search for a Product

	Enter "headphones" in the search bar and submit the search.

Step 3: Navigate to Product Listing Page

	Click on the first product from the search results to navigate to the Product Detail Page.
	Capture the product name and price for validation later.

Step 4: Add Product to Cart

	Click on the "Add to Cart" button.

Step 5: Navigate to Shopping Cart

	Click on the cart icon to go to the Shopping Cart page.
	Validate that the product from the Product Detail Page is listed in the cart.

Step 6: Update Shopping Cart

	Change the quantity of the product (e.g., increase from 1 to 2).
	Remove the extra product from the cart.

Step 7: Proceed to Checkout

	Click on the "Proceed to Checkout" button.
	Validate that the correct product is listed for checkout.

Step 8: Complete Checkout (Simulated)

	Fill in shipping and payment details with mock data.
	Simulate placing the order and capture any order confirmation message.

Step 9: Close Browser and Clean Up

	Close the browser window.
	Clean up and quit the WebDriver instance.