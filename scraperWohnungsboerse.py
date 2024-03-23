import re
import csv
from urllib.request import urlopen


def run():
    # CSV file öffnen im Schreibmodus und ein CSV-Schreibobjekt mit Semikolon-Trennzeichen erstellen
    with open(
        "data/data-wohnungsboerse.csv", "w", newline="", encoding="utf-8-sig"
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
        base_url = "https://www.wohnungsboerse.net/searches/index?estate_marketing_types=miete%2C1&marketing_type=miete&estate_types%5B0%5D=1&is_rendite=0&cities%5B0%5D=Berlin&term=Berlin&page={}"

        # Durch die ersten 50 Seiten der Suchergebnisse iterieren
        for page_number in range(1, 50):
            # URL für die aktuelle Seite erstellen
            url = base_url.format(page_number)
            print("")
            print("🛜  Scraping page", page_number, ":", url)
            # HTML-Seite herunterladen und dekodieren
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            # Regex Pattern für die Links zu den einzelnen Immobilien-Seiten
            link_pattern = r"<a href=\"(.*?)\" title="

            # Alle Links zu den Immobilien-Seiten finden
            estate_links = re.findall(link_pattern, html)

            # Andere Regex Pattern ignorieren, welche nicht zu den Immobilien-Seiten führen
            pattern = r"https://www\.wohnungsboerse\.net/immodetail/\d+"
            estate_links = re.findall(pattern, html)

            # Anzahl der gefundenen Immobilien-Links pro Übersicht ausgeben
            if estate_links:
                print("Number of estate links found:", len(estate_links))

            # Durch jede Immobilien-Seite iterieren
            for estate_link in estate_links:
                estate_url = estate_link
                print("Scraping estate:", estate_url, end=" ")

                # HTML-Seite der Immobilie herunterladen und dekodieren
                try:
                    estate_page = urlopen(estate_url)
                except:
                    print("❌")
                    continue
                estate_html_bytes = estate_page.read()
                estate_html = estate_html_bytes.decode("utf-8")

                # Regex Pattern für den Inhalt der Immobilien-Seite
                pattern = r"<section class=\"md:px-4 lg:container\">(.*?)</section>"

                # Alle Elemente auf der Immobilien-Seite finden
                estate_items = re.findall(pattern, estate_html, re.DOTALL)
                estate_items = estate_items[1::3]

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
                    # Titel extrahieren
                    title_match = re.search(
                        r'<h2 class="font-bold tracking-tight text-h4 lg:text-h3 mb-4 md:mb-8">(.*?)</h2>',
                        estate,
                    )
                    # Titel in Datenstruktur speichern
                    if title_match:
                        try:
                            estate_data["Title"] = title_match.group(1).strip()
                        except:
                            pass

                    # Fläche extrahieren
                    area_match = re.search(
                        r'<dt>Fläche<\/dt>\s*<dd class="font-bold md:text-h3">\s*([\d.]+)\s*&nbsp;m²\s*<\/dd>',
                        estate,
                    )
                    # Fläche in Datenstruktur speichern
                    if area_match:
                        try:
                            estate_data["Room Size (m²)"] = area_match.group(1)
                        except:
                            pass

                    # Anzahl der Zimmer extrahieren
                    room_match = re.search(
                        r'<dt>Zimmer<\/dt>\s*<dd class="font-bold md:text-h3">\s*([\d.]+)\s*<\/dd>',
                        estate,
                    )
                    # Anzahl der Zimmer in Datenstruktur speichern
                    if room_match:
                        try:
                            room_match = room_match.group(1)
                            estate_data["Number of Rooms"] = room_match
                        except:
                            pass

                    # Stadtteil extrahieren
                    pattern = r'<div class="pl-4 md:pl-5 w-52">(.*?)</div>'
                    city_match = re.search(pattern, estate, re.DOTALL)
                    # Stadtteil in Datenstruktur speichern
                    if city_match:
                        try:
                            city_match = city_match.group(1).strip()
                            city_match = re.sub(r"\s+", " ", city_match)
                            city_match = city_match.split("<br />")
                            estate_data["Location"] = city_match[1]
                        except:
                            pass

                    # Preisdaten extrahieren
                    pricing_match = re.search(
                        r'<div class="grid-cols-12 p-4 md:grid bg-bg md:py-10 md:px-8">(.*?)</div>',
                        estate,
                        re.DOTALL,
                    )
                    # Preisdaten in Datenstruktur speichern
                    if pricing_match:
                        try:
                            pricing_match = re.sub(r"\s+", " ", pricing_match.group(1))
                            cold_price = re.search(
                                r"Kaltmiete: </td> <td> (.*?)&nbsp;",
                                pricing_match,
                                re.DOTALL,
                            )
                            cold_price = re.sub(r"\.", "", cold_price.group(1))
                            estate_data["Cold Price"] = cold_price

                            warm_price = re.search(
                                r'Gesamtmiete:</td> <td class="font-bold text-green-emphasis"> (.*?)&nbsp;',
                                pricing_match,
                                re.DOTALL,
                            )
                            warm_price = re.sub(r"\.", "", warm_price.group(1))
                            estate_data["Warm Price"] = warm_price

                            utilities_cost = re.search(
                                r"Nebenkosten: </td> <td> (.*?)&nbsp;",
                                pricing_match,
                                re.DOTALL,
                            )
                            utilities_cost = re.sub(r"\.", "", utilities_cost.group(1))
                            estate_data["Utilities Cost"] = utilities_cost

                            deposit = re.search(
                                r"Kaution:</td> <td> (.*?)&nbsp;",
                                pricing_match,
                                re.DOTALL,
                            )
                            deposit = re.sub(r"\.", "", deposit.group(1))
                            estate_data["Deposit"] = deposit

                        except:
                            pass

                    # Etagendaten extrahieren
                    level_match = re.search(
                        r'<td\s+class="text-fg-muted">Etage:</td>\s*<td>\s*(.*?)\s*</td>',
                        estate,
                        re.DOTALL,
                    )
                    # Etagendaten in Datenstruktur speichern
                    if level_match:
                        try:
                            estate_data["Level"] = level_match.group(1)
                        except:
                            pass

                    # Einzugsdaten extrahieren
                    movein_match = re.search(
                        r'<td\s+class="text-fg-muted">\s*Frei ab:\s*</td>\s*<td>\s*(.*?)\s*</td>',
                        estate,
                        re.DOTALL,
                    )
                    # Einzugsdaten in Datenstruktur speichern
                    if movein_match:
                        try:
                            estate_data["Move-in Date"] = movein_match.group(1)
                        except:
                            pass

                    # Weitere Informationen sammeln
                    amenities_match = re.search(
                        r'<div class="p-4 mt-4 md:grid md:grid-cols-12 bg-bg md:py-10 md:px-8">\s*<div class="col-span-6">(.*?)</table>',
                        estate,
                        re.DOTALL,
                    )
                    # Weitere Informationen in Datenstruktur speichern
                    if amenities_match:
                        try:
                            # Auf erhobene Werte prüfen
                            amenities_match = re.sub(
                                r"\s+", " ", amenities_match.group(1)
                            )
                            key_amenities = re.findall(
                                r'<div class="before:icon-check_circle before:text-green before:text-base before:relative before:top-0.5 before:mr-1"> (.*?) </div>',
                                amenities_match,
                                re.DOTALL,
                            )
                            amenities = []
                            for match in key_amenities:
                                if "balkon" in match.lower():
                                    estate_data["Balcony"] = "Verfügbar"
                                elif "garten" in match.lower():
                                    estate_data["Garden"] = "Verfügbar"
                                elif "terrasse" in match.lower():
                                    estate_data["Terrace"] = "Verfügbar"
                                elif (
                                    "einbauküche" in match.lower()
                                    or "ebk" in match.lower()
                                ):
                                    estate_data["Kitchen"] = "Verfügbar"
                                else:
                                    amenities.append(match.strip())

                            side_amenities = re.findall(
                                r"<td>(.*?)</td>", amenities_match, re.DOTALL
                            )
                            for match in side_amenities:
                                if re.match(
                                    r"\d+", match
                                ):  # Check if match contains digits within <div> tags
                                    estate_data["Year of Construction"] = match
                                elif any(
                                    keyword in match.lower()
                                    for keyword in [
                                        "zentralheizung",
                                        "fernwärme",
                                        "gas",
                                        "öl",
                                        "holz",
                                        "wärmepumpe",
                                        "blockheizkraftwerk",
                                    ]
                                ):
                                    estate_data["Energy Source"] = match
                                elif re.match(
                                    r"^.{1}$", match.strip()
                                ):  # Check if match is exactly one character
                                    estate_data["Efficiency Class"] = match
                                else:
                                    amenities.append(match.strip())

                            estate_data["Amenities"] = ", ".join(amenities)
                        except:
                            pass

                    # Alle Daten in CSV-Datei schreiben
                    writer.writerow(estate_data)
                    print("✅")
