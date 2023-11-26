from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.scraping.craigslist import return_sites_for_state, return_results_for, scrape_listing_data


def get_listings_and_save_results(search_term: str, site:str, models, db):
    print(f'Saving results for {search_term} from {site} for cars and trucks')
    # returns (title, link)
    results = return_results_for(search_term, site)
    #save to db
    try:
        for title, link in results:
            db_listing = models.ListingsForScrapping(link=link, title=title)
            db.add(db_listing)
            db.commit()  # Committing after adding all listings'
    except IntegrityError as e:
        print('IntegrityError', e)
        return {'status': 'error', 'message': f'IntegrityError: {e}'}

    return {'status': 'ok', 'message': f'Saved results for {len(results)} listing for search:{search_term} from {site}'}

def scrape_listings_and_save_results(batch_size, models, db):
    # get listings to scrape where processed is not 1
    listings = db.query(models.ListingsForScrapping).filter(or_(models.ListingsForScrapping.processed.is_(None),models.ListingsForScrapping.processed != 1,)).limit(batch_size).all()
    print(f'Found {len(listings)} listings to scrape')
    summary = {
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "error_messages": []
    }
    # for each, scrape and save results
    for listing in listings:
        processed = listing.processed
        if processed:
            continue
        print(f'Scraping started')
        try:
            scrapped_data = scrape_listing_data(listing.link)
            print(f'Scrapped {listing.link}:\n {scrapped_data}')
            # save scrapped data to scrappedlisting table
            db_listing = models.ScrappedListing(**scrapped_data)
            db.add(db_listing)
            # then update listing to processed
            listing.processed = 1
            db.commit() 
            print(f'Successfully scrapped {listing.link}')
            summary["total_processed"] += 1
            summary["success"] += 1
        except IntegrityError as e:
            print('IntegrityError:', e)
            db.rollback()
            summary["total_processed"] += 1
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {listing.link}: IntegrityError - {e}')

        except Exception as e:
            print('Error during scraping or saving:', e)
            db.rollback()
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {listing.link}: General Error - {e}')
    return summary
