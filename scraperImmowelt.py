import re
import csv
from urllib.request import urlopen


def run():
    # CSV file öffnen im Schreibmodus und ein CSV-Schreibobjekt mit Semikolon-Trennzeichen erstellen
    with open(
        "data/data-immowelt.csv", "w", newline="", encoding="utf-8-sig"
    ) as csvfile:
        fieldnames = [
            "Title",
            "Warm Price",
            "Cold Price",
            "Utilities Cost",
            "Deposit",
            "Room Size (m²)",
            "Number of Rooms",
            "Level",
            "Location",
            "Amenities",
            "Env",
            "Year of Construction",
            "Elevator",
            "Parking",
            "Kitchen",
            "Balcony",
            "Garden",
            "Terrace",
            "Move-in Date",
            "Efficiency Class",
            "Energy Source",
            "Energy Demand",
            "Link",
        ]
        # CSV-Header schreiben
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, delimiter=";", quotechar='"'
        )
        writer.writeheader()

        # Basis-URL für die Suche nach Mietwohnungen in Berlin
        base_url = "https://www.immowelt.de/suche/berlin/wohnungen/mieten?d=true&sd=DESC&sf=TIMESTAMP&sp={}"

        # Durch die ersten 100 Seiten der Suchergebnisse iterieren
        for page_number in range(1, 100):
            # URL für die aktuelle Seite erstellen
            url = base_url.format(page_number)
            print("")
            print("🛜  Scraping page", page_number, ":", url)
            # HTML-Seite herunterladen und dekodieren
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            # Regex Pattern für die Links zu den einzelnen Immobilien-Seiten
            link_pattern = r'<a\s+href="([^"]+)"\s+id="[^"]+"\s+class="[^"]+"\s+target="_self"\s+rel="noreferrer">'

            # Alle Links zu den Immobilien-Seiten finden
            estate_links = re.findall(link_pattern, html)

            # Durch jede Immobilien-Seite iterieren
            for estate_link in estate_links:
                estate_url = estate_link
                print("Scraping estate:", estate_url, end=" ")

                # HTML-Seite der Immobilie herunterladen und dekodieren
                try:
                    estate_page = urlopen(estate_url)
                except:
                    print("Failed to scrape estate:", estate_url)
                    continue
                estate_html_bytes = estate_page.read()
                estate_html = estate_html_bytes.decode("utf-8")

                # Regex Pattern für den Inhalt der Immobilien-Seite
                pattern = r"<app-objectmeta(.*?)Dieses Angebot melden"

                # Alle Elemente auf der Immobilien-Seite finden
                estate_items = re.findall(pattern, estate_html, re.DOTALL)

                # Durch alle Elemente auf der Immobilien-Seite iterieren
                for estate in estate_items:
                    # Datenstruktur für die Immobilie initialisieren
                    estate_data = {
                        "Title": "",
                        "Warm Price": "",
                        "Cold Price": "",
                        "Utilities Cost": "",
                        "Deposit": "",
                        "Room Size (m²)": "",
                        "Number of Rooms": "",
                        "Level": "",
                        "Location": "",
                        "Amenities": "",
                        "Env": "",
                        "Year of Construction": "",
                        "Move-in Date": "",
                        "Elevator": "Nicht verfügbar",
                        "Parking": "Nicht verfügbar",
                        "Kitchen": "Nicht verfügbar",
                        "Balcony": "Nicht verfügbar",
                        "Garden": "Nicht verfügbar",
                        "Terrace": "Nicht verfügbar",
                        "Efficiency Class": "",
                        "Energy Source": "",
                        "Energy Demand": "",
                        "Link": estate_url,
                    }

                    # Einzelne Datenpunkte aus dem Immobilien-Element extrahieren
                    title_match = re.search(
                        r"<h1 _ngcontent-sc210=\"\" class=\"ng-star-inserted\">(.*?)</h1>",
                        estate,
                    )

                    if title_match:
                        try:
                            estate_data["Title"] = title_match.group(1).strip()
                        except:
                            pass

                    area_match = re.search(
                        r"<span _ngcontent-sc203=\"\" class=\"has-font-300\">(.*?)Wohnfläche",
                        estate,
                    )
                    if area_match:
                        try:
                            area = area_match.group(1).strip()
                            room_size = re.search(r"\d+", area)
                            if room_size:
                                estate_data["Room Size (m²)"] = room_size.group(0)
                        except:
                            pass

                    room_match = re.search(
                        r"Wohnfläche(.*?)<span _ngcontent-sc203=\"\" class=\"has-font-300\">(.*?)Zimmer",
                        estate,
                    )
                    if room_match:
                        try:
                            room_match = room_match.group(2).strip()
                            estate_data["Number of Rooms"] = room_match[0]
                        except:
                            pass

                    city_match = re.search(
                        r"data-cy=\"address-city\"(.*?)</div></span><a _ngcontent-sc206=\"\" sdlink=\"\" alt=\"auf der Karte ansehen\"",
                        estate,
                    )
                    if city_match:
                        try:
                            city_match = city_match.group(1).strip()
                            postcode = re.search(r"sc206=\"\">(.*?)&nbsp", city_match)
                            district = re.search(r"\((.*?)\)", city_match)
                            estate_data["Location"] = (
                                postcode.group(1) + " " + district.group(1)
                            )
                        except:
                            pass

                    pricing_match = re.search(
                        r"Preise &amp; Kosten</h2>(.*?)<h2>Lage</h2>", estate
                    )

                    if pricing_match:
                        try:
                            text_matches = re.findall(
                                r">([^<]+)<", pricing_match.group(1)
                            )

                            extracted_text = []
                            for match in text_matches:
                                extracted_text.append(match.strip())

                            for value in extracted_text:
                                if value == "Kaltmiete":
                                    raw_price = extracted_text[
                                        extracted_text.index(value) + 1
                                    ]
                                    cold_price = re.sub(
                                        r"[^\d.,]", "", raw_price
                                    )  # only numbers, periods, and commas
                                    estate_data["Cold Price"] = cold_price
                                if value == "Warmmiete":
                                    raw_price = extracted_text[
                                        extracted_text.index(value) + 1
                                    ]
                                    warm_price = re.sub(
                                        r"[^\d.,]", "", raw_price
                                    )  #  only numbers, periods, and commas
                                    estate_data["Warm Price"] = warm_price
                                if value == "Nebenkosten":
                                    raw_cost = extracted_text[
                                        extracted_text.index(value) + 1
                                    ]
                                    utilities_cost = re.sub(
                                        r"[^\d.,]", "", raw_cost
                                    )  # only numbers, periods, and commas
                                    estate_data["Utilities Cost"] = utilities_cost
                                if value == "Kaution":
                                    raw_deposit = extracted_text[
                                        extracted_text.index(value) + 1
                                    ]
                                    estate_data["Deposit"] = raw_deposit
                        except:
                            pass

                    level_match = re.search(
                        '>Wohnungslage</p><p _ngcontent-sc224="">(.*?)</p></sd-cell-col></sd-cell-row></sd-cell>',
                        estate,
                    )
                    if level_match:
                        try:
                            estate_data["Level"] = level_match.group(1).strip()
                        except:
                            pass

                    movein_match = re.search(
                        '>Bezug</p><p _ngcontent-sc224="">(.*?)</p></sd-cell-col></sd-cell-row></sd-cell>',
                        estate,
                    )
                    if movein_match:
                        try:
                            estate_data["Move-in Date"] = movein_match.group(1).strip()
                        except:
                            pass

                    amenities_match = re.search(
                        '<ul _ngcontent-sc224="">(.*?)</ul>', estate
                    )
                    if amenities_match:
                        try:
                            text_matches = re.findall(
                                r">([^<]+)<", amenities_match.group(1)
                            )
                            amenities = []
                            for match in text_matches:
                                if "balkon" in match.lower():
                                    estate_data["Balcony"] = "Verfügbar"
                                elif "garten" in match.lower():
                                    estate_data["Garden"] = "Verfügbar"
                                elif "terrasse" in match.lower():
                                    estate_data["Terrace"] = "Verfügbar"
                                elif "einbauküche" in match.lower():
                                    estate_data["Kitchen"] = "Verfügbar"
                                elif ":" in match:
                                    break
                                else:
                                    amenities.append(match.strip())
                            estate_data["Amenities"] = ", ".join(amenities)
                        except:
                            pass

                    env_match = re.search(
                        ">Wohnanlage(.*?)</ul>",
                        estate,
                    )
                    if env_match:
                        try:
                            text_matches = re.findall(r">([^<]+)<", env_match.group(1))
                            env = []
                            baujahr_found = False
                            for match in text_matches:
                                if baujahr_found:
                                    estate_data["Year of Construction"] = match.strip()
                                    baujahr_found = False
                                elif match == "Baujahr: ":
                                    baujahr_found = True
                                elif (
                                    "stellplatz" in match.lower()
                                    or "garage" in match.lower()
                                ):
                                    estate_data["Parking"] = "Verfügbar"
                                elif "aufzug" in match.lower():
                                    estate_data["Elevator"] = "Verfügbar"
                                else:
                                    env.append(match.strip())

                            estate_data["Env"] = ", ".join(env)
                        except:
                            pass

                    energy_match = re.search(
                        ">Energie &amp; Heizung</h2>(.*?)<app-electricity-calculator",
                        estate,
                    )
                    if energy_match:
                        try:
                            text_matches = re.findall(
                                r">([^<]+)<", energy_match.group(1)
                            )
                            for index, match in enumerate(text_matches):
                                if "effizienzklasse" in match.lower():
                                    estate_data["Efficiency Class"] = text_matches[
                                        index + 1
                                    ]
                                elif "wesentliche energieträger" in match.lower():
                                    estate_data["Energy Source"] = text_matches[
                                        index + 1
                                    ]
                                elif "endenergiebedarf" in match.lower():
                                    numerical = re.search(
                                        r"\d+.\d+", text_matches[index + 1]
                                    )
                                    estate_data["Energy Demand"] = numerical.group(0)
                        except:
                            pass

                    # Alle Daten in CSV-Datei schreiben
                    writer.writerow(estate_data)
                    print("✅")
