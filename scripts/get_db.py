import requests
import time
import gc

import pandas as pd

from bs4 import BeautifulSoup
from scripts import preprocessing


def get_behemoth():
    """
    Loads the initial large request necessary to rebuilt the database logic
    """
    t_zero = time.perf_counter()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    }

    behemoth = """https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&ants=\
    &nwas=&falls=&valids=&stype=contains&lrec=100000&map=ge&browse=&country=\
    All&srt=name&categ=All&mblist=All&rect=\
    &phot=&strewn=&snew=0&pnt=Normal%20table&dr=&page=1"""

    r = requests.get(url=behemoth, headers=headers,)

    body_tag, html_tag = check_closing_tags_bytes(r.content)

    if body_tag and html_tag:
        print("HTML document complete")
    else:
        t_end = time.perf_counter()
        raise RuntimeError(f"The request appears to have failed, exiting after {round(t_end - t_zero, 4)}")

    soup = BeautifulSoup(r.content, "html.parser")

    t_end = time.perf_counter()

    print(f"request time : {round(t_end - t_zero, 4)}")

    return soup


def check_closing_tags_bytes(html_bytes: bytes) -> tuple:
    """
    Check the last bytes of the HTML content for </body> and </html> tags.
    This function is to be launched on the request.content bytes object.

    Args:
        html_bytes (bytes): The HTML content as a bytes object.

    Returns:
        tuple: A tuple containing two booleans indicating the presence of </body> and </html> tags.
    """

    tail_content = html_bytes[-100:].decode("utf-8", errors="ignore").lower()

    closing_body_tag = "</body>" in tail_content
    closing_html_tag = "</html>" in tail_content

    return closing_body_tag, closing_html_tag


def make_dataframe(soup) -> pd.DataFrame:
    """
    Collects the main_table from the soup object, where the informations are.
    Uses loop to find all the meteorites and associated attributes.
    Creates a dataframe containing these informations and returns it.
    """

    main_table = soup.find("table", id="maintable")
    gc.collect()

    base_url = "https://www.lpi.usra.edu/meteor/metbull.php?"
    meteorite_data = []

    for row in main_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) > 8:  # Ensuring there are enough cells
            anchor = cells[0].find("a")
            if anchor and "href" in anchor.attrs:
                href = anchor["href"]
                code_start = href.find("code=") + len("code=")
                met_code = href[code_start:].split("&")[0] if "&" in href[code_start:] else href[code_start:]
                met_url = f"{base_url}code={met_code}"
            else:
                met_url = None

            # Extracting the required fields
            name = preprocessing.handle_name(cells[0].text.strip())
            year = preprocessing.handle_year(cells[4].text.strip())
            country = preprocessing.handle_country(cells[5].text.strip())
            met_type = preprocessing.handle_types(cells[6].text.strip())
            mass = preprocessing.handle_mass(cells[7].text.strip())

            # Append this meteorite"s info as a dict
            meteorite_data.append({
                "name": name,
                "year": year,
                "country": country,
                "type": met_type,
                "mass": mass,
                "URL": met_url
            })

    # Convert the list of dicts to a pandas DataFrame
    met_bull_df = pd.DataFrame(meteorite_data)

    return met_bull_df


def df_handler(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple handling of types and NAs logic
    """
    # handling NA years :
    df["year"] = df["year"].astype("Int64")
    df["year"] = df["year"].fillna(pd.NA)
    # handling NA types
    df["type"] = df["type"].replace("Unknown", pd.NA)
    # handling NA countries
    df["country"] = df["country"].replace("Unknown", pd.NA)

    return df


def get_metbull_data(saving_path: str, give_df: bool = True) -> None | pd.DataFrame:
    """
    Function :
        - The main function to fetch the data from the metbull site

    Attrs:
        - saving_path : str, non optional : the/path/to/savefile
        - give_df : bool, optionnal, default = True, whether or not to return the data as a pd.DataFrame

    Returns:
        - None if give_df = False
        - df : pd.DataFrame containing the meteorite data
    """
    if not saving_path:
        raise ValueError("Please provide a valid path to save the files.")

    soup = get_behemoth()
    df = make_dataframe(soup=soup)
    df = df_handler(df=df)

    df.to_json(f"{saving_path}/metbull_data.json", orient="records", lines=True)
    df.to_pickle(f"{saving_path}/metbull_data.pkl")

    if give_df:
        return df
