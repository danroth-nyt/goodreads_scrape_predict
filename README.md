# Goodreads Scraper and Interest Predictor

This repository includes code for both a Goodreads scraper and a jupyter notebook that performs EDA and modeling using the dataset collected during web scraping.  BeautifulSoup4 and Selenium were used for scraping and sklearn was used to create and experiment with linear regression models.  These highly interpretable models are then analyzed and feature coefficient variances are plotted in order to observe the most significant user interactions on Goodreads.  This code is meant to accompany my blog post, [What are the best predictors for interest in a book on Goodreads?](https://medium.com/@rdan689/what-are-the-best-predictors-for-interest-in-a-book-on-goodreads-1555ec3ebc1c).

## Getting Started

Use the .py scraper script in order to scrape Goodreads (using your own API key) and load up the jupyter notebook for example analysis and modeling.

### Prerequisites

Install all libraries listed under the Built With section.  Part of the scrape code requires a Goodreads login to gather Goodreads' book statistics.

## Running the tests

Follow the jupyter notebook in order to redo the original processing pipeline.

## Built With

* Python 3.7
* BeautifulSoup4
* Selenium
* SKlearn
* Seaborn
  
## Versioning

Version 1.0

### Current Concerns/Issues

* Some of the scrape code needs to be debugged and additional features can be added.

## Authors

* **Dan Roth** - *Initial work* 

## Acknowledgments

* Thanks to my teachers and classmates at Metis.


