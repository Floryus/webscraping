import scraperImmowelt
import scraperWohnungsboerse


if __name__ == "__main__":

    print("📡 Scraping Immowelt...")
    scraperImmowelt.run()

    print("")
    print("📡 Scraping Wohnungsboerse...")
    scraperWohnungsboerse.run()
    print("")
    print("✅ Both scrapers have finished.")
    print("💾 The data has been saved to the data folder.")
