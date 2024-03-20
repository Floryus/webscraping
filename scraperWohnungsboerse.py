import re
import csv
from urllib.request import urlopen


def run():
    # Open CSV file in write mode and create a CSV writer object with semicolon delimiter
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
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, delimiter=";", quotechar='"'
        )
        writer.writeheader()
        base_url = "https://www.wohnungsboerse.net/searches/index?estate_marketing_types=miete%2C1&marketing_type=miete&estate_types%5B0%5D=1&is_rendite=0&cities%5B0%5D=Berlin&term=Berlin&page={}"

        for page_number in range(1, 50):
            url = base_url.format(page_number)
            print("")
            print("🛜  Scraping page", page_number, ":", url)
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            # Define a regular expression pattern to match links to individual estate pages
            link_pattern = r"<a href=\"(.*?)\" title="

            # Find all matches using the pattern
            estate_links = re.findall(link_pattern, html)

            # Exclude other matches
            pattern = r"https://www\.wohnungsboerse\.net/immodetail/\d+"
            estate_links = re.findall(pattern, html)

            # If there are matches
            if estate_links:
                print("Number of estate links found:", len(estate_links))

            for estate_link in estate_links:
                estate_url = estate_link
                print("Scraping estate:", estate_url, end=" ")
                try:
                    estate_page = urlopen(estate_url)
                except:
                    print("❌")
                    continue
                estate_html_bytes = estate_page.read()
                estate_html = estate_html_bytes.decode("utf-8")

                # Define a regular expression pattern to match div elements with class "EstateItem"
                pattern = r"<section class=\"md:px-4 lg:container\">(.*?)</section>"

                # Find all matches using the pattern
                estate_items = re.findall(pattern, estate_html, re.DOTALL)

                estate_items = estate_items[1::3]

                # Loop through each matched element
                for estate in estate_items:
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

                    with open(
                        "boese.html", "a", newline="", encoding="utf-8-sig"
                    ) as file:
                        file.write(estate)

                    # Extracting attributes using regular expressions
                    title_match = re.search(
                        r'<h2 class="font-bold tracking-tight text-h4 lg:text-h3 mb-4 md:mb-8">(.*?)</h2>',
                        estate,
                    )

                    if title_match:
                        try:
                            estate_data["Title"] = title_match.group(1).strip()
                        except:
                            pass

                    area_match = re.search(
                        r'<dt>Fläche<\/dt>\s*<dd class="font-bold md:text-h3">\s*([\d.]+)\s*&nbsp;m²\s*<\/dd>',
                        estate,
                    )
                    if area_match:
                        try:
                            estate_data["Room Size (m²)"] = area_match.group(1)
                        except:
                            pass

                    room_match = re.search(
                        r'<dt>Zimmer<\/dt>\s*<dd class="font-bold md:text-h3">\s*([\d.]+)\s*<\/dd>',
                        estate,
                    )
                    if room_match:
                        try:
                            room_match = room_match.group(1)
                            estate_data["Number of Rooms"] = room_match
                        except:
                            pass

                    pattern = r'<div class="pl-4 md:pl-5 w-52">(.*?)</div>'
                    city_match = re.search(pattern, estate, re.DOTALL)
                    if city_match:
                        try:
                            city_match = city_match.group(1).strip()
                            city_match = re.sub(r"\s+", " ", city_match)
                            city_match = city_match.split("<br />")
                            estate_data["Location"] = city_match[1]
                        except:
                            pass

                    pricing_match = re.search(
                        r'<div class="grid-cols-12 p-4 md:grid bg-bg md:py-10 md:px-8">(.*?)</div>',
                        estate,
                        re.DOTALL,
                    )
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

                    level_match = re.search(
                        r'<td\s+class="text-fg-muted">Etage:</td>\s*<td>\s*(.*?)\s*</td>',
                        estate,
                        re.DOTALL,
                    )
                    if level_match:
                        try:
                            estate_data["Level"] = level_match.group(1)
                        except:
                            pass

                    movein_match = re.search(
                        r'<td\s+class="text-fg-muted">\s*Frei ab:\s*</td>\s*<td>\s*(.*?)\s*</td>',
                        estate,
                        re.DOTALL,
                    )
                    if movein_match:
                        try:
                            estate_data["Move-in Date"] = movein_match.group(1)
                        except:
                            pass

                    amenities_match = re.search(
                        r'<div class="p-4 mt-4 md:grid md:grid-cols-12 bg-bg md:py-10 md:px-8">\s*<div class="col-span-6">(.*?)</table>',
                        estate,
                        re.DOTALL,
                    )
                    if amenities_match:
                        try:
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

                    # Write the estate data to the CSV file
                    writer.writerow(estate_data)
                    print("✅")
