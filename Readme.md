# About Project

The objective of this project is to create a robust and scalable web scraping service to extract restaurant data from the GrabFood API (https://portal.grab.com/foodweb/v2/search). The service is designed using Object-Oriented Programming (OOP) principles and incorporates multithreading to handle higher loads efficiently. The project uses Python and relies on the requests library for HTTP requests, ThreadPoolExecutor from the concurrent.futures module for multithreading, and gzip and json for data compression and storage.

## Functions/Methods
The GrabFoodScraper class initializes with necessary configurations, including the API URL, request headers, and payload template. It also sets up a session with retry logic to handle transient errors.

The _requests_retry_session method configures a session with a retry mechanism to handle request failures due to server errors or connectivity issues.

The get_restaurant_list method fetches the list of restaurants by making paginated requests to the API.

The _make_request_with_backoff method implements exponential backoff for retrying requests in case of server errors.

The parse_restaurant_details method extracts and structures the restaurant details from the API response.

The scrape method orchestrates the scraping process, including fetching and parsing restaurant data, and saving the results using multithreading.

The _save_to_ndjson method saves the parsed restaurant details to a compressed NDJSON file.

## Installation

Install Python Version 3.6+ on system. Run Command.
```bash
pip install 
```

Execute the command
```bash
python main.py 
```

To decompress and view the file
```bash
gunzip -c grab_food_data.ndjson.gz
```

## Problems faced during implementation

### Handling Transient API Failures
Issue: The API sometimes responds with transient errors (e.g., HTTP status codes 500, 502, 503, 504), which could disrupt the scraping process.

Solution: Implemented a retry mechanism with exponential backoff in the _requests_retry_session and _make_request_with_backoff methods. This approach retries failed requests after increasing intervals, reducing the likelihood of repeated failures.

### Efficient Data Processing
Issue: Processing a large amount of restaurant data sequentially would be slow and inefficient, especially when handling a high volume of data.

Solution: Utilized multithreading with ThreadPoolExecutor to parallelize the parsing and saving of restaurant details. This approach significantly improves the performance and scalability of the scraper by distributing the workload across multiple threads.

# About me

I am Yashica Paliwal, a dedicated and innovative Software Engineer based in Kanpur, India. I specialize in both backend and frontend development, with a particular proficiency in C#, ASP.NET, Django, and JavaScript. I have a strong background in full-stack development, having worked with technologies such as Angular, React, MongoDB, and NodeJS.

My professional journey includes valuable internships at Wesoftek Solutions in Gurgaon and I-exceed Technology Solutions in Bengaluru. At Wesoftek Solutions, I managed backend development and data migration tasks, while at I-exceed, I contributed to frontend development and database integration. My academic achievements include a B.Tech in Computer Science from Jaypee University of Information Technology, where I graduated with an 8.4 CGPA.

I have successfully completed several projects, including a machine learning-based crop recommendation system and a dynamic food ordering website. My skill set is further enhanced by my training at IIT-K (IFACET) and certifications from HackerRank.

I am passionate about leveraging my technical skills to solve complex problems and create impactful solutions. Connect with me on LinkedIn or explore my work on GitHub.