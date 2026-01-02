import requests
import argparse
import dateparser
import datetime
import logging
import os
import re
from bs4 import BeautifulSoup
import rename_fooni_files as rff


# some config
# media_url = "https://media.fööni.fi"
media_url = "https://media.xn--fni-snaa.fi"
proflyer_url = media_url + "/proflyer_login"
debug = False
pbar = None

# TODO: add progressbar


def sort_dicts_by_session(dict_list: list[dict]) -> list[dict]:
    """Sort list of dicts by 'session' datetime, oldest first."""
    return sorted(dict_list, key=lambda d: d["session_time"])


def proflyer_request(cookie):
    # Grab proflyer
    logging.debug("Trying to grab proflyer page")
    try:
        response = requests.get(proflyer_url, headers={"Cookie": cookie})
        return response
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(f"Error on requesting {proflyer_url}")
        raise SystemExit(e)


def set_filter(url, cookie):
    logging.debug(f"Trying to set filter over url {media_url}/{url}")
    try:
        response = requests.get(media_url + "/" + url, headers={"Cookie": cookie})
        return response
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_video_urls_from_session(session, cookie, perspective):
    logging.info(f"\nGetting videos from session {session['session_time']}")
    response = set_filter(session["filter_url"], cookie)

    logging.info("Parsing HTML Response")
    soup = BeautifulSoup(response.text, "html.parser")
    preview_containers = soup.select_one(
        "#main > div > div:nth-child(2) > div"  # "#main > div > div:nth-child(2) > div"
    ).find_all("div", class_="media_container_responsive", recursive=False)
    urls = {}

    for container in preview_containers:
        link = container.find("a", class_="btn btn-link download_link")
        media_select = container.find("input", class_="media-select")
        filename = media_select.get("data-filename")
        new_name = rff.make_new_filename(
            filename=filename, session_time=session["session_time"].strftime("%H_%M")
        )

        perspective_in_new_name = [
            True for p in perspective.lower().split(" ") if p in new_name
        ]

        if link is not None and (
            (True in perspective_in_new_name) or (perspective is None)
        ):
            urls[new_name] = link["href"]

    return urls


def download_sessions(sessions):
    if not os.path.isdir("media"):
        os.mkdir("media")

    for session in sessions:
        date_path = os.path.join("media", session["session_time"].strftime("%Y-%m-%d"))
        session_path = os.path.join(
            date_path, session["session_time"].strftime("%H_%M")
        )
        logging.info(
            f'\n\n****** Downloading {len(session["video_urls"])} videos from session {session["session_time"]} to {session_path} ****** '
        )

        # create necessary paths
        if not os.path.isdir(date_path):
            os.mkdir(date_path)

        if not os.path.isdir(session_path):
            os.mkdir(session_path)

        for file_name, url in session["video_urls"].items():
            logging.info(f"- {file_name}")
            v = os.path.join(session_path, file_name)

            if not os.path.exists(v):
                try:
                    response = requests.get(url)
                    with open(v, "wb") as video:
                        video.write(response.content)
                    logging.info(f"  success!")
                except Exception as e:
                    logging.error(f"  ERROR: {e}")
            else:
                logging.info(f"  exists")


def main():
    # Debug on
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    # some config and cli sugar
    parser = argparse.ArgumentParser(description="Download Fööni Videos.")
    parser.add_argument("cookie_file")
    parser.add_argument(
        "--perspective",
        help="Set perspective(s) for downloading (bottom sideline side top centerline center).\
        Defaults to all perspectives.\
        When passing multiple perspectives, separate with space",
    )
    parser.add_argument(
        "--start", help="Set start date for downloading. Defaults: today-30days"
    )
    parser.add_argument(
        "--oneday",
        help="Download videos for start_date only. (y) Defaults: None",
    )
    args = parser.parse_args()

    if args.start is None:
        start_date = datetime.date.today() - datetime.timedelta(days=30)
        start_date = dateparser.parse(str(start_date))
        end = "to today"
    else:
        start_date = dateparser.parse(args.start)
        if args.oneday is not None:
            end = f"to {start_date + datetime.timedelta(days=1)}"
        else:
            end = "to today"

        if start_date is None:
            raise SystemExit("Start date could not be parsed.")
        # start_date -= datetime.timedelta(days=1)

    logging.info(f"\nWill fetch valid sessions from {start_date} {end}")

    # load cookie file
    with open(args.cookie_file) as f:
        cookie = f.read()

    r = proflyer_request(cookie)

    # grab all available sessions
    valid_sessions = []
    soup = BeautifulSoup(r.text, "html.parser")

    # assuming that finding the first dropdown should be sufficient.
    dropdown = soup.find("ul", attrs={"class": "dropdown-menu"})
    items = dropdown.find_all("li")

    for item in items:
        session_time = dateparser.parse(item.text)
        filter_link = item.find("a")

        if args.oneday is None:  # download all sessions after start_date
            condition = session_time.date() >= start_date.date()
        else:  # download sessions of start_date
            condition = session_time.date() == start_date.date()
        if condition:
            valid_sessions.append(
                {
                    "filter_url": filter_link["href"],
                    "session_time": session_time,
                    "video_urls": [],
                }
            )

    logging.info(f"Found {len(valid_sessions)} valid sessions")

    valid_sessions = sort_dicts_by_session(valid_sessions)

    for session in valid_sessions:
        session["video_urls"] = get_video_urls_from_session(
            session, cookie, args.perspective
        )
        logging.info(f"Fetched {len(session['video_urls'])} video urls")

    download_sessions(valid_sessions)


if __name__ == "__main__":
    main()
