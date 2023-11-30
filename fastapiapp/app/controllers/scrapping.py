from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
import json
import time
import concurrent
from app.scraping.craigslist import return_sites_for_state, return_results_for, scrape_listing_data, download_image_and_save_s3
from app.database import SessionLocal
from app.constants import ScrapeStatus

def get_listings_and_save_results(search_term: str, site: str, models, db):
    print(f'Saving results for {search_term} from {site} for cars and trucks')
    results = return_results_for(search_term, site)

    summary = {
        "site": site,
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "error_messages": []
    }

    for title, link in results:
        print('processing', title, link)
        summary["total_processed"] += 1
        try:
            db_listing = models.ListingsForScrapping(link=link, title=title)
            db.add(db_listing)
            db.commit()  # Committing after each listing
            summary["success"] += 1
        except IntegrityError as e:
            # print('IntegrityError:', e)
            db.rollback()  # Rollback in case of error
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {link}: IntegrityError - {e}')
        except Exception as e:
            # print('Error during saving:', e)
            db.rollback()
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {link}: General Error - {e}')

    return summary


def get_listings_and_save_results_OLD(search_term: str, site:str, models, db):
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
    start = time.time()
    # get listings to scrape where processed is not 1
    listings = db.query(models.ListingsForScrapping).filter(or_(models.ListingsForScrapping.processed.is_(None),models.ListingsForScrapping.processed == 0,)).limit(batch_size).all()
    print(f'Found {len(listings)} listings to scrape')
    summary = {
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "images_uploaded": 0,
        "total_images": 0,
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
            if scrapped_data == 'listing has expired':
                print(f'Listing {listing.link} has expired')
                listing.processed = 2
                db.commit()
                continue
            print(f'Scrapped {listing.link}:\n {scrapped_data}')
            # save scrapped data to scrappedlisting table
            db_listing = models.ScrappedListing(**scrapped_data)
            db.add(db_listing)
            # then update listing to processed
            listing.processed = 1
            db.commit() 
            print(f'Successfully scrapped {listing.link}')
            # upload images to s3
            image_links = json.loads(scrapped_data['image_links'])
            summary['total_images'] += len(image_links)
            #do this concurrently, 
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for index, image_link in enumerate(image_links):
                    future = executor.submit(download_image_and_save_s3, image_link, scrapped_data['hash'], index)
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    summary["images_uploaded"] += future.result()
            

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
    summary["time_taken"] = time.time() - start
    return summary

def get_sites_by_state(state: str, save: bool, models, db):
    sites = return_sites_for_state(state)
    if save:
        # build summary object
        summary = {
            "total sites": len(sites),
            "state": state,
            "success": 0,
            "failures": 0,
            "error_messages": []
        }
        # save to db
        try:
            db_site = models.CraigslistSites(state=state, sites=json.dumps(sites))
            db.add(db_site)
            db.commit()
            print(f'Successfully saved sites: {sites}')
            summary["success"] += 1
        except IntegrityError as e:
            print('IntegrityError while saving site', e)
            db.rollback()
            summary["failures"] += 1
            summary["error_messages"].append(f'State {state}: IntegrityError - {e}')
        except Exception as e:
            print('Error while saving site', e)
            db.rollback()
            summary["failures"] += 1
            summary["error_messages"].append(f'State {state}: General Error - {e}')
        return summary
    return sites

def return_sites_from_db(state: str, models, db):
    results = db.query(models.CraigslistSites).filter(models.CraigslistSites.state == state).first()
    if results:
        return json.loads(results.sites)
    return None

def scrape_listings_and_save_results_concurrent(batch_size, models, db):
    start = time.time()
    # get listings to scrape where processed is not 1
    listings = db.query(models.ListingsForScrapping).filter(
        or_(models.ListingsForScrapping.processed.is_(None),models.ListingsForScrapping.processed == 0,)
    ).limit(batch_size).all()
    print(f'Found {len(listings)} listings to scrape')
    #summary for reply
    summary = {
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "images_uploaded": 0,
        "total_images": 0,
        "error_messages": []
    }
    #double check listings
    listings_to_scrape = [listing for listing in listings if not listing.processed]
    print(f'Removed {len(listings)-len(listings_to_scrape)} listings that were already processed')

    # concurrently scrape and save results
    futures = []
    # for each, scrape and save results
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for listing in listings_to_scrape:
            future = executor.submit(_scrape_and_save_to_db_and_s3, listing.id, models)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            print('returned from thread')
            thread_summary = future.result()
            # take returned summary and add to summary
            summary["total_processed"] += thread_summary["total_processed"]    
            summary["success"] += thread_summary["success"]
            summary["failures"] += thread_summary["failures"]
            summary["images_uploaded"] += thread_summary["images_uploaded"]
            summary["total_images"] += thread_summary["total_images"]
            summary["error_messages"].extend(thread_summary["error_messages"])
    
    # take data and build summary object
    end = time.time()
    summary["time_taken"] = end - start
    return summary

def _scrape_and_save_to_db_and_s3(listing_id,models):
    db = SessionLocal()
    # get listing
    listing = db.query(models.ListingsForScrapping).filter(models.ListingsForScrapping.id == listing_id).first()
    print('got listing')
    summary = {
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "images_uploaded": 0,
        "total_images": 0,
        "error_messages": []
    }
    try:
        scrapped_data = scrape_listing_data(listing.link)
        if scrapped_data == 'listing has expired':
            print(f'Listing {listing.link} has expired')
            listing.processed = 2
            db.commit()
            summary["total_processed"] += 1
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {listing.link}: listing has expired')
            db.close()
            return  summary
        if scrapped_data == 'request failed':
            print(f'Listing {listing.link} request failed, listing may have expired')
            listing.processed = 2
            db.commit()
            summary["total_processed"] += 1
            summary["failures"] += 1
            summary["error_messages"].append(f'Listing {listing.link}: listing has expired')
            db.close()
            return  summary
        # save scrapped data to scrappedlisting table
        db_listing = models.ScrappedListing(**scrapped_data)
        db.add(db_listing)
        # then update listing to processed
        listing.processed = 1
        db.commit() 
        print(f'Successfully scrapped {listing.link}')
        # upload images to s3
        image_links = json.loads(scrapped_data['image_links'])
        summary['total_images'] += len(image_links)
        #do this concurrently, 
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for index, image_link in enumerate(image_links):
                future = executor.submit(download_image_and_save_s3, image_link, scrapped_data['hash'], index)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                summary["images_uploaded"] += future.result()
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
    finally:
        db.close()
    return summary


def scrape_listings_and_save_results_concurrentV2(batch_size, models, db):
    start = time.time()
    # get listings to scrape where processed is not 1
    listings = db.query(models.ListingsForScrapping).filter(
        or_(models.ListingsForScrapping.processed.is_(None),models.ListingsForScrapping.processed == 0,)
    ).order_by(func.random()).limit(batch_size).all()
    print(f'Found {len(listings)} listings to scrape')
    #double check listings
    listings_to_scrape = [listing for listing in listings if not listing.processed]
    print(f'Removed {len(listings)-len(listings_to_scrape)} listings that were already processed')
    
    #summary for reply
    summary = {
        "total_processed": 0,
        "success": 0,
        "failures": 0,
        "images_uploaded": 0,
        "total_images": 0,
        "db_save_errors": 0,
        "error_messages": []
    }
    
    summary["total_processed"] = len(listings_to_scrape)
    #object that will save all scraped data
    scrapped_data = []

    #listings to set processed = 2 (not found)
    listings_failed = []

    #scrape all pages concurrently and return the data object for saving
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for listing in listings_to_scrape:
            future = executor.submit(_scrape_data, listing.link, listing.id)
            futures.append(future)

    for future in concurrent.futures.as_completed(futures):
        status, result, id = future.result()
        if status == ScrapeStatus.OK:
            scrapped_data.append((result, id))
        else:
            listings_failed.append((result, id))

    # save each scrapped listing to db
    BATCH_SIZE = 25
    batch_count = 0
    
    image_upload_tasks = []

    for listing in scrapped_data:
        try:
            data, id = listing
            db_listing = models.ScrappedListing(**data)
            db.add(db_listing)
            db.query(models.ListingsForScrapping).filter(models.ListingsForScrapping.id == id).update({"processed": 1})

            image_links = json.loads(data['image_links'])
            summary['total_images'] += len(image_links)

            # Queue up image upload tasks for this listing
            for index, image_link in enumerate(image_links):
                task = (download_image_and_save_s3, image_link, data['hash'], index)
                image_upload_tasks.append(task)

            summary["success"] += 1    

            batch_count += 1
            if batch_count >= BATCH_SIZE:
                # Process image uploads for the batch
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(*task) for task in image_upload_tasks]
                    for future in concurrent.futures.as_completed(futures):
                        summary["images_uploaded"] += future.result()

                # Clear the task list for the next batch
                image_upload_tasks.clear()

                # Commit DB changes for this batch
                db.commit()
                batch_count = 0

        except Exception as e:
            print('Error during saving:', e)
            db.rollback()
            db_save_errors += 1
            summary["error_messages"].append(f'Listing {id}: General Error - {e}')

    # Handle any remaining tasks and DB commit for the last batch
    if batch_count > 0 or image_upload_tasks:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(*task) for task in image_upload_tasks]
            for future in concurrent.futures.as_completed(futures):
                summary["images_uploaded"] += future.result()

        if batch_count > 0:
            db.commit()

    # figure out which ones to delete from the listings table
    for listing in listings_failed:
        result, id = listing
        print(f'handling failed listing for listing: {id}')
        db.query(models.ListingsForScrapping).filter(models.ListingsForScrapping.id == id).update({"processed": 2})        
        summary["failures"] += 1
    db.commit()

    print(f'listings failed: {len(listings_failed)}')
    print(f'listings scrapped: {len(scrapped_data)}')
    total_time = time.time() - start
    summary["time_taken"] = total_time
    return summary

def _scrape_data(link, id):
    scrapped_data = scrape_listing_data(link)
    status = ScrapeStatus.OK
    if isinstance(scrapped_data, ScrapeStatus):
        print(f'failed scraping for: {link}', scrapped_data)
        status = scrapped_data
        scrapped_data = link
    return status, scrapped_data, id
