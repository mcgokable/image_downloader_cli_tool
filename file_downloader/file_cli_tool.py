import argparse

from dotenv import load_dotenv

from container import Container

load_dotenv()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from different resources")
    parser.add_argument(
        "-q", action="extend", nargs="+", required=True, help="query for API"
    )
    parser.add_argument("-n", help="number of images", default=1, type=int)
    parser.add_argument(
        "--save-to", type=str, required=True, help="folder for saving images"
    )
    parser.add_argument("--source", choices=["pixabay", "pexels"], required=True)
    args_dict = vars(parser.parse_args())

    container = Container()
    container.config.from_dict(args_dict)
    container.config.api_key.from_env(f"API_KEY_{args_dict['source'].upper()}")

    download_save_tool = container.download_save_tool()
    download_save_tool.run(args_dict["q"], args_dict["n"])

    print()
    print("Done")
