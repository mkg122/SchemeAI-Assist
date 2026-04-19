from app.scraper.scheme_scraper import fetch_schemes

def main():
    print("Fetching schemes from gov portal")

    schemes = fetch_schemes()

    print(f"Total schemes fetched: {len(schemes)}\n")

if __name__ == "__main__":
    main() 