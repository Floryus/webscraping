import scraperImmowelt
import scraperWohnungsboerse

# Diese Datei ausführen, um die beiden Scraper zu starten
if __name__ == "__main__":

    # Immowelt scraper starten
    print("📡 Scraping Immowelt...")
    scraperImmowelt.run()
    print("")

    # Wohnungsboerse scraper starten
    print("📡 Scraping Wohnungsboerse...")
    scraperWohnungsboerse.run()
    print("")

    # Ergebnisse anzeigen
    print("✅ Both scrapers have finished.")
    print("💾 The data has been saved to the data folder.")
